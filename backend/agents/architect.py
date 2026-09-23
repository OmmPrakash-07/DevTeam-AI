import json
import re

from services.llm import invoke_llm
from graph.state import ProjectState


def extract_text_from_response(response) -> str:
    """
    Extract plain text from different LLM response formats.
    Supports:
    - string
    - list of content blocks
    - dict content blocks
    """

    content = getattr(response, "content", response)

    if isinstance(content, str):
        return content.strip()

    if isinstance(content, list):
        parts = []

        for block in content:
            if isinstance(block, dict):
                text = block.get("text")

                if text:
                    parts.append(str(text))

            else:
                parts.append(str(block))

        return "\n".join(parts).strip()

    if isinstance(content, dict):
        if "text" in content:
            return str(content["text"]).strip()

        return json.dumps(content)

    return str(content).strip()


def extract_json_object(text: str) -> str:
    """
    Extract the first valid JSON object from an LLM response.

    Handles:
    - ```json ... ```
    - ``` ... ```
    - explanatory text before JSON
    - explanatory text after JSON
    """

    text = text.strip()

    # Remove markdown code fences.
    text = re.sub(
        r"^```(?:json)?\s*",
        "",
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(
        r"\s*```$",
        "",
        text
    )

    text = text.strip()

    # First try the complete response directly.
    try:
        json.loads(text)
        return text
    except json.JSONDecodeError:
        pass

    # Find the first JSON object.
    start = text.find("{")

    if start == -1:
        raise ValueError(
            "No JSON object found in architect response."
        )

    # Use JSONDecoder.raw_decode() so trailing text is allowed.
    decoder = json.JSONDecoder()

    try:
        _, end = decoder.raw_decode(text[start:])
        return text[start:start + end]

    except json.JSONDecodeError:
        pass

    # Last-resort balanced-brace extraction.
    depth = 0
    in_string = False
    escaped = False

    for index in range(start, len(text)):

        char = text[index]

        if escaped:
            escaped = False
            continue

        if char == "\\" and in_string:
            escaped = True
            continue

        if char == '"':
            in_string = not in_string
            continue

        if in_string:
            continue

        if char == "{":
            depth += 1

        elif char == "}":
            depth -= 1

            if depth == 0:
                candidate = text[start:index + 1]

                try:
                    json.loads(candidate)
                    return candidate
                except json.JSONDecodeError:
                    break

    raise ValueError(
        "Unable to extract valid JSON from architect response."
    )


def normalize_architecture(architecture: dict) -> dict:
    """
    Ensure the architecture object always has the expected structure.
    """

    if not isinstance(architecture, dict):
        architecture = {}

    frontend = architecture.get("frontend", {})
    backend = architecture.get("backend", {})
    database = architecture.get("database", {})

    if not isinstance(frontend, dict):
        frontend = {}

    if not isinstance(backend, dict):
        backend = {}

    if not isinstance(database, dict):
        database = {}

    responsibilities = lambda value: (
        value if isinstance(value, list) else []
    )

    folder_structure = architecture.get(
        "folder_structure",
        []
    )

    if not isinstance(folder_structure, list):
        folder_structure = []

    return {
        "project_type": str(
            architecture.get(
                "project_type",
                "other"
            ) or "other"
        ),

        "frontend": {
            "technology": str(
                frontend.get(
                    "technology",
                    ""
                ) or ""
            ),
            "responsibilities": responsibilities(
                frontend.get(
                    "responsibilities",
                    []
                )
            )
        },

        "backend": {
            "technology": str(
                backend.get(
                    "technology",
                    ""
                ) or ""
            ),
            "responsibilities": responsibilities(
                backend.get(
                    "responsibilities",
                    []
                )
            )
        },

        "database": {
            "technology": str(
                database.get(
                    "technology",
                    ""
                ) or ""
            ),
            "collections_or_tables": responsibilities(
                database.get(
                    "collections_or_tables",
                    []
                )
            )
        },

        "authentication": str(
            architecture.get(
                "authentication",
                ""
            ) or ""
        ),

        "api_style": str(
            architecture.get(
                "api_style",
                ""
            ) or ""
        ),

        "folder_structure": [
            str(item)
            for item in folder_structure
            if item
        ]
    }


def architect_agent(state: ProjectState) -> ProjectState:

    # ========================================================
    # INPUT DATA
    # ========================================================

    user_request = state.get(
        "user_request",
        ""
    )

    requirements = "\n".join(
        f"- {req}"
        for req in state.get(
            "requirements",
            []
        )
    )

    # ========================================================
    # ARCHITECT PROMPT
    # ========================================================

    prompt = f"""
You are the Software Architect Agent in an autonomous
software development team.

Design the technical architecture based ONLY on the
actual software request and requirements.

USER SOFTWARE REQUEST:
{user_request}

PROJECT REQUIREMENTS:
{requirements}

Determine the appropriate project type.

IMPORTANT:
Do NOT assume every project is a full-stack web application.

The project_type must accurately describe the requested
software.

Possible examples:

- Python CLI application
- Python desktop application
- Python automation script
- Python backend/API
- Full-stack web application
- Frontend web application
- REST API
- Mobile application
- Java desktop application
- Java backend application
- Data analysis application
- Machine learning application
- Other appropriate type

Choose the technology stack according to the actual request.

If the request is a simple Python calculator, for example:

"project_type": "Python CLI application"

Do NOT invent unnecessary frontend, database,
authentication, or API technologies.

If a database is not required:

"technology": ""
"collections_or_tables": []

If authentication is not required:

"authentication": ""

If an API is not required:

"api_style": ""

Return ONLY valid JSON.

Use exactly this structure:

{{
    "project_type": "",
    "frontend": {{
        "technology": "",
        "responsibilities": []
    }},
    "backend": {{
        "technology": "",
        "responsibilities": []
    }},
    "database": {{
        "technology": "",
        "collections_or_tables": []
    }},
    "authentication": "",
    "api_style": "",
    "folder_structure": []
}}

Rules:

1. project_type must match the actual request.
2. Do not add unnecessary technologies.
3. Do not invent a frontend for CLI or backend-only projects.
4. Do not invent a database when unnecessary.
5. Do not invent authentication when unnecessary.
6. Do not invent an API when unnecessary.
7. Keep folder_structure realistic.
8. Return valid JSON only.
9. Do not use markdown.
10. Do not use ```json.
11. Do not add explanations outside the JSON.
"""

    # ========================================================
    # CALL LLM
    # ========================================================

    response = invoke_llm(
    prompt,
    max_tokens=1500
    )

    # ========================================================
    # EXTRACT RESPONSE TEXT
    # ========================================================

    architecture_text = extract_text_from_response(
        response
    )

    print(
        "\n========== ARCHITECT OUTPUT =========="
    )

    print(
        architecture_text
    )

    print(
        "======================================\n"
    )

    # ========================================================
    # EXTRACT + PARSE JSON
    # ========================================================

    try:

        json_text = extract_json_object(
            architecture_text
        )

        architecture = json.loads(
            json_text
        )

        architecture = normalize_architecture(
            architecture
        )

        print(
            "✅ Architect JSON parsed successfully."
        )

    except Exception as error:

        print(
            "⚠️ Architect JSON parsing failed:"
        )

        print(
            error
        )

        # Safe fallback architecture.
        architecture = {
            "project_type": "other",
            "frontend": {
                "technology": "",
                "responsibilities": []
            },
            "backend": {
                "technology": "",
                "responsibilities": []
            },
            "database": {
                "technology": "",
                "collections_or_tables": []
            },
            "authentication": "",
            "api_style": "",
            "folder_structure": []
        }

    # ========================================================
    # VALIDATE PROJECT TYPE
    # ========================================================

    if not architecture.get(
        "project_type"
    ):

        architecture["project_type"] = "other"

    # ========================================================
    # RETURN UPDATED STATE
    # ========================================================

    return {
        **state,
        "architecture": architecture
    }