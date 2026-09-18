import json

from services.llm import get_llm
from graph.state import ProjectState


def developer_agent(state: ProjectState) -> ProjectState:

    llm = get_llm()

    requirements = "\n".join(
        f"- {req}"
        for req in state.get("requirements", [])
    )

    architecture = json.dumps(
        state.get("architecture", {}),
        indent=2
    )

    prompt = f"""
You are the Developer Agent in an autonomous
software development team.

PROJECT REQUIREMENTS:
{requirements}

TECHNICAL ARCHITECTURE:
{architecture}

Your task is to design the initial source files
for this project.

Return ONLY valid JSON using exactly this structure:

{{
    "files": [
        {{
            "path": "frontend/src/App.jsx",
            "content": "file content here"
        }},
        {{
            "path": "backend/main.py",
            "content": "file content here"
        }}
    ]
}}

Rules:

1. Generate practical source files based on the requirements
   and architecture.
2. Every file must have a relative path.
3. Every file must contain complete source code.
4. Do not use markdown code fences.
5. Do not add explanations outside the JSON.
6. Do not generate .env files.
7. Do not include API keys or passwords.
"""

    response = llm.invoke(prompt)

    # Gemini may return content as a list of blocks
    if isinstance(response.content, list):

        content = "\n".join(
            str(block.get("text", block))
            if isinstance(block, dict)
            else str(block)
            for block in response.content
        )

    else:

        content = str(response.content)

    content = content.strip()

    # Remove markdown fences if Gemini adds them
    if content.startswith("```json"):

        content = content[len("```json"):].strip()

    if content.startswith("```"):

        content = content[len("```"):].strip()

    if content.endswith("```"):

        content = content[:-3].strip()

    try:

        result = json.loads(content)

        files = result.get("files", [])

    except json.JSONDecodeError:

        files = []

    generated_files = [
        file.get("path")
        for file in files
        if isinstance(file, dict) and file.get("path")
    ]

    return {
        **state,
        "tasks": files,
        "generated_files": generated_files
    }