import json

from services.llm import invoke_llm
from graph.state import ProjectState


def code_reviewer_agent(
    state: ProjectState
) -> ProjectState:


    tasks = state.get(
        "tasks",
        []
    )

    test_results = state.get(
        "test_results",
        {}
    )

    files = json.dumps(
        tasks,
        indent=2
    )

    prompt = f"""
You are the Code Reviewer Agent in an autonomous
software development team.

Review the generated source code.

GENERATED FILES:
{files}

TEST RESULTS:
{json.dumps(test_results, indent=2)}

Analyze the code for:

1. Code quality
2. Readability
3. Maintainability
4. Potential bugs
5. Security problems
6. Best practices
7. Unnecessary or duplicated code

Return ONLY valid JSON using exactly this structure:

{{
    "overall_status": "approved",
    "issues": [],
    "suggestions": [],
    "summary": "short review summary"
}}

Rules:

1. Do not modify the source files.
2. Do not use markdown code fences.
3. Do not add explanations outside the JSON.
4. Never generate API keys, passwords, or secrets.
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

        review = json.loads(content)

    except json.JSONDecodeError:

        review = {
            "overall_status": "review_failed",
            "issues": [
                "Code reviewer returned invalid JSON."
            ],
            "suggestions": [],
            "summary": content
        }

    print(
        "\n========== CODE REVIEWER OUTPUT =========="
    )

    print(
        json.dumps(
            review,
            indent=2
        )
    )

    print(
        "==========================================\n"
    )

    return {
        **state,
        "review": review
    }