"""Persistence boundary for generated projects and assistant conversation history."""

from contextlib import closing
from datetime import datetime, timezone
import os
from pathlib import Path
import sqlite3
from typing import Protocol


DEFAULT_DATABASE_PATH = (
    Path(__file__).resolve().parents[1] / "data" / "devteam_ai.sqlite3"
)


class ProjectRepository(Protocol):
    def initialize(self) -> None: ...

    # Project persistence
    def save_project(self, project: dict) -> None: ...

    def list_projects(self) -> list[dict]: ...

    # Conversation history persistence
    def save_history(self, history: dict) -> None: ...

    def list_history(self) -> list[dict]: ...

    def get_history(self, history_id: str) -> dict | None: ...

    def delete_history(self, history_id: str) -> bool: ...


class SQLiteProjectRepository:
    """SQLite adapter for projects and assistant conversation history."""

    def __init__(self, database_path: Path | None = None):
        configured_path = os.getenv("DEVTEAM_DATABASE_PATH")

        self.database_path = (
            Path(configured_path)
            if configured_path
            else (database_path or DEFAULT_DATABASE_PATH)
        )

    def _connect(self):
        return sqlite3.connect(self.database_path, timeout=30)

    def initialize(self) -> None:
        self.database_path.parent.mkdir(parents=True, exist_ok=True)

        with closing(self._connect()) as connection:
            with connection:
                # --------------------------------------------------
                # Generated projects
                # --------------------------------------------------

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
                    """
                    CREATE INDEX IF NOT EXISTS idx_projects_created_at
                    ON projects(created_at DESC)
                    """
                )

                # --------------------------------------------------
                # Assistant conversation history
                # --------------------------------------------------

                connection.execute(
                    """
                    CREATE TABLE IF NOT EXISTS history (
                        history_id TEXT PRIMARY KEY,
                        user_request TEXT NOT NULL,
                        intent TEXT NOT NULL,
                        answer TEXT NOT NULL,
                        created_at TEXT NOT NULL
                    )
                    """
                )

                connection.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_history_created_at
                    ON history(created_at DESC)
                    """
                )

    # ==============================================================
    # PROJECT PERSISTENCE
    # ==============================================================

    def save_project(self, project: dict) -> None:
        with closing(self._connect()) as connection:
            with connection:
                connection.execute(
                    """
                    INSERT INTO projects (
                        project_id,
                        user_request,
                        created_at,
                        updated_at,
                        status,
                        test_status,
                        file_count
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?)

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
                SELECT
                    project_id,
                    user_request,
                    created_at,
                    updated_at,
                    status,
                    test_status,
                    file_count
                FROM projects
                ORDER BY created_at DESC, project_id DESC
                """
            ).fetchall()

        return [dict(row) for row in rows]

    # ==============================================================
    # CONVERSATION HISTORY
    # ==============================================================

    def save_history(self, history: dict) -> None:
        """
        Save a normal assistant conversation.

        This table is intentionally separate from `projects`.
        ANSWER and CODING_HELP requests should use this method and
        must never create a project record.
        """

        with closing(self._connect()) as connection:
            with connection:
                connection.execute(
                    """
                    INSERT INTO history (
                        history_id,
                        user_request,
                        intent,
                        answer,
                        created_at
                    )
                    VALUES (?, ?, ?, ?, ?)

                    ON CONFLICT(history_id) DO UPDATE SET
                        user_request = excluded.user_request,
                        intent = excluded.intent,
                        answer = excluded.answer
                    """,
                    (
                        history["history_id"],
                        history["user_request"],
                        history["intent"],
                        history["answer"],
                        history["created_at"],
                    ),
                )

    def list_history(self) -> list[dict]:
        """Return conversation history newest first."""

        with closing(self._connect()) as connection:
            connection.row_factory = sqlite3.Row

            rows = connection.execute(
                """
                SELECT
                    history_id,
                    user_request,
                    intent,
                    answer,
                    created_at
                FROM history
                ORDER BY created_at DESC, history_id DESC
                """
            ).fetchall()

        return [dict(row) for row in rows]

    def get_history(self, history_id: str) -> dict | None:
        """Return one history entry by ID."""

        with closing(self._connect()) as connection:
            connection.row_factory = sqlite3.Row

            row = connection.execute(
                """
                SELECT
                    history_id,
                    user_request,
                    intent,
                    answer,
                    created_at
                FROM history
                WHERE history_id = ?
                """,
                (history_id,),
            ).fetchone()

        return dict(row) if row else None

    def delete_history(self, history_id: str) -> bool:
        """Delete one conversation history entry."""

        with closing(self._connect()) as connection:
            with connection:
                cursor = connection.execute(
                    """
                    DELETE FROM history
                    WHERE history_id = ?
                    """,
                    (history_id,),
                )

                return cursor.rowcount > 0


# ==============================================================
# Shared repository instance
# ==============================================================

project_repository: ProjectRepository = SQLiteProjectRepository()


def utc_timestamp() -> str:
    """Return the current UTC timestamp in ISO-8601 format."""

    return datetime.now(timezone.utc).isoformat()