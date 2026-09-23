import json

from services.llm import invoke_llm
from graph.state import ProjectState


# ============================================================
# JSON CLEANING
# ============================================================

def clean_json_response(content: str) -> str:
    """
    Remove markdown code fences and extract the JSON object.
    """

    if not content:
        raise ValueError(
            "Developer returned an empty response."
        )

    content = content.strip()

    # Remove ```json
    if content.startswith("```json"):
        content = content[len("```json"):].strip()

    # Remove ```
    elif content.startswith("```"):
        content = content[len("```"):].strip()

    # Remove ending ```
    if content.endswith("```"):
        content = content[:-3].strip()

    # Try direct JSON first.
    try:
        json.loads(content)
        return content
    except json.JSONDecodeError:
        pass

    # --------------------------------------------------------
    # Extract first complete JSON object.
    # This helps when the provider adds extra text.
    # --------------------------------------------------------

    start = content.find("{")

    if start == -1:
        raise ValueError(
            "No JSON object found in Developer response."
        )

    decoder = json.JSONDecoder()

    try:
        _, end = decoder.raw_decode(
            content[start:]
        )

        return content[start:start + end]

    except json.JSONDecodeError as error:
        raise ValueError(
            f"Developer returned invalid or incomplete JSON: {error}"
        )


# ============================================================
# DUPLICATE FILE REMOVAL
# ============================================================

def remove_duplicate_files(
    files: list[dict],
) -> list[dict]:
    """
    Remove duplicate file paths and normalize paths.
    """

    unique = {}

    for file in files:

        if not isinstance(
            file,
            dict,
        ):
            continue

        path = file.get("path")
        content = file.get("content")

        if not path or content is None:
            continue

        path = str(path).replace(
            "\\",
            "/",
        )

        # Never allow generated_project/ prefix.
        if path.startswith(
            "generated_project/"
        ):
            path = path[
                len("generated_project/"):
            ]

        # Prevent absolute paths.
        if path.startswith("/"):
            continue

        # Prevent Windows absolute paths.
        if len(path) >= 2 and path[1] == ":":
            continue

        # Prevent path traversal.
        path_parts = path.split("/")

        if ".." in path_parts:
            continue

        unique[path] = {
            "path": path,
            "content": str(content),
        }

    return list(
        unique.values()
    )


# ============================================================
# RESPONSE CONTENT EXTRACTION
# ============================================================

def extract_response_content(response) -> str:
    """
    Extract text from the AIMessage returned by invoke_llm().
    """

    if response is None:
        raise ValueError(
            "Developer received an empty LLM response."
        )

    content = getattr(
        response,
        "content",
        response,
    )

    # --------------------------------------------------------
    # String
    # --------------------------------------------------------

    if isinstance(
        content,
        str,
    ):
        content = content.strip()

        if not content:
            raise ValueError(
                "Developer received empty response content."
            )

        return content

    # --------------------------------------------------------
    # List
    # --------------------------------------------------------

    if isinstance(
        content,
        list,
    ):

        parts = []

        for block in content:

            if isinstance(
                block,
                dict,
            ):

                text = block.get(
                    "text"
                )

                if text:
                    parts.append(
                        str(text)
                    )

            elif hasattr(
                block,
                "text",
            ):

                text = getattr(
                    block,
                    "text",
                )

                if text:
                    parts.append(
                        str(text)
                    )

            else:

                parts.append(
                    str(block)
                )

        result = "\n".join(
            parts
        ).strip()

        if not result:
            raise ValueError(
                "Developer received empty response content."
            )

        return result

    # --------------------------------------------------------
    # Dictionary
    # --------------------------------------------------------

    if isinstance(
        content,
        dict,
    ):

        if "text" in content:

            result = str(
                content["text"]
            ).strip()

        else:

            result = json.dumps(
                content,
                ensure_ascii=False,
            )

        if not result:
            raise ValueError(
                "Developer received empty response content."
            )

        return result

    # --------------------------------------------------------
    # Fallback
    # --------------------------------------------------------

    result = str(
        content
    ).strip()

    if not result:
        raise ValueError(
            "Developer received empty response content."
        )

    return result


# ============================================================
# VALIDATE GENERATED FILES
# ============================================================

