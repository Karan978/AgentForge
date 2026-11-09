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


def finalize(
    state: AgentState,
) -> AgentState:
    """
    Record why the workflow ended, so success, rejection and an
    exhausted retry budget can be told apart.
    """

    tests_passed = state.get("tests_passed", False)
    review_passed = state.get("review_passed", False)

    if tests_passed and review_passed:
        return {
            **state,
            "final_status": "SUCCESS",
            "final_reason": "Tests passed and QA approved the change.",
        }

    reasons = []

    if not tests_passed:
        exit_code = state.get("test_exit_code")
        if exit_code == 5:
            reasons.append("no tests were collected")
        elif exit_code is None:
            reasons.append("tests did not complete")
        else:
            reasons.append(f"tests failed (pytest exit code {exit_code})")

    if not review_passed:
        reasons.append("QA requested changes")

    return {
        **state,
        "final_status": "FAILED",
        "final_reason": (
            f"Stopped after {state.get('iteration', 0)} of "
            f"{MAX_ITERATIONS} developer attempts: "
            + "; ".join(reasons)
            + "."
        ),
    }


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

    workflow.add_node(
        "finalize",
        finalize,
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
            "finish": "finalize",
        },
    )

    workflow.add_edge(
        "finalize",
        END,
    )

    return workflow.compile()