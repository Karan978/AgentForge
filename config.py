from dotenv import load_dotenv
from langchain_openai import ChatOpenAI


load_dotenv()


def get_llm() -> ChatOpenAI:
    """
    Create and return the LLM used by all agents.
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