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
        project_manager_agent
    )

    graph.add_node(
        "architect",
        architect_agent
    )

    graph.add_node(
        "developer",
        developer_agent
    )

    graph.add_node(
        "filesystem",
        filesystem_agent
    )

    graph.add_node(
        "tester",
        tester_agent
    )

    graph.add_node(
        "debugger",
        debugger_agent
    )

    graph.add_node(
        "code_reviewer",
        code_reviewer_agent
    )

    graph.add_node(
        "documentation",
        documentation_agent
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