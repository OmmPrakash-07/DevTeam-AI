from pathlib import Path
import json

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


def debugger_agent(state: ProjectState):

    project_id = state.get("project_id")

    if not project_id:
        error = "Project ID is missing from project state."

        return {
            **state,
            "errors": [
                *state.get("errors", []),
                error
            ]
        }

    project_dir = get_project_dir(project_id)

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

    test_results = state.get(
        "test_results",
        {}
    )

    previous_errors = state.get(
        "errors",
        []
    )

    debug_attempts = state.get(
        "debug_attempts",
        0
    )

    debug_attempts += 1

    # Prevent infinite debugging loops.
    if debug_attempts > 3:

        return {
            **state,
            "debug_attempts": debug_attempts
        }

    prompt = f"""
You are the Debugger Agent in an autonomous software development team.

Your job is to analyze test failures and provide minimal, correct fixes.

USER REQUEST:
{user_request}

REQUIREMENTS:
{json.dumps(requirements, indent=2)}

ARCHITECTURE:
{json.dumps(architecture, indent=2)}

CURRENT TASKS:
{json.dumps(tasks, indent=2)}

TEST RESULTS:
{json.dumps(test_results, indent=2)}

CURRENT ERRORS:
{json.dumps(previous_errors, indent=2)}

DEBUG ATTEMPT:
{debug_attempts}

PROJECT ID:
{project_id}

PROJECT DIRECTORY:
{project_dir}

IMPORTANT RULES:

1. Fix the actual reported problem.
2. Do not invent new requirements.
3. Do not add unnecessary features.
4. Do not introduce unnecessary dependencies.
5. Prefer Python standard library.
6. Tests should use unittest unless pytest is explicitly required.
7. Do not import pytest unless the project explicitly requires it.
8. Keep the existing architecture.
9. Do not create duplicate files.
10. Do not use absolute file paths.
11. Do not include generated_project/ in the path.
12. Only return files that actually need to be created or modified.
13. If the generated test itself is incorrect, fix the test.
14. Make sure imports match the actual project structure.
15. Keep the fix minimal.
16. Do not create .env files or secrets.
17. Do not modify unrelated files.

Return ONLY valid JSON.

Required format:

{{
    "files": [
        {{
            "path": "relative/path/to/file.py",
            "content": "complete corrected file content"
        }}
    ],
    "explanation": "short explanation of the bug and fix"
}}

If no code change is required, return:

{{
    "files": [],
    "explanation": "No code changes required."
}}
"""

    try:

        response = invoke_llm(prompt)

        content = clean_json_response(
            response.content
        )

        result = json.loads(content)

    except Exception as error:

        debug_error = (
            f"Debugger LLM error: {error}"
        )

        return {
            **state,
            "debug_attempts": debug_attempts,
            "errors": [
                *previous_errors,
                debug_error
            ]
        }

    files = result.get(
        "files",
        []
    )

    if not isinstance(files, list):
        files = []

    fixed_files = []

    updated_tasks = list(tasks)

    generated_files = list(
        state.get(
            "generated_files",
            []
        )
    )

    seen_paths = set()

    for file in files:

        if not isinstance(file, dict):
            continue

        raw_path = file.get(
            "path"
        )

        if not raw_path:
            continue

        relative_path = normalize_path(
            str(raw_path)
        )

        if not relative_path:
            continue

        # Prevent duplicate files.
        if relative_path in seen_paths:
            continue

        seen_paths.add(relative_path)

        path = Path(relative_path)

        # Absolute paths are not allowed.
        if path.is_absolute():

            continue

        target = (
            project_dir / path
        ).resolve()

        # Prevent path traversal.
        try:

            target.relative_to(
                project_dir.resolve()
            )

        except ValueError:

            continue

        content = file.get(
            "content",
            ""
        )

        if not isinstance(
            content,
            str
        ):
            content = str(content)

        target.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        target.write_text(
            content,
            encoding="utf-8"
        )

        fixed_files.append(
            relative_path
        )

        # Update existing task if present.
        task_found = False

        for task in updated_tasks:

            task_path = normalize_path(
                str(task.get("path", ""))
            )

            if task_path == relative_path:

                task["path"] = relative_path
                task["content"] = content
                task_found = True
                break

        # Add new task only if absolutely necessary.
        if not task_found:

            updated_tasks.append({
                "path": relative_path,
                "content": content
            })

        # Update generated files list.
        if relative_path not in [
            normalize_path(str(item))
            for item in generated_files
        ]:

            generated_files.append(
                relative_path
            )

    return {
        **state,

        "project_id": project_id,

        "tasks": updated_tasks,

        "generated_files": generated_files,

        "debug_attempts": debug_attempts,

        "errors": previous_errors,

        "debug_result": {
            "status": "completed",
            "attempt": debug_attempts,
            "fixed_files": fixed_files,
            "explanation": result.get(
                "explanation",
                ""
            )
        }
    }