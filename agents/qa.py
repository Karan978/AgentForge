from typing import Literal

from langchain_core.messages import (
    SystemMessage,
    HumanMessage,
)
from pydantic import BaseModel, Field

from config import get_llm

from graph.state import AgentState

from tools.shell import run_tests

from tools.git import git_diff


class QAReview(BaseModel):
    """Structured QA review, so the verdict never has to be parsed from text."""

    review: str = Field(
        description=(
            "The full technical review in Markdown: findings per area, "
            "confirmed issues vs potential risks, and the reasoning behind "
            "the verdict with the most important actions required."
        )
    )
    verdict: Literal["APPROVED", "CHANGES_REQUESTED"] = Field(
        description="APPROVED only if the implementation should be accepted."
    )


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
changes. Put the full review in the `review` field and set
the `verdict` field to APPROVED or CHANGES_REQUESTED.
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

    # Pass/fail comes from pytest's exit code, not from searching the
    # output. "No tests collected" (exit code 5) counts as not passed:
    # the developer is required to add tests, and the reason is shown
    # in the test output that is fed back to it.
    test_run = run_tests(repo_path)

    test_output = str(test_run)

    tests_passed = test_run.passed

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

At the end, provide a concise final assessment: explain the
reasoning behind the verdict and identify the most important
actions required before acceptance, if any.

Set the verdict field to APPROVED or CHANGES_REQUESTED.
"""

    result: QAReview = get_llm().with_structured_output(
        QAReview
    ).invoke(
        [
            SystemMessage(
                content=SYSTEM_PROMPT
            ),
            HumanMessage(
                content=prompt
            ),
        ]
    )

    review = f"{result.review}\n\nVERDICT: {result.verdict}"

    review_passed = result.verdict == "APPROVED"

    return {
        **state,
        "diff": diff,
        "test_output": test_output,
        "test_exit_code": test_run.exit_code,
        "tests_passed": tests_passed,
        "review": review,
        "review_passed": review_passed,
    }
