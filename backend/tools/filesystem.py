from pathlib import Path

from graph.state import ProjectState


BASE_DIR = (
    Path(__file__).resolve().parents[2] / "generated_projects"
)


def create_project_files(
    project_name: str,
    files: list[dict]
) -> list[str]:

    project_dir = BASE_DIR / project_name

    project_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    created_files = []

    for file in files:

        if not isinstance(file, dict):
            continue

        relative_path = file.get("path")
        content = file.get("content", "")

        if not relative_path:
            continue

        path = Path(relative_path)

        # Prevent absolute paths
        if path.is_absolute():
            raise ValueError(
                f"Absolute paths are not allowed: {relative_path}"
            )

        # Prevent path traversal
        target = (project_dir / path).resolve()

        try:
            target.relative_to(project_dir.resolve())
        except ValueError:
            raise ValueError(
                f"Path traversal is not allowed: {relative_path}"
            )

        # Create parent directories
        target.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        # Write file
        target.write_text(
            str(content),
            encoding="utf-8"
        )

        created_files.append(
            str(target.relative_to(BASE_DIR))
        )

    return created_files


def filesystem_agent(state: ProjectState) -> ProjectState:

    tasks = state.get("tasks", [])

    if not tasks:
        raise RuntimeError(
            "File System Agent received no files from Developer Agent."
        )

    print("\n========== FILE SYSTEM AGENT ==========")

    created_files = create_project_files(
        "generated_project",
        tasks
    )

    print(f"✅ Created {len(created_files)} files:")

    for file_path in created_files:
        print(f"   📄 {file_path}")

    print("=======================================\n")

    return {
        **state,
        "generated_files": created_files
    }