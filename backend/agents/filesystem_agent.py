from graph.state import ProjectState
from tools.filesystem import create_project_files


def filesystem_agent(state: ProjectState):

    project_id = state.get("project_id")

    if not project_id:
        raise ValueError("Project ID is missing from project state.")

    tasks = state.get("tasks", [])

    files = []

    for task in tasks:

        path = task.get("path")
        content = task.get("content", "")

        if not path:
            continue

        # Remove generated_project/ prefix if the Developer added it.
        if path.startswith("generated_project/"):
            path = path[len("generated_project/"):]

        files.append({
            "path": path,
            "content": content
        })

    created_files = create_project_files(
        project_id,
        files
    )

    return {
        "project_id": project_id,
        "generated_files": created_files
    }