"""
Shared tool-calling loop for the agents.

The LLM is given a set of tools. Each turn, every tool call it requests
is executed and the result is sent back, until it answers without
requesting a tool or the step limit is reached.
"""

from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    HumanMessage,
    ToolMessage,
)
from langchain_core.tools import BaseTool


MAX_TOOL_STEPS = 25

# Keep a single tool result from flooding the context window.
MAX_TOOL_OUTPUT_CHARS = 20_000


def _truncate(text: str) -> str:
    if len(text) <= MAX_TOOL_OUTPUT_CHARS:
        return text
    return (
        text[:MAX_TOOL_OUTPUT_CHARS]
        + f"\n\n[truncated: {len(text) - MAX_TOOL_OUTPUT_CHARS} "
        "more characters]"
    )


def run_tool_loop(
    llm,
    tools: list[BaseTool],
    messages: list[BaseMessage],
    max_steps: int = MAX_TOOL_STEPS,
) -> str:
    """
    Run the LLM with tools until it produces a final answer.

    Returns the final answer text.
    """

    tools_by_name = {t.name: t for t in tools}
    llm_with_tools = llm.bind_tools(tools)
    messages = list(messages)

    for _ in range(max_steps):
        response: AIMessage = llm_with_tools.invoke(messages)
        messages.append(response)

        if not response.tool_calls:
            return response.content

        for call in response.tool_calls:
            selected = tools_by_name.get(call["name"])

            if selected is None:
                result = f"Unknown tool: {call['name']}"
            else:
                try:
                    result = selected.invoke(call["args"])
                except Exception as exc:
                    result = f"Tool error: {exc}"

            messages.append(
                ToolMessage(
                    content=_truncate(str(result)),
                    tool_call_id=call["id"],
                )
            )

    # Step limit reached: ask for a final answer without tools.
    messages.append(
        HumanMessage(
            content=(
                "You have reached the tool-call limit. Stop using tools "
                "and give your final answer now, including anything "
                "left unfinished."
            )
        )
    )
    return llm.invoke(messages).content