def validate_generated_files(
    files: list,
) -> list[dict]:
    """
    Validate the files returned by the Developer Agent.
    """

    if not isinstance(
        files,
        list,
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

    return valid_files


# ============================================================
# DEVELOPER AGENT
# ============================================================

def developer_agent(
    state: ProjectState,
) -> ProjectState:

    user_request = state.get(
        "user_request",
        "",
    )

    requirements_list = state.get(
        "requirements",
        [],
    )

    requirements = "\n".join(
        f"- {req}"
        for req in requirements_list[:15]
    )

    architecture = state.get(
        "architecture",
        {},
    )

    # --------------------------------------------------------
    # Compact architecture
    # --------------------------------------------------------

    architecture_json = json.dumps(
        architecture,
        indent=2,
        ensure_ascii=False,
    )

    expected_files = architecture.get(
        "folder_structure",
        [],
    )

    # Keep the file list compact.
    expected_files = expected_files[:30]

    expected_files_text = "\n".join(
        f"- {file_path}"
        for file_path in expected_files
    )

    # ========================================================
    # DEVELOPER PROMPT
    # ========================================================

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

RETURN ONLY VALID JSON.

Required JSON structure:

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
3. Follow the ARCHITECTURE exactly.
4. Do NOT invent requirements.
5. Do NOT invent unnecessary modules.
6. Do NOT invent unnecessary classes.
7. Do NOT invent unnecessary services.
8. Do NOT invent unnecessary validators.
9. Do NOT invent unnecessary exception files.
10. Do NOT invent unnecessary APIs.
11. Do NOT invent databases unless required.
12. Do NOT invent authentication unless required.
13. Do NOT introduce unnecessary frameworks.
14. Do NOT introduce unnecessary dependencies.
15. Generate all files required by the architecture.
16. You MAY generate unit tests when appropriate.
17. Tests MUST test the actual generated implementation.
18. Tests MUST NOT require external packages unless explicitly required.
19. For Python projects, prefer unittest from the standard library.
20. Never use pytest unless explicitly required.
21. Every generated file must have complete content.
22. Use relative file paths only.
23. Never prefix paths with generated_project/.
24. Never generate duplicate file paths.
25. Never generate .env files.
26. Never include API keys.
27. Never include passwords.
28. Never include secrets.
29. Use Python standard library unless another dependency is explicitly required.
30. Python CLI programs may use input().
31. Python business logic must be independently testable.
32. Calculation/business functions should return values instead of only printing results.
33. Do not create unnecessary files.
34. Keep the implementation simple and practical.
35. Do not use markdown code fences.
36. Do not add explanations outside the JSON.
37. Return complete JSON.
38. Do not stop in the middle of a file.
39. Make sure every JSON string is properly escaped.
40. Make sure the final response ends with valid closing JSON.

IMPORTANT:

The generated tests must match the generated source code.

Do not create tests for files, functions, classes,
exceptions, or modules that do not exist.

For a simple Python calculator, a valid structure could be:

calculator/__init__.py
calculator/calc.py
calculator/main.py
tests/test_calc.py
README.md

But ONLY generate this structure if it matches
the actual requirements and architecture.

Keep the implementation compact.

Do not include long explanations in source files.

Return ONLY the JSON object.
"""

    print(
        "\n========== DEVELOPER AGENT =========="
    )

    # ========================================================
    # ATTEMPTS
    # ========================================================

    # Two attempts are retained.
    # The second attempt uses a more explicit compact prompt.

    for attempt in range(1, 3):

        try:

            print(
                f"Developer attempt: {attempt}"
            )

            # IMPORTANT:
            # The Developer needs more output than Code Reviewer.
            # But using the default 4000 caused Groq to return
            # incomplete JSON. Keep it controlled.
            response = invoke_llm(
            prompt,
            max_tokens=6000,
            )

            content = extract_response_content(
                response
            )

            print(
                f"Developer response length: "
                f"{len(content)} characters"
            )

            content = clean_json_response(
                content
            )

            result = json.loads(
                content
            )

            if not isinstance(
                result,
                dict,
            ):
                raise ValueError(
                    "Developer response must be a JSON object."
                )

            files = result.get(
                "files",
                [],
            )

            valid_files = validate_generated_files(
                files
            )

            # ------------------------------------------------
            # Generate project file references.
            # ------------------------------------------------

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

                "generated_files": generated_files,
            }

        except (
            json.JSONDecodeError,
            ValueError,
        ) as error:

            print(
                f"⚠️ Developer JSON failed "
                f"on attempt {attempt}: {error}"
            )

            # ------------------------------------------------
            # Second attempt
            # ------------------------------------------------

            if attempt == 1:

                prompt = f"""
You are the Developer Agent.

Your previous response was invalid or incomplete.

Generate the project again.

USER REQUEST:
{user_request}

PROJECT REQUIREMENTS:
{requirements}

ARCHITECTURE:
{architecture_json}

REQUIRED FILES:
{expected_files_text}

RETURN ONLY ONE VALID JSON OBJECT.

Required structure:

{{
  "files": [
    {{
      "path": "relative/file/path",
      "content": "complete source code"
    }}
  ]
}}

CRITICAL RULES:

- Generate only required files.
- Do not invent features.
- Do not invent dependencies.
- Do not invent frameworks.
- Do not create duplicate paths.
- Do not create .env files.
- Do not include secrets.
- Use relative paths.
- Do not use generated_project/ in paths.
- Tests must match actual source code.
- Python tests should use unittest.
- Do not use pytest unless explicitly required.
- Every file must contain complete source code.
- Do not truncate files.
- Properly escape JSON strings.
- Return valid JSON only.
- Do not use markdown code fences.
- Do not add any explanation.
- Make the response compact.

IMPORTANT:

The JSON must be completely closed.

The response MUST end with:

}}
"""

            else:

                raise RuntimeError(
                    "Developer Agent failed to generate "
                    f"valid JSON after {attempt} attempts: "
                    f"{error}"
                )

        except Exception as error:

            # ------------------------------------------------
            # Provider or unexpected error
            # ------------------------------------------------

            print(
                f"⚠️ Developer attempt {attempt} "
                f"failed: {error}"
            )

            if attempt == 2:

                raise RuntimeError(
                    "Developer Agent failed after "
                    f"{attempt} attempts: {error}"
                )

    # This should never be reached.
    raise RuntimeError(
        "Developer Agent ended without generating files."
    )