import asyncio
import io
import json
import os
import re
import threading
import uuid
import zipfile
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, StreamingResponse

from graph.workflow import create_workflow
from services.intent import (
    ALLOWED_INTENTS,
    classify_intent,
    generate_assistant_response,
)
from services.project_repository import project_repository, utc_timestamp
from services.model_manager import get_available_models
from tools.filesystem import get_project_dir


# --------------------------------------------------
# Application Lifespan
# --------------------------------------------------


@asynccontextmanager
async def app_lifespan(_app):
    project_repository.initialize()
    yield


# --------------------------------------------------
# FastAPI Application
# --------------------------------------------------


app = FastAPI(
    title="DevTeam AI",
    description="Multi-Agent Autonomous Software Development Team",
    version="1.0.0",
    lifespan=app_lifespan,
)


# --------------------------------------------------
# CORS Configuration
# --------------------------------------------------


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "https://devteam-ai.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------
# Workflow
# --------------------------------------------------


workflow = create_workflow()


# --------------------------------------------------
# Model Catalogue
# --------------------------------------------------


@app.get("/models")
def list_models():
    """
    Return all configured AI providers and their available models.

    This endpoint is used by the frontend model selector.
    """
    return {
        "providers": get_available_models()
    }


# --------------------------------------------------
# Response Helpers
# --------------------------------------------------


def build_generate_response(result: dict) -> dict:
    """Build the response shared by the regular and streaming endpoints."""

    return {
        "project_id": result.get("project_id"),
        "user_request": result.get("user_request"),
        "requirements": result.get("requirements", []),
        "architecture": result.get("architecture", {}),
        "generated_files": result.get("generated_files", []),
        "tasks": result.get("tasks", []),
        "test_results": result.get("test_results", {}),
        "review": result.get("review", {}),
        "debug_attempts": result.get("debug_attempts", 0),
        "activity_history": result.get("activity_history", []),
        "current_active_agent": result.get("current_active_agent"),
    }


def format_sse_event(event_name: str, data: dict) -> str:
    encoded_data = json.dumps(
        data,
        ensure_ascii=False,
    )

    return (
        f"event: {event_name}\n"
        f"data: {encoded_data}\n\n"
    )


# --------------------------------------------------
# History Persistence
# --------------------------------------------------


_HISTORY_ID_PATTERN = re.compile(
    r"history_[A-Za-z0-9_-]+\Z"
)


def create_history_id() -> str:
    """Create a unique identifier for an assistant conversation."""

    return (
        f"history_"
        f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_"
        f"{uuid.uuid4().hex[:6]}"
    )


def persist_history_entry(
    user_request: str,
    intent: str,
    answer: str,
) -> dict:
    """
    Persist a normal ANSWER or CODING_HELP interaction.

    These entries are intentionally stored separately
    from generated software projects.
    """

    history_id = create_history_id()
    created_at = utc_timestamp()

    history = {
        "history_id": history_id,
        "user_request": user_request,
        "intent": intent,
        "answer": answer,
        "created_at": created_at,
    }

    project_repository.save_history(history)

    return history


def resolve_history_id(history_id: str) -> str:
    """Validate a history ID before querying the repository."""

    if not _HISTORY_ID_PATTERN.fullmatch(history_id):
        raise HTTPException(
            status_code=400,
            detail="Invalid history ID.",
        )

    return history_id


# --------------------------------------------------
# Project Persistence
# --------------------------------------------------


def persist_completed_project(
    result: dict,
    created_at: str,
) -> dict:
    project_id = result.get("project_id")
    user_request = result.get("user_request")

    project_dir = get_project_dir(
        project_id,
        create=False,
    )

    if not project_dir.is_dir() or not user_request:
        raise ValueError(
            "Completed project data is unavailable."
        )

    test_results = result.get("test_results") or {}

    metadata = {
        "project_id": project_id,
        "user_request": user_request,
        "created_at": created_at,
        "updated_at": utc_timestamp(),
        "status": "completed",
        "test_status": test_results.get("status"),
        "file_count": len(
            list(iter_project_files(project_dir))
        ),
    }

    project_repository.save_project(metadata)

    return metadata


# --------------------------------------------------
# Project Validation
# --------------------------------------------------


