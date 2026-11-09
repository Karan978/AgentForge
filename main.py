import argparse

from graph.workflow import build_graph


def main():

    parser = argparse.ArgumentParser(
        description="AgentForge - Multi-Agent Software Engineer"
    )

    parser.add_argument(
        "--repo",
        required=True,
        help="Path to the repository",
    )

    parser.add_argument(
        "--task",
        required=True,
        help="Engineering task",
    )

    args = parser.parse_args()

    # ---------------------------------------------------------
    # Build LangGraph
    # ---------------------------------------------------------

    graph = build_graph()

    # ---------------------------------------------------------
    # Initial state
    # ---------------------------------------------------------

    initial_state = {
        "task": args.task,
        "repo_path": args.repo,
        "iteration": 0,
        "tests_passed": False,
        "review_passed": False,
    }

    # ---------------------------------------------------------
    # Execute
    # ---------------------------------------------------------

    result = graph.invoke(
        initial_state
    )

    # ---------------------------------------------------------
    # Display results
    # ---------------------------------------------------------

    print()
    print("=" * 80)
    print("AGENTFORGE")
    print("=" * 80)

    print("\nTASK")
    print("-" * 80)

    print(result["task"])

    print("\nANALYSIS")
    print("-" * 80)

    print(result.get("analysis", ""))

    print("\nDEVELOPER")
    print("-" * 80)

    print(
        result.get(
            "developer_summary",
            "",
        )
    )

    print("\nTEST RESULTS")
    print("-" * 80)

    print(
        result.get(
            "test_output",
            "",
        )
    )

    print("\nCODE REVIEW")
    print("-" * 80)

    print(
        result.get(
            "review",
            "",
        )
    )

    print("\nSTATUS")
    print("-" * 80)

    if (
        result.get("tests_passed")
        and result.get("review_passed")
    ):
        print("SUCCESS")

    else:
        print("NEEDS HUMAN REVIEW")

    print()


if __name__ == "__main__":
    main()