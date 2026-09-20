from fastapi import FastAPI, HTTPException

from graph.workflow import create_workflow


app = FastAPI(
    title="DevTeam AI",
    description="Multi-Agent Autonomous Software Development Team",
    version="1.0.0"
)


workflow = create_workflow()


@app.get("/")
def root():

    return {
        "message": "DevTeam AI is running 🚀"
    }


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

    initial_state = {
        "user_request": user_request,
        "debug_attempts": 0,
        "errors": []
    }

    result = workflow.invoke(
        initial_state
    )

    return {
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