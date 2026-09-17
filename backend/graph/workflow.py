from langgraph.graph import StateGraph, START, END

from graph.state import ProjectState
from agents.project_manager import project_manager_agent


def create_workflow():

    graph = StateGraph(ProjectState)

    graph.add_node(
        "project_manager",
        project_manager_agent
    )

    graph.add_edge(
        START,
        "project_manager"
    )

    graph.add_edge(
        "project_manager",
        END
    )

    return graph.compile()