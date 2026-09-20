import json

from services.llm import invoke_llm
from graph.state import ProjectState


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
        for req in state.get("requirements", [])
    )

    # ========================================================
    # ARCHITECT PROMPT
    # ========================================================

    prompt = f"""
You are the Software Architect Agent in an autonomous
software development team.

Your job is to design the technical architecture based
ONLY on the actual software request and requirements.

USER SOFTWARE REQUEST:
{user_request}

PROJECT REQUIREMENTS:
{requirements}

Determine the appropriate project type.

IMPORTANT:
Do NOT assume that every project is a full-stack web application.

The project_type must accurately describe the requested
software.

Possible examples include:

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

For example:

If the request is:
"Create a simple Python calculator application"

then the architecture should be something similar to:

"project_type": "Python CLI application"

and the frontend/backend/database sections should NOT
invent unnecessary technologies.

If a database is not required, use an empty technology
and an empty collections_or_tables list.

If authentication is not required, use an empty string.

If an API is not required, use an empty string.

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
2. Do not add technologies that are not needed.
3. Do not invent a frontend for CLI or backend-only projects.
4. Do not invent a database when one is unnecessary.
5. Do not invent authentication when it is unnecessary.
6. Do not invent an API when it is unnecessary.
7. Keep folder_structure realistic for the project.
8. Return valid JSON only.
9. Do not include markdown.
10. Do not use ```json.
11. Do not add explanations outside the JSON.
"""

    # ========================================================
    # CALL LLM
    # ========================================================

    response = invoke_llm(prompt)

    # ========================================================
    # EXTRACT RESPONSE
    # ========================================================

    if isinstance(response.content, list):

        architecture_text = "\n".join(
            str(block.get("text", block))
            if isinstance(block, dict)
            else str(block)
            for block in response.content
        )

    else:

        architecture_text = str(
            response.content
        )

    architecture_text = architecture_text.strip()

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
    # REMOVE MARKDOWN CODE FENCES
    # ========================================================

    if architecture_text.startswith("```json"):

        architecture_text = architecture_text[
            len("```json"):
        ].strip()

    elif architecture_text.startswith("```"):

        architecture_text = architecture_text[
            len("```"):
        ].strip()

    if architecture_text.endswith("```"):

        architecture_text = architecture_text[
            :-len("```")
        ].strip()

    # ========================================================
    # PARSE JSON
    # ========================================================

    try:

        architecture = json.loads(
            architecture_text
        )

    except json.JSONDecodeError as error:

        print(
            "⚠️ Architect JSON parsing failed:"
        )

        print(
            error
        )

        architecture = {
            "project_type": "unknown",
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
            "folder_structure": [],
            "raw": architecture_text
        }

    # ========================================================
    # VALIDATE PROJECT TYPE
    # ========================================================

    if not architecture.get("project_type"):

        architecture["project_type"] = "other"

    # ========================================================
    # RETURN UPDATED STATE
    # ========================================================

    return {
        **state,
        "architecture": architecture
    }