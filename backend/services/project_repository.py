"""Persistence boundary for generated-project metadata."""

from contextlib import closing
from datetime import datetime, timezone
import os
from pathlib import Path
import sqlite3
from typing import Protocol


DEFAULT_DATABASE_PATH = Path(__file__).resolve().parents[1] / "data" / "devteam_ai.sqlite3"


class ProjectRepository(Protocol):
    def initialize(self) -> None: ...

    def save_project(self, project: dict) -> None: ...

    def list_projects(self) -> list[dict]: ...


class SQLiteProjectRepository:
    """SQLite adapter; application code depends only on this repository API."""

    def __init__(self, database_path: Path | None = None):
        configured_path = os.getenv("DEVTEAM_DATABASE_PATH")
        self.database_path = Path(configured_path) if configured_path else (
            database_path or DEFAULT_DATABASE_PATH
        )

    def _connect(self):
        return sqlite3.connect(self.database_path, timeout=30)

    def initialize(self) -> None:
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        with closing(self._connect()) as connection:
            with connection:
                connection.execute(
                    """
                    CREATE TABLE IF NOT EXISTS projects (
                        project_id TEXT PRIMARY KEY,
                        user_request TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        updated_at TEXT NOT NULL,
                        status TEXT NOT NULL,
                        test_status TEXT,
                        file_count INTEGER NOT NULL DEFAULT 0
                    )
                    """
                )
                connection.execute(
                    "CREATE INDEX IF NOT EXISTS idx_projects_created_at "
                    "ON projects(created_at DESC)"
                )

    def save_project(self, project: dict) -> None:
        with closing(self._connect()) as connection:
            with connection:
                connection.execute(
                    """
                    INSERT INTO projects (
                        project_id, user_request, created_at, updated_at,
                        status, test_status, file_count
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(project_id) DO UPDATE SET
                        user_request = excluded.user_request,
                        updated_at = excluded.updated_at,
                        status = excluded.status,
                        test_status = excluded.test_status,
                        file_count = excluded.file_count
                    """,
                    (
                        project["project_id"],
                        project["user_request"],
                        project["created_at"],
                        project["updated_at"],
                        project["status"],
                        project.get("test_status"),
                        project["file_count"],
                    ),
                )

    def list_projects(self) -> list[dict]:
        with closing(self._connect()) as connection:
            connection.row_factory = sqlite3.Row
            rows = connection.execute(
                """
                SELECT project_id, user_request, created_at, updated_at,
                       status, test_status, file_count
                FROM projects
                ORDER BY created_at DESC, project_id DESC
                """
            ).fetchall()
        return [dict(row) for row in rows]


project_repository: ProjectRepository = SQLiteProjectRepository()


def utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()
