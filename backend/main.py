import asyncio
import json
import threading

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi import Query
from datetime import datetime
import uuid

from graph.workflow import create_workflow


app = FastAPI(
    title="DevTeam AI",
    description="Multi-Agent Autonomous Software Development Team",
    version="1.0.0"
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
    encoded_data = json.dumps(data, ensure_ascii=False)
    return f"event: {event_name}\ndata: {encoded_data}\n\n"


# --------------------------------------------------
# Root Endpoint
# --------------------------------------------------

@app.get("/")
def root():
    return {
        "message": "DevTeam AI is running 🚀"
    }


# --------------------------------------------------
# Generate Project
# --------------------------------------------------

@app.post("/generate")
def generate_project(request: dict):

    user_request = request.get(
        "request",
        ""
    ).strip()

    if not user_request:
        raise HTTPException(
            status_code=400,
            detail="Please provide a software request."
        )

    project_id = (
        f"project_"
        f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_"
        f"{uuid.uuid4().hex[:6]}"
    )

    initial_state = {
        "project_id": project_id,
        "user_request": user_request,
        "debug_attempts": 0,
        "errors": []
    }

    result = workflow.invoke(
        initial_state
    )

    return build_generate_response(result)


@app.get("/generate/stream")
async def generate_project_stream(request: str = Query(...)):
    user_request = request.strip()

    if not user_request:
        raise HTTPException(
            status_code=400,
            detail="Please provide a software request."
        )

    project_id = (
        f"project_"
        f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_"
        f"{uuid.uuid4().hex[:6]}"
    )

    initial_state = {
        "project_id": project_id,
        "user_request": user_request,
        "debug_attempts": 0,
        "errors": []
    }

    async def event_stream():
        loop = asyncio.get_running_loop()
        events = asyncio.Queue()
        disconnected = threading.Event()
        end_of_stream = object()

        def publish(item):
            if disconnected.is_set():
                return

            try:
                loop.call_soon_threadsafe(events.put_nowait, item)
            except RuntimeError:
                # The request's event loop has closed, so there is no client
                # left to receive events from this invocation.
                disconnected.set()

        def run_workflow_stream():
            final_state = None

            try:
                for mode, chunk in workflow.stream(
                    initial_state,
                    stream_mode=["custom", "values"],
                ):
                    if disconnected.is_set():
                        break

                    if mode == "custom":
                        publish(("activity", chunk))
                    elif mode == "values":
                        final_state = chunk

                if not disconnected.is_set():
                    if final_state is None:
                        raise RuntimeError("Workflow returned no final state.")

                    publish((
                        "complete",
                        build_generate_response(final_state),
                    ))
            except Exception:
                publish((
                    "error",
                    {"message": "An error occurred while generating the project."},
                ))
            finally:
                publish(end_of_stream)

        worker = asyncio.create_task(
            asyncio.to_thread(run_workflow_stream)
        )

        try:
            while True:
                item = await events.get()

                if item is end_of_stream:
                    break

                event_name, event_data = item
                yield format_sse_event(event_name, event_data)

                if event_name in {"complete", "error"}:
                    break
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
