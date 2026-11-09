from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.tools import tool

from agents.tool_loop import run_tool_loop
from config import get_llm
from graph.state import AgentState
from tools.filesystem import list_files, read_file


SYSTEM_PROMPT = """
You are a senior software engineer acting as a
repository analyst.

Your responsibility is to understand an existing
software repository and create a precise implementation
plan.

You MUST NOT modify files. You only have read-only tools.

Use the read_file tool to inspect the source files and
tests that are relevant to the task before drawing
conclusions.

Your analysis should identify:

1. Repository structure
2. Relevant files
3. Existing classes and functions
4. Dependencies
5. Existing tests
6. How the requested change fits the architecture
7. Files that should be modified
8. New files that may be required
9. Edge cases
10. Risks

Your output must be practical enough for another
software engineer to implement the task.

Do not invent files or APIs that you have not observed.
"""


def _make_tools(repo_path: str):

    @tool("read_file")
    def read_file_tool(file_path: str) -> str:
        """Read a file. `file_path` is relative to the repository root."""
        return read_file(repo_path, file_path)

    return [read_file_tool]


def software_analyst(state: AgentState) -> AgentState:
    repo_path = state["repo_path"]
    task = state["task"]
    # Inspect Repository
    files = list_files(repo_path)
    prompt = f"""
    Engineering task:

    {task}


    Repository:

    {repo_path}


    Files in repository:

    {files}


    Read the files relevant to the task, then produce:

    ## Repository Analysis

    Explain the relevant architecture.

    ## Relevant Files

    Identify files relevant to the task.

    ## Implementation Plan

    Give a step-by-step implementation plan.

    ## Testing Plan

    Describe tests that should be added or modified.

    ## Risks

    Identify potential regressions and edge cases.
    """

    analysis = run_tool_loop(
        get_llm(),
        _make_tools(repo_path),
        [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=prompt),
        ],
    )

    return {
        **state,
        "analysis": analysis,
        "implementation_plan": analysis,
    }
