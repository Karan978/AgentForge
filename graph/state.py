from typing import TypedDict


class AgentState(TypedDict, total=False):
    # User Request
    task: str
    repo_path: str
    # Analyst Agent
    analysis: str
    implementation_plan: str
    # Developer Agent
    developer_summary: str
    changed_files: list[str]
    diff: str
    # QA Agent
    test_output: str
    test_exit_code: int | None
    tests_passed: bool
    review: str
    review_passed: bool
    # Workflow
    iteration: int
    final_status: str
    final_reason: str
