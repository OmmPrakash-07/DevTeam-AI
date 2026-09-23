import json

from pathlib import Path

from graph.state import ProjectState

from services.llm import invoke_llm

from tools.filesystem import get_project_dir


# ============================================================
# RESPONSE TEXT EXTRACTION
# ============================================================

def extract_text_from_response(response) -> str:
    """
    Extract plain text from different LLM response formats.
    """

    content = getattr(
        response,
        "content",
        response,
    )

    # --------------------------------------------------------
    # STRING
    # --------------------------------------------------------

    if isinstance(content, str):
        return content.strip()

    # --------------------------------------------------------
    # LIST
    # --------------------------------------------------------

    if isinstance(content, list):

        parts = []

        for block in content:

            if isinstance(block, dict):

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

        return "\n".join(
            parts
        ).strip()

    # --------------------------------------------------------
    # DICTIONARY
    # --------------------------------------------------------

    if isinstance(content, dict):

        if "text" in content:

            return str(
                content["text"]
            ).strip()

        return json.dumps(
            content,
            ensure_ascii=False,
        )

    # --------------------------------------------------------
    # OTHER OBJECT
    # --------------------------------------------------------

    return str(
        content
    ).strip()


# ============================================================
# JSON CLEANING
# ============================================================

def clean_json_response(
    content: str,
) -> str:
    """
    Remove markdown code fences and extract JSON.
    """

    content = content.strip()

    # --------------------------------------------------------
    # Remove ```json
    # --------------------------------------------------------

    if content.startswith(
        "```json"
    ):

        content = content[
            len("```json"):
        ]

    # --------------------------------------------------------
    # Remove ```
    # --------------------------------------------------------

    elif content.startswith(
        "```"
    ):

        content = content[
            len("```"):
        ]

    # --------------------------------------------------------
    # Remove ending ```
    # --------------------------------------------------------

    if content.endswith(
        "```"
    ):

        content = content[
            :-len("```")
        ]

    content = content.strip()

    # --------------------------------------------------------
    # Direct JSON
    # --------------------------------------------------------

    try:

        json.loads(
            content
        )

        return content

    except json.JSONDecodeError:

        pass

    # --------------------------------------------------------
    # Find first JSON object
    # --------------------------------------------------------

    start = content.find(
        "{"
    )

    if start == -1:

        raise ValueError(
            "No JSON object found in code reviewer response."
        )

    decoder = json.JSONDecoder()

    try:

        _, end = decoder.raw_decode(
            content[start:]
        )

        return content[
            start:start + end
        ]

    except json.JSONDecodeError:

        pass

    raise ValueError(
        "Unable to extract valid JSON from code reviewer response."
    )


# ============================================================
# PATH NORMALIZATION
# ============================================================

def normalize_path(
    file_path: str,
) -> str:
    """
    Normalize generated project file paths.
    """

    file_path = file_path.replace(
        "\\",
        "/",
    )

    if file_path.startswith(
        "generated_project/"
    ):

        file_path = file_path[
            len("generated_project/"):
        ]

    return file_path


# ============================================================
# READ PROJECT FILES
# ============================================================

def read_project_files(
    project_dir: Path,
    generated_files: list,
) -> list:
    """
    Read generated project files safely.

    Path traversal is prevented by resolving the
    final path and checking that it remains inside
    the project directory.
    """

    project_files = []

    seen = set()

    project_root = project_dir.resolve()

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

        seen.add(
            relative_path
        )

        path = (
            project_root /
            relative_path
        ).resolve()

        # ----------------------------------------------------
        # Prevent path traversal
        # ----------------------------------------------------

        try:

            path.relative_to(
                project_root
            )

        except ValueError:

            continue

        # ----------------------------------------------------
        # Must exist
        # ----------------------------------------------------

        if not path.exists():
            continue

        if not path.is_file():
            continue

        # ----------------------------------------------------
        # Read file
        # ----------------------------------------------------

        try:

            content = path.read_text(
                encoding="utf-8"
            )

            project_files.append(
                {
                    "path": relative_path,
                    "content": content,
                }
            )

        except Exception:

            continue

    return project_files


