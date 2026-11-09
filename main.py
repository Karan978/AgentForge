import argparse
import sys

from graph.workflow import build_graph
from tools.git import working_tree_problem


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
    # Require a clean git working tree
    # ---------------------------------------------------------
    # The agents edit the repository in place. Starting clean means
    # the final diff contains only their changes and can be reverted.

    problem = working_tree_problem(args.repo)

    if problem:
        print(f"Cannot start: {problem}", file=sys.stderr)
        sys.exit(1)

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

    print("\nCHANGED FILES")
    print("-" * 80)

    print(
        "\n".join(result.get("changed_files", []))
        or "None"
    )

    print("\nDIFF")
    print("-" * 80)

    print(
        result.get(
            "diff",
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

    print(result.get("final_status", "UNKNOWN"))
    print(result.get("final_reason", ""))

    if result.get("final_status") != "SUCCESS":
        print()
        print("NEEDS HUMAN REVIEW. The changes were left in the repository.")
        print("To discard them (the tree was clean before the run):")
        print(f'  git -C "{args.repo}" restore --staged --worktree .')
        print(f'  git -C "{args.repo}" clean -fd')

    print()


if __name__ == "__main__":
    main()