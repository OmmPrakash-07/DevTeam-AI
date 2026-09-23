from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2] / "recent_projects"


def get_project_dir(project_id: str, create: bool = True) -> Path:
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

    base_dir = BASE_DIR.resolve()
    candidate = BASE_DIR / project_id

    # A project root must be its own directory, not a symlink that aliases
    # another project (or another location within the storage root).
    if candidate.is_symlink():
        raise ValueError("Project directory cannot be a symlink.")

    project_dir = candidate.resolve()

    # Project IDs are single path components, so the resolved directory must
    # remain a direct child of the storage root with the same name.
    if project_dir.parent != base_dir or project_dir.name != project_id:
        raise ValueError("Project directory is outside the allowed base directory.")

    if create:
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
