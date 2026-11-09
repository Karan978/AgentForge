from functools import lru_cache

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI


load_dotenv()


@lru_cache(maxsize=1)
def get_llm() -> ChatOpenAI:
    """
    Create and return the LLM used by all agents.

    Cached so every agent shares one client, and called lazily from
    inside the agents so importing a module never needs credentials.
    """

    api_key = ""

    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY is not set. "
            "Add it to your .env file."
        )

    return ChatOpenAI(
        model="gpt-4.1-mini",
        temperature=0,
        api_key=api_key,
    )
