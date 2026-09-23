from datetime import datetime, timezone

from langgraph.graph import (
    StateGraph,
    START,
    END,
)

from graph.state import ProjectState
from agents.project_manager import project_manager_agent
from agents.architect import architect_agent
from agents.developer import developer_agent
from agents.filesystem_agent import filesystem_agent
from agents.tester import tester_agent
from agents.debugger import debugger_agent
from agents.code_reviewer import code_reviewer_agent
from agents.documentation import documentation_agent


AGENT_DETAILS = {
    "project_manager": ("Project Manager", "Project Manager is working..."),
    "architect": ("Architect", "Architect is designing the project..."),
    "developer": ("Developer", "Developer is generating the project code..."),
    "filesystem": ("File System", "File System is creating project files..."),
    "tester": ("Tester", "Tester is validating the project..."),
    "debugger": ("Debugger", "Debugger is analyzing and fixing failures..."),
    "code_reviewer": ("Code Reviewer", "Code Reviewer is reviewing the project..."),
    "documentation": ("Documentation", "Documentation is being generated..."),
}


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def _record_activity(state: ProjectState, event: dict) -> None:
    """Append an activity event to the current state history."""
    history = state.setdefault("activity_history", [])
    history.append(event)


def _with_activity(agent_name: str, agent):
    """Wrap a workflow node with running, completion, and failure events."""
    display_name, running_message = AGENT_DETAILS[agent_name]

    def tracked_agent(state: ProjectState) -> ProjectState:
        attempt_number = None
        if agent_name == "debugger":
            attempt_number = state.get("debug_attempts", 0) + 1
        elif agent_name == "tester":
            attempt_number = state.get("debug_attempts", 0) + 1

        event_fields = {
            "agent_name": agent_name,
            "display_name": display_name,
        }
        if attempt_number is not None:
            event_fields["attempt_number"] = attempt_number

        running_event = {
            **event_fields,
            "status": "running",
            "message": running_message,
            "timestamp": _timestamp(),
        }
        _record_activity(state, running_event)
        state["current_active_agent"] = agent_name

        try:
            result = agent(state)
        except Exception as error:
            _record_activity(state, {
                **event_fields,
                "status": "failed",
                "message": f"{display_name} failed: {error}",
                "timestamp": _timestamp(),
            })
            state["current_active_agent"] = None
            raise

        result = {**state, **result}
        completion_status = "completed"
        completion_message = f"{display_name} completed successfully."

        if agent_name == "tester":
            test_status = result.get("test_results", {}).get("status")
            if test_status == "failed":
                completion_status = "failed"
                completion_message = "Tester completed; project tests failed."
            else:
                completion_message = "Tester completed; project tests passed."

        result.setdefault("activity_history", []).append({
            **event_fields,
            "status": completion_status,
            "message": completion_message,
            "timestamp": _timestamp(),
        })
        result["current_active_agent"] = None
        return result

    return tracked_agent


# ============================================================
# TESTER DECISION
# ============================================================

def should_debug(state: ProjectState):
    test_results = state.get("test_results", {})
    debug_attempts = state.get("debug_attempts", 0)

    status = test_results.get("status")

    print("\n========== WORKFLOW DECISION ==========")
    print(f"Test status: {status}")
    print(f"Debug attempts: {debug_attempts}")

    # --------------------------------------------------------
    # Tests passed → go directly to Code Reviewer
    # --------------------------------------------------------

    if status == "passed":
        print("✅ Tests passed → Code Reviewer")
        print("======================================\n")
        return "reviewer"

    # --------------------------------------------------------
    # Maximum debugging attempts reached
    # --------------------------------------------------------

    if debug_attempts >= 3:
        print("⚠️ Maximum debugging attempts reached → Code Reviewer")
        print("======================================\n")
        return "reviewer"

    # --------------------------------------------------------
    # Tests failed → Debugger
    # --------------------------------------------------------

    print("❌ Tests failed → Debugger")
    print("======================================\n")

    return "debugger"


# ============================================================
# CREATE WORKFLOW
# ============================================================

def create_workflow():

    graph = StateGraph(ProjectState)

    # ========================================================
    # AGENTS
    # ========================================================

    graph.add_node(
        "project_manager",
        _with_activity("project_manager", project_manager_agent)
    )

    graph.add_node(
        "architect",
        _with_activity("architect", architect_agent)
    )

    graph.add_node(
        "developer",
        _with_activity("developer", developer_agent)
    )

    graph.add_node(
        "filesystem",
        _with_activity("filesystem", filesystem_agent)
    )

    graph.add_node(
        "tester",
        _with_activity("tester", tester_agent)
    )

    graph.add_node(
        "debugger",
        _with_activity("debugger", debugger_agent)
    )

    graph.add_node(
        "code_reviewer",
        _with_activity("code_reviewer", code_reviewer_agent)
    )

    graph.add_node(
        "documentation",
        _with_activity("documentation", documentation_agent)
    )

    # ========================================================
    # MAIN PIPELINE
    # ========================================================

    graph.add_edge(
        START,
        "project_manager"
    )

    graph.add_edge(
        "project_manager",
        "architect"
    )

    graph.add_edge(
        "architect",
        "developer"
    )

    graph.add_edge(
        "developer",
        "filesystem"
    )

    graph.add_edge(
        "filesystem",
        "tester"
    )

    # ========================================================
    # TESTER → DEBUGGER / REVIEWER
    # ========================================================

    graph.add_conditional_edges(
        "tester",
        should_debug,
        {
            "debugger": "debugger",
            "reviewer": "code_reviewer",
        }
    )

    # ========================================================
    # DEBUGGER → TESTER
    # ========================================================

    graph.add_edge(
        "debugger",
        "tester"
    )

    # ========================================================
    # REVIEWER → DOCUMENTATION
    # ========================================================

    graph.add_edge(
        "code_reviewer",
        "documentation"
    )

    # ========================================================
    # DOCUMENTATION → END
    # ========================================================

    graph.add_edge(
        "documentation",
        END
    )

    return graph.compile()
