from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.tools import tool

from agents.tool_loop import run_tool_loop
from config import get_llm
from graph.state import AgentState
from tools.filesystem import list_files, read_file, write_file
from tools.git import git_diff
from tools.shell import run_tests


SYSTEM_PROMPT = """
You are a senior Python software engineer.

You are responsible for implementing the requested
software change.

You have these tools:

- list_files: list repository files
- read_file: read a file
- write_file: create or overwrite a file with full content
- run_tests: run the pytest suite
- git_diff: show your changes so far

Follow the existing architecture and coding style.

IMPORTANT:

- Do not rewrite unrelated files.
- Do not remove existing functionality.
- Do not invent dependencies unnecessarily.
- Prefer minimal, maintainable changes.
- Add or update tests where appropriate.
- Inspect relevant files with read_file before modifying them.
- write_file replaces the whole file, so always write the
  complete new content.
- Run tests after implementation.
- If tests fail, diagnose and fix the problem.

Your final response should summarize:

1. What you changed
2. Files changed
3. Tests executed
4. Test results
5. Remaining issues
"""


def _make_tools(repo_path: str, changed_files: set[str]):

    @tool("list_files")
    def list_files_tool() -> str:
        """List all files in the repository."""
        return list_files(repo_path)

    @tool("read_file")
    def read_file_tool(file_path: str) -> str:
        """Read a file. `file_path` is relative to the repository root."""
        return read_file(repo_path, file_path)

    @tool("write_file")
    def write_file_tool(file_path: str, content: str) -> str:
        """
        Create or overwrite a file with the complete new content.
        `file_path` is relative to the repository root.
        """
        result = write_file(repo_path, file_path, content)
        if result.startswith("Successfully"):
            changed_files.add(file_path)
        return result

    @tool("run_tests")
    def run_tests_tool() -> str:
        """Run the repository's pytest suite and return the results."""
        return str(run_tests(repo_path))

    @tool("git_diff")
    def git_diff_tool() -> str:
        """Show all changes made to the repository so far."""
        return git_diff(repo_path)

    return [
        list_files_tool,
        read_file_tool,
        write_file_tool,
        run_tests_tool,
        git_diff_tool,
    ]


def _feedback_section(state: AgentState) -> str:
    """
    On a retry, give the developer the QA results from the previous
    attempt so it can address them.
    """

    if state.get("iteration", 0) == 0 or "review" not in state:
        return ""

    return f"""

    PREVIOUS ATTEMPT WAS REJECTED BY QA
    ===================================

    Your earlier changes are still in the repository. Fix the
    problems below instead of starting over.

    Test results:

    {state.get("test_output", "")}

    QA review:

    {state.get("review", "")}
    """


def developer(state: AgentState) -> AgentState:
    repo_path = state["repo_path"]
    task = state["task"]
    analysis = state.get("analysis", "")

    files = list_files(repo_path)

    prompt = f"""
    Engineering task:

    {task}


    Repository files:

    {files}


    Senior engineer's analysis:

    {analysis}
    {_feedback_section(state)}

    Your job is now to implement the task.

    First inspect the relevant source files.

    Then determine the required changes.

    When implementing:

    - read the relevant files
    - write the required changes
    - add/update tests
    - run the tests
    - inspect git diff
    - fix failures if necessary

    You are allowed to modify repository files.
    """

    changed_files = set(state.get("changed_files", []))

    developer_summary = run_tool_loop(
        get_llm(),
        _make_tools(repo_path, changed_files),
        [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=prompt),
        ],
    )

    return {
        **state,
        "developer_summary": developer_summary,
        "changed_files": sorted(changed_files),
        "diff": git_diff(repo_path),
        "iteration": state.get("iteration", 0) + 1,
    }
