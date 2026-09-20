from graph.state import ProjectState
from tools.filesystem import create_project_files


def filesystem_agent(
    state: ProjectState
) -> ProjectState:

    files = state.get("tasks", [])

    if not files:
        return {
            **state,
            "generated_files": []
        }

    project_name = "generated_project"

    created_files = create_project_files(
        project_name,
        files
    )

    return {
        **state,
        "generated_files": created_files
    }