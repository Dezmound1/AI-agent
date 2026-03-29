import abc

class BaseLLMClient(abc.ABC):
    """Base class for LLM clients."""


    @abc.abstractmethod
    async def chat(self, messages: list[dict], system: str = "") -> str:
        """Create a message using the LLM client with context."""
        pass
