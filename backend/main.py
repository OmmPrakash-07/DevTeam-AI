from fastapi import FastAPI

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

    user_request = request.get("request", "")

    initial_state = {
        "user_request": user_request
    }

    result = workflow.invoke(initial_state)

    return {
    "user_request": result.get("user_request"),
    "requirements": result.get("requirements", []),
    "architecture": result.get("architecture", {})
}