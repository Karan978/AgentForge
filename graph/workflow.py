from langgraph.graph import (
    StateGraph,
    END,
)

from graph.state import AgentState

from agents.analyst import software_analyst
from agents.developer import developer
from agents.qa import qa_reviewer


MAX_ITERATIONS = 3


def route_after_qa(
    state: AgentState,
) -> str:

    # ---------------------------------------------------------
    # Successful implementation
    # ---------------------------------------------------------

    if (
        state.get("tests_passed", False)
        and state.get("review_passed", False)
    ):
        return "finish"

    # ---------------------------------------------------------
    # Prevent infinite loops
    # ---------------------------------------------------------

    if state.get(
        "iteration",
        0,
    ) >= MAX_ITERATIONS:

        return "finish"

    # ---------------------------------------------------------
    # Developer needs another attempt
    # ---------------------------------------------------------

    return "developer"


def build_graph():

    workflow = StateGraph(
        AgentState
    )

    # ---------------------------------------------------------
    # Nodes
    # ---------------------------------------------------------

    workflow.add_node(
        "analyst",
        software_analyst,
    )

    workflow.add_node(
        "developer",
        developer,
    )

    workflow.add_node(
        "qa",
        qa_reviewer,
    )

    # ---------------------------------------------------------
    # Entry point
    # ---------------------------------------------------------

    workflow.set_entry_point(
        "analyst"
    )

    # ---------------------------------------------------------
    # Main workflow
    # ---------------------------------------------------------

    workflow.add_edge(
        "analyst",
        "developer",
    )

    workflow.add_edge(
        "developer",
        "qa",
    )

    # ---------------------------------------------------------
    # QA routing
    # ---------------------------------------------------------

    workflow.add_conditional_edges(
        "qa",
        route_after_qa,
        {
            "developer": "developer",
            "finish": END,
        },
    )

    return workflow.compile()