_PROJECT_ID_PATTERN = re.compile(
    r"project_[A-Za-z0-9_-]+\Z"
)


def resolve_existing_project_dir(
    project_id: str,
) -> Path:
    if not _PROJECT_ID_PATTERN.fullmatch(project_id):
        raise HTTPException(
            status_code=400,
            detail="Invalid project ID.",
        )

    try:
        project_dir = get_project_dir(
            project_id,
            create=False,
        )
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Invalid project ID.",
        ) from None

    if not project_dir.is_dir():
        raise HTTPException(
            status_code=404,
            detail="Project not found.",
        )

    return project_dir


def iter_project_files(project_dir: Path):
    """
    Yield resolved regular files that remain inside
    the project directory.
    """

    root = project_dir.resolve(
        strict=True
    )

    def raise_walk_error(error):
        raise error

    for current_dir, directory_names, file_names in os.walk(
        root,
        onerror=raise_walk_error,
        followlinks=False,
    ):
        current_path = Path(current_dir)

        directory_names[:] = sorted(
            name
            for name in directory_names
            if not (
                current_path / name
            ).is_symlink()
        )

        for file_name in sorted(file_names):
            candidate = (
                current_path / file_name
            )

            if candidate.is_symlink():
                continue

            resolved_file = candidate.resolve(
                strict=True
            )

            try:
                relative_path = (
                    resolved_file.relative_to(root)
                )
            except ValueError:
                continue

            if resolved_file.is_file():
                yield (
                    resolved_file,
                    relative_path.as_posix(),
                )


# --------------------------------------------------
# Root Endpoint
# --------------------------------------------------


@app.get("/")
def root():
    return {
        "message": "DevTeam AI is running 🚀"
    }


# --------------------------------------------------
# Generate
# --------------------------------------------------


@app.post("/generate")
def generate_project(request: dict):
    user_request = request.get(
        "request",
        "",
    ).strip()

    if not user_request:
        raise HTTPException(
            status_code=400,
            detail="Please provide a software request.",
        )

    # --------------------------------------------------
    # Intent Classification
    # --------------------------------------------------

    try:
        intent = classify_intent(
            user_request
        )
    except Exception:
        raise HTTPException(
            status_code=503,
            detail=(
                "Unable to classify this request "
                "right now."
            ),
        ) from None

    # --------------------------------------------------
    # Normal Answer / Coding Help
    # --------------------------------------------------

    if intent in {
        "ANSWER",
        "CODING_HELP",
    }:
        try:
            answer = generate_assistant_response(
                user_request,
                intent,
            )
        except Exception:
            raise HTTPException(
                status_code=503,
                detail=(
                    "Unable to answer this request "
                    "right now."
                ),
            ) from None

        # IMPORTANT:
        # Normal questions and coding-help requests
        # are saved ONLY in History.
        #
        # They do NOT create:
        # - project IDs
        # - project folders
        # - project records

        try:
            history = persist_history_entry(
                user_request=user_request,
                intent=intent,
                answer=answer,
            )
        except Exception:
            raise HTTPException(
                status_code=500,
                detail=(
                    "Unable to save conversation "
                    "history."
                ),
            ) from None

        return {
            "intent": intent,
            "user_request": user_request,
            "answer": answer,
            "history_id": history[
                "history_id"
            ],
            "created_at": history[
                "created_at"
            ],
        }

    # --------------------------------------------------
    # Validate Project Intent
    # --------------------------------------------------

    if intent not in ALLOWED_INTENTS:
        raise HTTPException(
            status_code=400,
            detail="Unsupported request intent.",
        )

    # --------------------------------------------------
    # Create Project
    # --------------------------------------------------

    project_id = (
        f"project_"
        f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_"
        f"{uuid.uuid4().hex[:6]}"
    )

    created_at = utc_timestamp()

    initial_state = {
        "project_id": project_id,
        "user_request": user_request,
        "debug_attempts": 0,
        "errors": [],
    }

    # --------------------------------------------------
    # Run Multi-Agent Workflow
    # --------------------------------------------------

    result = workflow.invoke(
        initial_state
    )

    # --------------------------------------------------
    # Persist Completed Project
    # --------------------------------------------------

    try:
        persist_completed_project(
            result,
            created_at,
        )
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Unable to save project history.",
        ) from None

    # --------------------------------------------------
    # Return Project Response
    # --------------------------------------------------

    return {
        **build_generate_response(
            result
        ),
        "intent": "BUILD_PROJECT",
    }


