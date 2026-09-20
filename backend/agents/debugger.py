import json

from services.llm import invoke_llm
from graph.state import ProjectState
from tools.filesystem import create_project_files


def clean_json_response(content: str) -> str:

    content = content.strip()

    if content.startswith("```json"):

        content = content[
            len("```json"):
        ].strip()

    elif content.startswith("```"):

        content = content[
            len("```"):
        ].strip()

    if content.endswith("```"):

        content = content[:-3].strip()

    return content


def normalize_path(path: str) -> str:

    path = str(path).replace(
        "\\",
        "/"
    )

    if path.startswith(
        "generated_project/"
    ):

        path = path[
            len("generated_project/"):
        ]

    return path


def debugger_agent(
    state: ProjectState
) -> ProjectState:

    debug_attempts = (
        state.get(
            "debug_attempts",
            0
        ) + 1
    )

    errors = state.get(
        "errors",
        []
    )

    tasks = state.get(
        "tasks",
        []
    )

    if not errors:

        return {
            **state,
            "debug_attempts": debug_attempts
        }

    error_text = "\n".join(
        f"- {error}"
        for error in errors
    )

    files = json.dumps(
        tasks,
        indent=2
    )

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

    prompt = f"""
You are the Debugger Agent.

USER REQUEST:
{user_request}

PROJECT REQUIREMENTS:
{requirements}

TEST ERRORS:
{error_text}

CURRENT GENERATED FILES:
{files}

DEBUG ATTEMPT:
{debug_attempts}

Fix the actual errors without changing the
project requirements or inventing new requirements.

Return ONLY valid JSON:

{{
    "files": [
        {{
            "path": "relative/file/path",
            "content": "complete fixed file content"
        }}
    ],
    "explanation": "short explanation"
}}

STRICT RULES:

1. Fix only the actual reported errors.
2. Do not invent modules just because a test imports them.
3. Do not create missing architecture unless the
   original requirements explicitly require it.
4. Tests must match the implementation.
5. If a generated test is incorrect, fix the test.
6. Do not add pytest if pytest was not required.
7. Prefer Python unittest.
8. Do not add external dependencies unnecessarily.
9. Return complete file contents.
10. Use relative paths only.
11. Never use generated_project/ in paths.
12. Do not generate secrets.
13. Do not change unrelated files.
14. Do not use markdown code fences.
15. Do not add explanations outside JSON.
"""

    print(
        "\n========== DEBUGGER AGENT =========="
    )

    try:

        response = invoke_llm(prompt)

        if isinstance(
            response.content,
            list
        ):

            content = "\n".join(
                str(block.get("text", block))
                if isinstance(block, dict)
                else str(block)
                for block in response.content
            )

        else:

            content = str(
                response.content
            )

        content = clean_json_response(
            content
        )

        result = json.loads(
            content
        )

        fixed_files = result.get(
            "files",
            []
        )

        explanation = result.get(
            "explanation",
            ""
        )

        if not isinstance(
            fixed_files,
            list
        ):

            raise ValueError(
                "'files' must be a list."
            )

    except Exception as error:

        print(
            f"❌ Debugger failed: {error}"
        )

        return {
            **state,
            "debug_attempts": debug_attempts,
            "errors": [
                f"Debugger failed: {error}"
            ]
        }

    normalized_files = []

    for file in fixed_files:

        if not isinstance(
            file,
            dict
        ):
            continue

        path = file.get(
            "path"
        )

        content = file.get(
            "content"
        )

        if not path or content is None:
            continue

        normalized_files.append({
            "path": normalize_path(path),
            "content": str(content)
        })

    if not normalized_files:

        return {
            **state,
            "debug_attempts": debug_attempts,
            "errors": [
                "Debugger returned no valid files."
            ]
        }

    try:

        create_project_files(
            "generated_project",
            normalized_files
        )

    except Exception as error:

        return {
            **state,
            "debug_attempts": debug_attempts,
            "errors": [
                f"Debugger file write failed: {error}"
            ]
        }

    updated_tasks = tasks.copy()

    for fixed_file in normalized_files:

        fixed_path = fixed_file["path"]

        replaced = False

        for index, existing_file in enumerate(
            updated_tasks
        ):

            if normalize_path(
                existing_file.get("path", "")
            ) == fixed_path:

                updated_tasks[index] = fixed_file

                replaced = True

                break

        if not replaced:

            updated_tasks.append(
                fixed_file
            )

    generated_files = []

    for task in updated_tasks:

        path = task.get(
            "path"
        )

        if not path:
            continue

        normalized = normalize_path(
            path
        )

        full_path = (
            f"generated_project/{normalized}"
        )

        if full_path not in generated_files:

            generated_files.append(
                full_path
            )

    print(
        f"🔧 Debugger fixed "
        f"{len(normalized_files)} files."
    )

    print(
        f"💡 {explanation}"
    )

    print(
        "===================================\n"
    )

    return {
        **state,
        "tasks": updated_tasks,
        "generated_files": generated_files,
        "errors": [],
        "debug_attempts": debug_attempts,
        "review": {
            "debugger_explanation": explanation
        }
    }