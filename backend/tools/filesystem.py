from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2] / "generated_projects"


def get_project_dir(project_id: str) -> Path:
    """
    Return the isolated directory for a project.
    """

    if not project_id:
        raise ValueError("Project ID is required.")

    project_id = project_id.strip()

    # Only allow safe project IDs.
    if not project_id.startswith("project_"):
        raise ValueError(f"Invalid project ID: {project_id}")

    if "/" in project_id or "\\" in project_id:
        raise ValueError("Invalid project ID.")

    project_dir = (BASE_DIR / project_id).resolve()

    # Make sure the project directory stays inside BASE_DIR.
    try:
        project_dir.relative_to(BASE_DIR.resolve())
    except ValueError:
        raise ValueError("Project directory is outside the allowed base directory.")

    project_dir.mkdir(parents=True, exist_ok=True)

    return project_dir


def create_project_files(
    project_id: str,
    files: list[dict]
) -> list[str]:

    project_dir = get_project_dir(project_id)

    created_files = []

    for file in files:

        relative_path = file.get("path")
        content = file.get("content", "")

        if not relative_path:
            continue

        path = Path(relative_path)

        # Absolute paths are not allowed.
        if path.is_absolute():
            raise ValueError(
                f"Absolute paths are not allowed: {relative_path}"
            )

        target = (project_dir / path).resolve()

        # Prevent path traversal.
        try:
            target.relative_to(project_dir)
        except ValueError:
            raise ValueError(
                f"Path traversal is not allowed: {relative_path}"
            )

        target.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        target.write_text(
            content,
            encoding="utf-8"
        )

        created_files.append(
            str(target.relative_to(project_dir))
        )

    return created_files