# --------------------------------------------------
# Generate Stream
# --------------------------------------------------


@app.get("/generate/stream")
async def generate_project_stream(
    request: str = Query(...),
):
    user_request = request.strip()

    if not user_request:
        raise HTTPException(
            status_code=400,
            detail="Please provide a software request.",
        )

    async def event_stream():
        loop = asyncio.get_running_loop()

        events = asyncio.Queue()

        disconnected = threading.Event()

        end_of_stream = object()

        def publish(item):
            if disconnected.is_set():
                return

            try:
                loop.call_soon_threadsafe(
                    events.put_nowait,
                    item,
                )
            except RuntimeError:
                disconnected.set()

        def run_workflow_stream():
            try:
                # --------------------------------------------------
                # Intent Classification
                # --------------------------------------------------

                try:
                    intent = classify_intent(
                        user_request
                    )
                except Exception:
                    publish(
                        (
                            "error",
                            {
                                "message": (
                                    "Unable to classify this "
                                    "request right now."
                                )
                            },
                        )
                    )
                    return

                if disconnected.is_set():
                    return

                publish(
                    (
                        "intent",
                        {
                            "intent": intent,
                        },
                    )
                )

                # --------------------------------------------------
                # Normal Answer / Coding Help
                # --------------------------------------------------

                if intent in {
                    "ANSWER",
                    "CODING_HELP",
                }:
                    try:
                        answer = (
                            generate_assistant_response(
                                user_request,
                                intent,
                            )
                        )
                    except Exception:
                        publish(
                            (
                                "error",
                                {
                                    "message": (
                                        "Unable to answer this "
                                        "request right now."
                                    )
                                },
                            )
                        )
                        return

                    # Save normal conversations
                    # ONLY in History.

                    try:
                        history = persist_history_entry(
                            user_request=user_request,
                            intent=intent,
                            answer=answer,
                        )
                    except Exception:
                        publish(
                            (
                                "error",
                                {
                                    "message": (
                                        "Unable to save conversation "
                                        "history."
                                    )
                                },
                            )
                        )
                        return

                    if not disconnected.is_set():
                        publish(
                            (
                                "response",
                                {
                                    "intent": intent,
                                    "user_request": user_request,
                                    "answer": answer,
                                    "history_id": history[
                                        "history_id"
                                    ],
                                    "created_at": history[
                                        "created_at"
                                    ],
                                },
                            )
                        )

                    return

                # --------------------------------------------------
                # Validate Project Intent
                # --------------------------------------------------

                if intent != "BUILD_PROJECT":
                    publish(
                        (
                            "error",
                            {
                                "message": (
                                    "Unable to classify this "
                                    "request right now."
                                )
                            },
                        )
                    )
                    return

                # --------------------------------------------------
                # Create Project
                # --------------------------------------------------

                project_id = (
                    f"project_"
                    f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_"
                    f"{uuid.uuid4().hex[:6]}"
                )

                created_at = utc_timestamp()

                initial_state = {
                    "project_id": project_id,
                    "user_request": user_request,
                    "debug_attempts": 0,
                    "errors": [],
                }

                final_state = None

                # --------------------------------------------------
                # Stream Workflow
                # --------------------------------------------------

                for mode, chunk in workflow.stream(
                    initial_state,
                    stream_mode=[
                        "custom",
                        "values",
                    ],
                ):
                    if disconnected.is_set():
                        break

                    if mode == "custom":
                        publish(
                            (
                                "activity",
                                chunk,
                            )
                        )

                    elif mode == "values":
                        final_state = chunk

                # --------------------------------------------------
                # Persist Completed Project
                # --------------------------------------------------

                if not disconnected.is_set():
                    if final_state is None:
                        raise RuntimeError(
                            "Workflow returned no final state."
                        )

                    persist_completed_project(
                        final_state,
                        created_at,
                    )

                    publish(
                        (
                            "complete",
                            {
                                **build_generate_response(
                                    final_state
                                ),
                                "intent": "BUILD_PROJECT",
                            },
                        )
                    )

            except Exception:
                publish(
                    (
                        "error",
                        {
                            "message": (
                                "An error occurred while "
                                "generating the project."
                            )
                        },
                    )
                )

            finally:
                publish(
                    end_of_stream
                )

        # --------------------------------------------------
        # Run Workflow in Background Thread
        # --------------------------------------------------

        worker = asyncio.create_task(
            asyncio.to_thread(
                run_workflow_stream
            )
        )

        try:
            while True:
                item = await events.get()

                if item is end_of_stream:
                    break

                event_name, event_data = item

                yield format_sse_event(
                    event_name,
                    event_data,
                )

        finally:
            disconnected.set()

            if worker.done():
                await worker

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


