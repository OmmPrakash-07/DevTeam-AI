from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
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

    return {
        "project_id": result.get(
            "project_id"
        ),

        "user_request": result.get(
            "user_request"
        ),

        "requirements": result.get(
            "requirements",
            []
        ),

        "architecture": result.get(
            "architecture",
            {}
        ),

        "generated_files": result.get(
            "generated_files",
            []
        ),

        "tasks": result.get(
            "tasks",
            []
        ),

        "test_results": result.get(
            "test_results",
            {}
        ),

        "review": result.get(
            "review",
            {}
        ),

        "debug_attempts": result.get(
            "debug_attempts",
            0
        )
    }