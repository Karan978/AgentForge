import os
from functools import lru_cache
from pathlib import Path

from dotenv import dotenv_values
from langchain_openai import ChatOpenAI


# The .env file next to this file, so it is found no matter which folder
# AgentForge is started from.
ENV_FILE = Path(__file__).resolve().parent / ".env"


def get_api_key() -> str:
    """
    Return the OpenAI API key.

    An OPENAI_API_KEY environment variable takes precedence; otherwise
    the key is read from .env.

    The .env file is read with dotenv_values() rather than load_dotenv(),
    so the key is NOT copied into os.environ. That keeps it out of the
    environment of child processes, such as the target repository's
    test suite.
    """

    key = os.environ.get("OPENAI_API_KEY") or dotenv_values(ENV_FILE).get(
        "OPENAI_API_KEY"
    )

    return (key or "").strip()


@lru_cache(maxsize=1)
def get_llm() -> ChatOpenAI:
    """
    Create and return the LLM used by all agents.

    Cached so every agent shares one client, and called lazily from
    inside the agents so importing a module never needs credentials.
    """

    api_key = get_api_key()

    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY is not set. Add it to "
            f"{ENV_FILE} (OPENAI_API_KEY=sk-...) or set it as an "
            "environment variable."
        )

    return ChatOpenAI(
        model="gpt-4.1-mini",
        temperature=0,
        api_key=api_key,
    )
