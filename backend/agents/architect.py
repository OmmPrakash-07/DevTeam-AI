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

Return ONLY valid JSON with this structure:

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

Do not include markdown or ```json.
"""

    response = llm.invoke(prompt)

    architecture_text = response.content.strip()

    return {
        **state,
        "architecture": {
            "raw": architecture_text
        }
    }