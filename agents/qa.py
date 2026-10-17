from langchain_core.messages import (
    SystemMessage,
    HumanMessage,
)

from config import get_llm

from graph.state import AgentState

from tools.shell import run_command

from tools.git import git_diff


llm = get_llm()


SYSTEM_PROMPT = """
You are a senior QA engineer and principal software
reviewer responsible for evaluating a software
implementation before it is accepted.

Your task is to perform a rigorous technical assessment
using the original engineering requirements, the
implementation summary, the code changes, and the
automated test results provided to you.

Evaluate the implementation across the following areas:

1. Functional correctness
2. Test coverage
3. Edge cases
4. Backwards compatibility
5. Maintainability
6. Error handling
7. Security
8. Performance
9. Consistency with the existing codebase

Do not assume that passing tests automatically means the
implementation is correct.

Likewise, do not assume that every failing test means the
implementation is incorrect. Consider whether a failure
could instead be caused by:

- an incorrect test
- a pre-existing defect
- an environment problem
- a dependency problem
- a configuration problem
- a flaky test
- an unrelated failure

Base your conclusions on the evidence provided.

Distinguish between:

- confirmed problems
- likely problems
- potential risks

Do not report speculative issues without explaining the
reasoning or evidence behind them.

Pay particular attention to whether the implementation
actually satisfies the original requirements rather than
merely passing the available tests.

Your final assessment must clearly state whether the
implementation should be accepted or requires further
changes.

Use exactly one of the following verdicts:

APPROVED

CHANGES_REQUESTED
"""


def qa_reviewer(
    state: AgentState,
) -> AgentState:

    repo_path = state["repo_path"]

    task = state["task"]

    developer_summary = state.get(
        "developer_summary",
        "",
    )

    # ---------------------------------------------------------
    # Run automated tests
    # ---------------------------------------------------------

    test_output = run_command(
        "pytest",
        repo_path,
    )

    tests_passed = (
        "failed" not in test_output.lower()
        and "error" not in test_output.lower()
        and "exit code: 0" in test_output.lower()
    )

    # ---------------------------------------------------------
    # Get code changes
    # ---------------------------------------------------------

    diff = git_diff(repo_path)

    # ---------------------------------------------------------
    # Ask LLM to review
    # ---------------------------------------------------------

    prompt = f"""
Evaluate the following software implementation.

ORIGINAL ENGINEERING TASK
=========================
{task}


IMPLEMENTATION SUMMARY
======================
{developer_summary}


CODE CHANGES
============
{diff}


AUTOMATED TEST RESULTS
======================
{test_output}


Perform a rigorous technical review of the implementation.

First determine whether the implementation satisfies the
original engineering task.

Then evaluate:

1. Functional correctness
   - Does the implementation produce the required behavior?
   - Are important requirements missing?
   - Are there incorrect assumptions or behaviors?

2. Test coverage
   - Do the existing tests adequately validate the change?
   - Are important scenarios or failure cases untested?
   - Do the test results provide sufficient evidence of correctness?

3. Edge cases
   - What happens with invalid, empty, unexpected, or boundary inputs?
   - Could unusual conditions cause incorrect behavior?

4. Backwards compatibility
   - Could existing functionality be affected?
   - Could existing callers, interfaces, or data formats break?

5. Maintainability
   - Is the implementation consistent with the existing codebase?
   - Does it introduce unnecessary complexity, duplication, or coupling?

6. Error handling
   - Are expected failures handled appropriately?
   - Could errors be silently ignored or incorrectly propagated?

7. Security
   - Look for concrete security weaknesses introduced by the change.
   - Consider issues such as unsafe input handling, authentication,
     authorization, injection, secrets exposure, unsafe file access,
     or unsafe command execution where relevant.

8. Performance
   - Could the change introduce unnecessary computation, I/O,
     memory usage, database queries, or network requests?

9. Regression risk
   - Could the change negatively affect functionality that is not
     directly covered by the tests?

Analyze the automated test results carefully.

If tests failed, determine whether the failures are actually
caused by the implementation. Do not automatically attribute
every failure to the code change.

For every significant issue you identify, explain:

- what the issue is
- where it occurs
- why it matters
- what evidence supports the finding
- its severity

Separate confirmed issues from potential risks.

Do not invent problems that are not supported by the provided
code, test results, or requirements.

At the end, provide a concise final assessment.

Use exactly one verdict:

APPROVED

or

CHANGES_REQUESTED

Then explain the reasoning behind the verdict and identify
the most important actions required before acceptance, if any.
"""

    response = llm.invoke(
        [
            SystemMessage(
                content=SYSTEM_PROMPT
            ),
            HumanMessage(
                content=prompt
            ),
        ]
    )

    review = response.content

    review_passed = (
        "APPROVED" in review.upper()
        and "CHANGES_REQUESTED"
        not in review.upper()
    )

    return {
        **state,
        "test_output": test_output,
        "tests_passed": tests_passed,
        "review": review,
        "review_passed": review_passed,
    }