# --------------------------------------------------
# History
# --------------------------------------------------


@app.get("/history")
def list_history():
    """
    Return saved ANSWER and CODING_HELP conversations.

    Generated software projects are intentionally excluded.
    """

    try:
        return {
            "history": (
                project_repository.list_history()
            )
        }
    except Exception:
        raise HTTPException(
            status_code=500,
            detail=(
                "Unable to load conversation history."
            ),
        ) from None


@app.get("/history/{history_id}")
def get_history(
    history_id: str,
):
    """Return a single saved conversation."""

    history_id = resolve_history_id(
        history_id
    )

    try:
        history = (
            project_repository.get_history(
                history_id
            )
        )
    except Exception:
        raise HTTPException(
            status_code=500,
            detail=(
                "Unable to load conversation history."
            ),
        ) from None

    if history is None:
        raise HTTPException(
            status_code=404,
            detail="History entry not found.",
        )

    return history


@app.delete("/history/{history_id}")
def delete_history(
    history_id: str,
):
    """Delete a single saved conversation."""

    history_id = resolve_history_id(
        history_id
    )

    try:
        deleted = (
            project_repository.delete_history(
                history_id
            )
        )
    except Exception:
        raise HTTPException(
            status_code=500,
            detail=(
                "Unable to delete conversation "
                "history."
            ),
        ) from None

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="History entry not found.",
        )

    return {
        "message": (
            "History entry deleted successfully."
        ),
        "history_id": history_id,
    }


# --------------------------------------------------
# Projects
# --------------------------------------------------


@app.get("/projects")
def list_projects():
    try:
        return {
            "projects": (
                project_repository.list_projects()
            )
        }
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Unable to load recent projects.",
        ) from None


# --------------------------------------------------
# Project Files
# --------------------------------------------------


@app.get("/projects/{project_id}")
def get_project_files(
    project_id: str,
):
    project_dir = resolve_existing_project_dir(
        project_id
    )

    try:
        files = []

        for file_path, relative_path in iter_project_files(
            project_dir
        ):
            content_bytes = file_path.read_bytes()

            is_binary = (
                b"\x00" in content_bytes
            )

            if is_binary:
                content = None

            else:
                try:
                    content = content_bytes.decode(
                        "utf-8"
                    )
                except UnicodeDecodeError:
                    content = None
                    is_binary = True

            files.append(
                {
                    "path": relative_path,
                    "content": content,
                    "is_binary": is_binary,
                }
            )

        return {
            "project_id": project_id,
            "files": files,
        }

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Unable to read project files.",
        ) from None


# --------------------------------------------------
# Project Download
# --------------------------------------------------


@app.get(
    "/projects/{project_id}/download"
)
def download_project(
    project_id: str,
):
    project_dir = resolve_existing_project_dir(
        project_id
    )

    try:
        archive_buffer = io.BytesIO()

        with zipfile.ZipFile(
            archive_buffer,
            mode="w",
            compression=zipfile.ZIP_DEFLATED,
        ) as archive:

            for file_path, relative_path in iter_project_files(
                project_dir
            ):
                archive.write(
                    file_path,
                    arcname=relative_path,
                )

        return Response(
            content=archive_buffer.getvalue(),
            media_type="application/zip",
            headers={
                "Content-Disposition": (
                    f'attachment; filename="{project_id}.zip"'
                ),
            },
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Unable to create project download.",
        ) from None