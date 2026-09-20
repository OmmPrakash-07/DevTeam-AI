from langgraph.graph import StateGraph, START, END

from graph.state import ProjectState
from agents.project_manager import project_manager_agent
from agents.architect import architect_agent
from agents.developer import developer_agent
from agents.filesystem_agent import filesystem_agent
from agents.tester import tester_agent


def create_workflow():

    graph = StateGraph(ProjectState)

    # Agents
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

    # Workflow
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

    graph.add_edge(
        "tester",
        END
    )

    return graph.compile()