from services.llm import invoke_llm
from graph.state import ProjectState


def project_manager_agent(state: ProjectState) -> ProjectState:


    prompt = f"""
You are the Project Manager Agent of an autonomous
software development team.

Analyze the user's software request.

User request:
{state["user_request"]}

Extract the main software requirements.

Return ONLY a numbered list of concise requirements.
"""

    response = invoke_llm(prompt)

    # Gemini may return content as a list of content blocks.
    if isinstance(response.content, list):
        content = "\n".join(
            str(block.get("text", block))
            if isinstance(block, dict)
            else str(block)
            for block in response.content
        )
    else:
        content = str(response.content)

    requirements = []

    for line in content.splitlines():

        line = line.strip()

        if line:
            cleaned = line.lstrip("0123456789.- ").strip()

            if cleaned:
                requirements.append(cleaned)

    return {
        **state,
        "requirements": requirements
    }