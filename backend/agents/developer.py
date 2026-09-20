import json

from services.llm import invoke_llm
from graph.state import ProjectState


def clean_json_response(content: str) -> str:
    content = content.strip()

    if content.startswith("```json"):
        content = content[len("```json"):].strip()
    elif content.startswith("```"):
        content = content[len("```"):].strip()

    if content.endswith("```"):
        content = content[:-3].strip()

    return content


def remove_duplicate_files(files: list[dict]) -> list[dict]:

    unique = {}

    for file in files:

        if not isinstance(file, dict):
            continue

        path = file.get("path")
        content = file.get("content")

        if not path or content is None:
            continue

        path = str(path).replace("\\", "/")

        if path.startswith("generated_project/"):
            path = path[len("generated_project/"):]

        unique[path] = {
            "path": path,
            "content": str(content)
        }

    return list(unique.values())


def developer_agent(state: ProjectState) -> ProjectState:

    user_request = state.get(
        "user_request",
        ""
    )

    requirements = "\n".join(
        f"- {req}"
        for req in state.get("requirements", [])
    )

    architecture = state.get(
        "architecture",
        {}
    )

    architecture_json = json.dumps(
        architecture,
        indent=2
    )

    expected_files = architecture.get(
        "folder_structure",
        []
    )

    expected_files_text = "\n".join(
        f"- {file_path}"
        for file_path in expected_files
    )

    prompt = f"""
You are the Developer Agent in an autonomous
software development team.

USER REQUEST:
{user_request}

PROJECT REQUIREMENTS:
{requirements}

ARCHITECTURE:
{architecture_json}

REQUIRED FILES:
{expected_files_text}

Generate the complete project.

Return ONLY valid JSON:

{{
  "files": [
    {{
      "path": "relative/file/path",
      "content": "complete source code"
    }}
  ]
}}

STRICT RULES:

1. Follow the USER REQUEST exactly.
2. Follow the PROJECT REQUIREMENTS exactly.
3. Do NOT invent requirements.
4. Do NOT invent extra modules, classes, services,
   validators, exception files, APIs, databases,
   authentication systems, or frameworks unless they
   are explicitly required by the requirements or architecture.
5. Generate all files required by the architecture.
6. You MAY generate unit tests when appropriate.
7. Tests MUST test the actual generated implementation.
8. Tests MUST NOT require external packages unless the
   architecture explicitly requires them.
9. For Python projects, prefer unittest from the Python
   standard library instead of pytest.
10. Never use "import pytest" unless pytest is explicitly
    required by the architecture.
11. Every file must have complete content.
12. Use relative paths only.
13. Never prefix paths with "generated_project/".
14. Never generate duplicate paths.
15. Do not generate .env files.
16. Do not include secrets or API keys.
17. Use Python standard library unless another dependency
    is explicitly required.
18. Python CLI programs may use input(), but their core
    business logic must be independently testable.
19. Calculation/business functions should return values
    rather than only printing results.
20. Do not create unnecessary files.
21. Keep the implementation simple and practical.
22. Do not use markdown code fences.
23. Do not add explanations outside the JSON.

IMPORTANT:

The generated tests must match the generated source code.

Do not create tests for files, functions, classes, exceptions,
or modules that do not exist.

For a simple Python calculator, a valid structure could be:

calculator/__init__.py
calculator/calc.py
calculator/main.py
tests/test_calc.py
README.md

But only generate this structure if it matches the
requirements and architecture.

Keep the total response compact.
"""

    print(
        "\n========== DEVELOPER AGENT =========="
    )

    for attempt in range(1, 3):

        try:

            print(
                f"Developer attempt: {attempt}"
            )

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

            files = result.get(
                "files",
                []
            )

            if not isinstance(
                files,
                list
            ):

                raise ValueError(
                    "'files' must be a list."
                )

            valid_files = remove_duplicate_files(
                files
            )

            if not valid_files:

                raise ValueError(
                    "No valid files were generated."
                )

            generated_files = [
                f"generated_project/{file['path']}"
                for file in valid_files
            ]

            print(
                f"✅ Developer generated "
                f"{len(valid_files)} unique files."
            )

            for file_path in generated_files:

                print(
                    f"   📄 {file_path}"
                )

            print(
                "======================================\n"
            )

            return {
                **state,
                "tasks": valid_files,
                "generated_files": generated_files
            }

        except (
            json.JSONDecodeError,
            ValueError
        ) as error:

            print(
                f"⚠️ Developer JSON failed "
                f"on attempt {attempt}: {error}"
            )

            if attempt == 1:

                prompt += """

Your previous response was invalid.

Generate the project again.

Remember:

- Do not invent modules.
- Do not invent dependencies.
- Use unittest instead of pytest.
- Tests must match the generated source code.
- Return complete valid JSON.
"""

            else:

                raise RuntimeError(
                    "Developer Agent failed to generate "
                    f"valid JSON after {attempt} attempts: "
                    f"{error}"
                )