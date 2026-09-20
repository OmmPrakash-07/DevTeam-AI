import json
from pathlib import Path

from graph.state import ProjectState
from services.llm import invoke_llm
from tools.filesystem import get_project_dir


def clean_json_response(content: str) -> str:
    """
    Remove markdown code fences from LLM response.
    """

    content = content.strip()

    if content.startswith("```json"):
        content = content[7:]

    elif content.startswith("```"):
        content = content[3:]

    if content.endswith("```"):
        content = content[:-3]

    return content.strip()


def normalize_path(file_path: str) -> str:
    """
    Normalize generated file paths.
    """

    file_path = file_path.replace("\\", "/")

    if file_path.startswith("generated_project/"):
        file_path = file_path[len("generated_project/"):]

    return file_path


def read_project_files(
    project_dir: Path,
    generated_files: list
) -> list:
    """
    Read actual generated project files.
    """

    project_files = []

    seen = set()

    for file_path in generated_files:

        if not file_path:
            continue

        relative_path = normalize_path(
            str(file_path)
        )

        if not relative_path:
            continue

        if relative_path in seen:
            continue

        seen.add(relative_path)

        target = (
            project_dir / relative_path
        ).resolve()

        # Prevent path traversal.
        try:

            target.relative_to(
                project_dir.resolve()
            )

        except ValueError:

            continue

        if not target.exists():
            continue

        if not target.is_file():
            continue

        try:

            content = target.read_text(
                encoding="utf-8"
            )

            project_files.append({
                "path": relative_path,
                "content": content
            })

        except Exception:

            continue

    return project_files


def write_documentation(
    project_dir: Path,
    readme_content: str
) -> str:
    """
    Write README.md inside the current project directory.
    """

    readme_path = (
        project_dir / "README.md"
    ).resolve()

    # Prevent path traversal.
    try:

        readme_path.relative_to(
            project_dir.resolve()
        )

    except ValueError:

        raise ValueError(
            "README path is outside the project directory."
        )

    readme_path.write_text(
        readme_content,
        encoding="utf-8"
    )

    return "README.md"


def documentation_agent(
    state: ProjectState
):

    project_id = state.get(
        "project_id"
    )

    if not project_id:

        error = (
            "Project ID is missing "
            "from project state."
        )

        return {
            **state,

            "errors": [
                *state.get("errors", []),
                error
            ]
        }

    project_dir = get_project_dir(
        project_id
    )

    user_request = state.get(
        "user_request",
        ""
    )

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

    generated_files = state.get(
        "generated_files",
        []
    )

    test_results = state.get(
        "test_results",
        {}
    )

    review = state.get(
        "review",
        {}
    )

    project_files = read_project_files(
        project_dir,
        generated_files
    )

    prompt = f"""
You are the Documentation Agent in an autonomous
software development team.

Create accurate documentation for the generated project.

PROJECT ID:
{project_id}

USER REQUEST:
{user_request}

REQUIREMENTS:
{json.dumps(requirements, indent=2)}

ARCHITECTURE:
{json.dumps(architecture, indent=2)}

TASKS:
{json.dumps(tasks, indent=2)}

GENERATED FILES:
{json.dumps(project_files, indent=2)}

TEST RESULTS:
{json.dumps(test_results, indent=2)}

CODE REVIEW:
{json.dumps(review, indent=2)}

Create a professional README.md.

IMPORTANT RULES:

1. Document only what actually exists in the project.
2. Do not invent features.
3. Do not claim dependencies that are not used.
4. Do not claim files that do not exist.
5. Do not claim databases, APIs, authentication, frontend,
   backend services, frameworks, or libraries unless they
   actually exist.
6. Keep the documentation consistent with the generated code.
7. Mention how to install/run the project only when the
   required commands can be determined from the actual files.
8. Include testing instructions when tests exist.
9. Mention the project structure based on actual files.
10. Do not include secrets or API keys.
11. Do not create unnecessary documentation files.
12. Generate ONLY the README content.
13. Use normal UTF-8 characters.
14. Do not use mojibake or corrupted characters.
15. Do not use generated_project/ as the displayed project
    directory name.
16. Keep the README concise but useful.

The README should normally contain:

# Project Title

## Description

## Features

## Technologies Used

## Project Structure

## Installation

## Usage

## Testing

## Project Information

Only include sections that are relevant to the actual project.

Return ONLY valid JSON:

{{
    "readme": "# Project Title\\n\\n...",
    "summary": "Short description of the documentation."
}}
"""

    try:

        response = invoke_llm(
            prompt
        )

        content = clean_json_response(
            response.content
        )

        result = json.loads(
            content
        )

    except Exception as error:

        documentation_error = (
            f"Documentation LLM error: {error}"
        )

        return {
            **state,

            "errors": [
                *state.get("errors", []),
                documentation_error
            ]
        }

    readme_content = result.get(
        "readme",
        ""
    )

    if not isinstance(
        readme_content,
        str
    ):

        readme_content = str(
            readme_content
        )

    readme_content = readme_content.strip()

    if not readme_content:

        error = (
            "Documentation Agent returned "
            "empty README content."
        )

        return {
            **state,

            "errors": [
                *state.get("errors", []),
                error
            ]
        }

    try:

        readme_file = write_documentation(
            project_dir,
            readme_content
        )

    except Exception as error:

        write_error = (
            f"Failed to write README.md: {error}"
        )

        return {
            **state,

            "errors": [
                *state.get("errors", []),
                write_error
            ]
        }

    normalized_generated_files = []

    for file_path in generated_files:

        normalized = normalize_path(
            str(file_path)
        )

        if normalized:
            normalized_generated_files.append(
                normalized
            )

    if readme_file not in normalized_generated_files:

        normalized_generated_files.append(
            readme_file
        )

    return {
        **state,

        "project_id": project_id,

        "generated_files": normalized_generated_files,

        "documentation": {
            "status": "completed",
            "file": readme_file,
            "project_id": project_id,
            "project_directory": str(
                project_dir
            ),
            "summary": result.get(
                "summary",
                "README.md generated successfully."
            )
        }
    }