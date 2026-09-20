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
    Read generated project files for code review.
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

        path = (
            project_dir / relative_path
        ).resolve()

        # Prevent path traversal.
        try:

            path.relative_to(
                project_dir.resolve()
            )

        except ValueError:

            continue

        if not path.exists():
            continue

        if not path.is_file():
            continue

        try:

            content = path.read_text(
                encoding="utf-8"
            )

            project_files.append({
                "path": relative_path,
                "content": content
            })

        except Exception:

            continue

    return project_files


def code_reviewer_agent(
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
            "review": {
                "overall_status": "failed",
                "issues": [error],
                "suggestions": [],
                "summary": error
            },
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

    generated_files = state.get(
        "generated_files",
        []
    )

    tasks = state.get(
        "tasks",
        []
    )

    test_results = state.get(
        "test_results",
        {}
    )

    project_files = read_project_files(
        project_dir,
        generated_files
    )

    files_for_review = []

    for file in project_files:

        files_for_review.append({
            "path": file["path"],
            "content": file["content"]
        })

    prompt = f"""
You are the Code Reviewer Agent in an autonomous
software development team.

Review the generated software project carefully.

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

TEST RESULTS:
{json.dumps(test_results, indent=2)}

GENERATED PROJECT FILES:
{json.dumps(files_for_review, indent=2)}

Review the project for:

1. Correctness
2. Requirement compliance
3. Architecture consistency
4. Code quality
5. Import correctness
6. Error handling
7. Security problems
8. Unnecessary dependencies
9. Duplicate or unnecessary code
10. Test quality
11. Documentation consistency
12. Obvious runtime problems

IMPORTANT RULES:

- Review the actual generated files.
- Do not invent requirements.
- Do not request unnecessary features.
- Do not recommend unnecessary frameworks.
- Do not recommend unnecessary dependencies.
- Do not require pytest unless explicitly required.
- Prefer unittest for Python projects.
- Do not treat optional improvements as mandatory defects.
- Distinguish real issues from suggestions.
- If tests passed, do not claim they failed without evidence.
- Keep the review specific and actionable.
- Do not modify files.
- Do not create files.

Return ONLY valid JSON.

Required format:

{{
    "overall_status": "approved",
    "issues": [],
    "suggestions": [],
    "summary": "Short review summary."
}}

If there are actual problems:

{{
    "overall_status": "changes_requested",
    "issues": [
        "Specific issue 1",
        "Specific issue 2"
    ],
    "suggestions": [
        "Optional improvement 1"
    ],
    "summary": "Short review summary."
}}
"""

    try:

        response = invoke_llm(
            prompt
        )

        content = clean_json_response(
            response.content
        )

        review = json.loads(
            content
        )

    except Exception as error:

        review_error = (
            f"Code reviewer error: {error}"
        )

        return {
            **state,

            "review": {
                "overall_status": "failed",
                "issues": [review_error],
                "suggestions": [],
                "summary": review_error
            },

            "errors": [
                *state.get("errors", []),
                review_error
            ]
        }

    # Validate review structure.
    overall_status = review.get(
        "overall_status",
        "approved"
    )

    if overall_status not in {
        "approved",
        "changes_requested",
        "failed"
    }:

        overall_status = "approved"

    issues = review.get(
        "issues",
        []
    )

    suggestions = review.get(
        "suggestions",
        []
    )

    summary = review.get(
        "summary",
        ""
    )

    if not isinstance(
        issues,
        list
    ):
        issues = [str(issues)]

    if not isinstance(
        suggestions,
        list
    ):
        suggestions = [str(suggestions)]

    if not isinstance(
        summary,
        str
    ):
        summary = str(summary)

    final_review = {
        "overall_status": overall_status,

        "issues": issues,

        "suggestions": suggestions,

        "summary": summary,

        "project_id": project_id,

        "project_directory": str(
            project_dir
        )
    }

    return {
        **state,

        "project_id": project_id,

        "review": final_review
    }