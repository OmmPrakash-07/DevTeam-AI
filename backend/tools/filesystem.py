from pathlib import Path


BASE_DIR = (
    Path(__file__).resolve().parents[2] / "generated_projects"
)


def create_project_files(
    project_name: str,
    files: list[dict]
) -> list[str]:

    project_dir = BASE_DIR / project_name

    # Create project directory
    project_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    created_files = []

    for file in files:

        relative_path = file.get("path")
        content = file.get("content", "")

        if not relative_path:
            continue

        # Prevent absolute paths
        path = Path(relative_path)

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
            content,
            encoding="utf-8"
        )

        created_files.append(
            str(target.relative_to(BASE_DIR))
        )

    return created_files