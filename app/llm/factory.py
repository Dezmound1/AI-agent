import enum
from .anthropic import LLMClaude
from .ollama import LLMOllama
from .base import BaseLLMClient


class LLMName(enum.Enum):
    """Names of LLM clients."""
    ANTHROPIC = LLMClaude
    OLLAMA = LLMOllama

def get_llm_client(llm_name: str) -> BaseLLMClient:
    """Get an LLM client by name."""

    return LLMName[llm_name.upper()].value()