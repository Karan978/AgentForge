from langchain_core.messages import SystemMessage, HumanMessage
from config import get_llm
from graph.state import AgentState
from tools.filesystem import list_files,read_file,write_file

from tools.shell import run_command
from tools.git import git_diff

llm = get_llm()

SYSTEM_PROMPT = """
You are a senior Python software engineer.

You are responsible for implementing the requested
software change.

You have access to:

- repository files
- file reading
- file writing
- test execution
- git diff

Follow the existing architecture and coding style.

IMPORTANT:

- Do not rewrite unrelated files.
- Do not remove existing functionality.
- Do not invent dependencies unnecessarily.
- Prefer minimal, maintainable changes.
- Add or update tests where appropriate.
- Inspect relevant files before modifying them.
- Run tests after implementation.
- If tests fail, diagnose and fix the problem.

Your final response should summarize:

1. What you changed
2. Files changed
3. Tests executed
4. Test results
5. Remaining issues
"""

def developer(state: AgentState) -> AgentState:
    repo_path = state["repo_path"]
    task = state["task"]
    analysis= state["Analysis"]

    files = list_files(repo_path)

    prompt = f"""
    Engineering task:

    {task}


    Repository files:

    {files}


    Senior engineer's analysis:

    {analysis}


    Your job is now to implement the task.

    First inspect the relevant source files.

    Then determine the required changes.

    When implementing:

    - read the relevant files
    - write the required changes
    - add/update tests
    - run pytest
    - inspect git diff
    - fix failures if necessary

    You are allowed to modify repository files.
    """
    response = llm.invoke(
        [
            SystemMessage(content = SYSTEM_PROMPT),
            HumanMessage(content = prompt)
        ]
    )

    developer_summary = response.content

    diff = git_diff(repo_path)

    return{
        **state,
        "developer_summary":developer_summary,
        "changed_files": [],
        "test_output": diff,
        "iteration": state.get("iteration",0)+1
    }
