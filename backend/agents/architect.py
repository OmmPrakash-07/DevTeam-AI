import json

from services.llm import get_llm
from graph.state import ProjectState


def architect_agent(state: ProjectState) -> ProjectState:

    llm = get_llm()

    requirements = "\n".join(
        f"- {req}"
        for req in state.get("requirements", [])
    )

    prompt = f"""
You are the Software Architect Agent in an autonomous
software development team.

The Project Manager identified these requirements:

{requirements}

Design a technical architecture for the project.

Return ONLY valid JSON.

Use exactly this structure:

{{
    "project_type": "full-stack web application",
    "frontend": {{
        "technology": "",
        "responsibilities": []
    }},
    "backend": {{
        "technology": "",
        "responsibilities": []
    }},
    "database": {{
        "technology": "",
        "collections_or_tables": []
    }},
    "authentication": "",
    "api_style": "",
    "folder_structure": []
}}

Do not include markdown.
Do not use ```json.
Do not add explanations outside the JSON.
"""

    response = llm.invoke(prompt)

    # Gemini may return content as a list of blocks
    if isinstance(response.content, list):

        architecture_text = "\n".join(
            str(block.get("text", block))
            if isinstance(block, dict)
            else str(block)
            for block in response.content
        )

    else:

        architecture_text = str(response.content)

    architecture_text = architecture_text.strip()

    print("\n========== ARCHITECT OUTPUT ==========")
    print(architecture_text)
    print("======================================\n")

    # Remove markdown code fences if Gemini adds them
    if architecture_text.startswith("```json"):

        architecture_text = architecture_text[
            len("```json"):
        ].strip()

    if architecture_text.startswith("```"):

        architecture_text = architecture_text[
            len("```"):
        ].strip()

    if architecture_text.endswith("```"):

        architecture_text = architecture_text[
            :-len("```")
        ].strip()

    # Convert JSON text into Python dictionary
    try:

        architecture = json.loads(
            architecture_text
        )

    except json.JSONDecodeError:

        architecture = {
            "raw": architecture_text
        }

    return {
        **state,
        "architecture": architecture
    }