# ============================================================
# COMPACT FILE CONTENT
# ============================================================

def build_review_files(
    project_files: list,
) -> list:
    """
    Keep the review prompt small.

    Large generated files can consume huge amounts
    of input tokens. The reviewer only needs a
    representative amount of source code.

    Limits:
    - Maximum per file: 3500 characters
    - Maximum total: 12000 characters
    """

    MAX_FILE_CHARS = 3500

    MAX_TOTAL_CHARS = 12000

    files = []

    total_chars = 0

    for file in project_files:

        path = file["path"]

        content = file["content"]

        remaining = (
            MAX_TOTAL_CHARS -
            total_chars
        )

        if remaining <= 0:
            break

        allowed = min(
            MAX_FILE_CHARS,
            remaining,
        )

        if len(content) > allowed:

            content = (
                content[:allowed]
                + "\n\n"
                + "[FILE CONTENT TRUNCATED FOR REVIEW]"
            )

        files.append(
            {
                "path": path,
                "content": content,
            }
        )

        total_chars += len(
            content
        )

    return files


# ============================================================
# CODE REVIEWER AGENT
# ============================================================

def code_reviewer_agent(
    state: ProjectState,
):
    project_id = state.get(
        "project_id"
    )

    # ========================================================
    # PROJECT ID
    # ========================================================

    if not project_id:

        error = (
            "Project ID is missing "
            "from project state."
        )

        return {
            **state,

            "review": {
                "overall_status": "failed",
                "issues": [
                    error
                ],
                "suggestions": [],
                "summary": error,
            },

            "errors": [
                *state.get(
                    "errors",
                    [],
                ),
                error,
            ],
        }

    # ========================================================
    # PROJECT DIRECTORY
    # ========================================================

    project_dir = get_project_dir(
        project_id
    )

    # ========================================================
    # INPUT STATE
    # ========================================================

    user_request = state.get(
        "user_request",
        "",
    )

    requirements = state.get(
        "requirements",
        [],
    )

    architecture = state.get(
        "architecture",
        {},
    )

    generated_files = state.get(
        "generated_files",
        [],
    )

    test_results = state.get(
        "test_results",
        {},
    )

    # ========================================================
    # READ GENERATED FILES
    # ========================================================

    project_files = read_project_files(
        project_dir,
        generated_files,
    )

    # Keep prompt compact.
    files_for_review = build_review_files(
        project_files
    )

    # ========================================================
    # COMPACT ARCHITECTURE
    # ========================================================

    architecture_summary = {
        "project_type": architecture.get(
            "project_type",
            "",
        ),

        "frontend": architecture.get(
            "frontend",
            {},
        ),

        "backend": architecture.get(
            "backend",
            {},
        ),

        "database": architecture.get(
            "database",
            {},
        ),

        "authentication": architecture.get(
            "authentication",
            "",
        ),

        "api_style": architecture.get(
            "api_style",
            "",
        ),
    }

    # ========================================================
    # COMPACT TEST RESULTS
    # ========================================================

    test_summary = {
        "status": test_results.get(
            "status",
            "unknown",
        ),

        "total_files": test_results.get(
            "total_files",
            0,
        ),

        "passed": test_results.get(
            "passed",
            0,
        ),

        "failed": test_results.get(
            "failed",
            0,
        ),

        "errors": test_results.get(
            "errors",
            0,
        ),
    }

    # ========================================================
    # COMPACT REQUIREMENTS
    # ========================================================

    # Prevent an unusually large requirement list
    # from consuming the entire reviewer prompt.

    compact_requirements = requirements[:10]

    # ========================================================
    # REVIEW PROMPT
    # ========================================================

    prompt = f"""
You are the Code Reviewer Agent.

Review the generated software project.

USER REQUEST:
{user_request}

REQUIREMENTS:
{json.dumps(compact_requirements, ensure_ascii=False)}

ARCHITECTURE:
{json.dumps(architecture_summary, ensure_ascii=False)}

TEST RESULTS:
{json.dumps(test_summary, ensure_ascii=False)}

GENERATED FILES:
{json.dumps(files_for_review, ensure_ascii=False)}

Check ONLY for real, evidence-based problems.

Review:

1. Correctness
2. Requirement compliance
3. Architecture consistency
4. Code quality
5. Import correctness
6. Error handling
7. Security problems
8. Unnecessary dependencies
9. Duplicate code
10. Test quality
11. Documentation consistency
12. Obvious runtime problems

IMPORTANT:

- Review the actual generated code.
- Do not invent requirements.
- Do not request unnecessary features.
- Do not recommend unnecessary frameworks.
- Do not recommend unnecessary dependencies.
- Do not require pytest unless explicitly required.
- Prefer unittest for Python projects.
- Do not treat optional improvements as defects.
- If tests passed, do not claim they failed.
- Keep issues specific and actionable.
- Do not modify files.
- Do not create files.
- Keep the response concise.
- Return ONLY valid JSON.
- Do not wrap the JSON in markdown.
- Do not include explanations outside the JSON.

Required format:

{{
    "overall_status": "approved",
    "issues": [],
    "suggestions": [],
    "summary": "Short review summary."
}}

If real problems exist:

{{
    "overall_status": "changes_requested",
    "issues": [
        "Specific issue"
    ],
    "suggestions": [
        "Optional improvement"
    ],
    "summary": "Short review summary."
}}
"""

    # ========================================================
    # CALL LLM
    # ========================================================

    try:

        # Code review needs a short response.
        # Keeping this at 1200 reduces provider
        # token usage and improves fallback reliability.

        response = invoke_llm(
            prompt,
            max_tokens=1200,
        )

        content = extract_text_from_response(
            response
        )

        content = clean_json_response(
            content
        )

        review = json.loads(
            content
        )

    except Exception as error:

        review_error = (
            f"Code reviewer unavailable: {error}"
        )

        print(
            f"⚠️ {review_error}"
        )

        # IMPORTANT:
        # Reviewer failure should NOT make the
        # generated project itself fail.

        return {
            **state,

            "review": {
                "overall_status": "unavailable",
                "issues": [],
                "suggestions": [],
                "summary": (
                    "AI code review was unavailable. "
                    "Automated project tests completed "
                    "separately."
                ),
                "project_id": project_id,
                "project_directory": str(
                    project_dir
                ),
                "error": review_error,
            },
        }

    # ========================================================
    # VALIDATE REVIEW STRUCTURE
    # ========================================================

    overall_status = review.get(
        "overall_status",
        "approved",
    )

    if overall_status not in {
        "approved",
        "changes_requested",
        "failed",
    }:

        overall_status = "approved"

    issues = review.get(
        "issues",
        [],
    )

    suggestions = review.get(
        "suggestions",
        [],
    )

    summary = review.get(
        "summary",
        "",
    )

    # --------------------------------------------------------
    # Normalize issues
    # --------------------------------------------------------

    if not isinstance(
        issues,
        list,
    ):

        issues = [
            str(issues)
        ]

    # --------------------------------------------------------
    # Normalize suggestions
    # --------------------------------------------------------

    if not isinstance(
        suggestions,
        list,
    ):

        suggestions = [
            str(suggestions)
        ]

    # --------------------------------------------------------
    # Normalize summary
    # --------------------------------------------------------

    if not isinstance(
        summary,
        str,
    ):

        summary = str(
            summary
        )

    # ========================================================
    # FINAL REVIEW
    # ========================================================

    final_review = {
        "overall_status": overall_status,

        "issues": issues,

        "suggestions": suggestions,

        "summary": summary,

        "project_id": project_id,

        "project_directory": str(
            project_dir
        ),
    }

    return {
        **state,

        "project_id": project_id,

        "review": final_review,
    }