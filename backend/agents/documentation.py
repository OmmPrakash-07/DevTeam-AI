import json

from services.llm import invoke_llm
from graph.state import ProjectState
from tools.filesystem import create_project_files


def documentation_agent(
    state: ProjectState
) -> ProjectState:


    requirements = state.get(
        "requirements",
        []
    )

    architecture = state.get(
        "architecture",
        {}
    )

    tasks = state.get(
        "tasks",
        []
    )

    review = state.get(
        "review",
        {}
    )

    prompt = f"""
You are the Documentation Agent in an autonomous
software development team.

Create professional documentation for the generated
software project.

PROJECT REQUIREMENTS:
{json.dumps(requirements, indent=2)}

ARCHITECTURE:
{json.dumps(architecture, indent=2)}

GENERATED FILES:
{json.dumps(tasks, indent=2)}

CODE REVIEW:
{json.dumps(review, indent=2)}

Create a README.md containing:

1. Project title
2. Project overview
3. Features
4. Technology stack
5. Project structure
6. Installation instructions
7. How to run the project
8. API information if applicable
9. Testing information
10. Future improvements

Return ONLY valid JSON using exactly this structure:

{{
    "files": [
        {{
            "path": "README.md",
            "content": "complete README content"
        }}
    ]
}}

Rules:

1. Generate complete documentation.
2. Use information from the project data provided above.
3. Do not invent API keys, passwords, or secrets.
4. Do not include .env contents.
5. Do not add explanations outside the JSON.
6. Do not use markdown code fences around the JSON.
"""

    response = invoke_llm(prompt)

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

    # Remove possible Markdown code fences
    if content.startswith("```json"):
        content = content[len("```json"):].strip()

    if content.startswith("```"):
        content = content[len("```"):].strip()

    if content.endswith("```"):
        content = content[:-3].strip()

    try:

        result = json.loads(content)

        documentation_files = result.get(
            "files",
            []
        )

    except json.JSONDecodeError:

        documentation_files = []

    all_tasks = tasks + documentation_files

    # Write documentation files to disk
    if documentation_files:

        try:

            create_project_files(
                "generated_project",
                documentation_files
            )

        except Exception as error:

            return {
                **state,
                "tasks": tasks + documentation_files,
                "errors": state.get("errors", []) + [
                    f"Documentation file write failed: {error}"
                ]
            }

    all_tasks = tasks + documentation_files

    return {
        **state,
        "tasks": all_tasks,
        "generated_files": [
            *state.get("generated_files", []),
            *[
                f"generated_project/{file.get('path')}"
                for file in documentation_files
                if isinstance(file, dict) and file.get("path")
            ]
        ]
    }