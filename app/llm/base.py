import abc


class BaseLLMClient(abc.ABC):
    """Base class for LLM clients."""

    @abc.abstractmethod
    async def chat(self, messages: list[dict], system: str = "") -> str:
        """
        Create a message using the LLM client with context.

        Parameters
        ----------
        messages: list[dict]
            The messages to send to the LLM.
        system: str
            The system prompt to send to the LLM.
        """
        pass

    @abc.abstractmethod
    async def chat_with_tools(
        self,
        messages: list[dict],
        system: str = "",
        tools: list[dict] = [],
    ) -> str:
        """
        Create a message using the LLM client with tools.

        Parameters
        ----------
        messages: list[dict]
            The messages to send to the LLM.
        system: str
            The system prompt to send to the LLM.
        tools: list[dict]
            The tools to use in the LLM.
        """
        pass

    @abc.abstractmethod
    def format_tool_result(self, response: dict, result: str) -> list[dict]:
        """
        Format the tool result.
        
        Parameters
        ----------
        response: dict
            The response from the LLM.
        result: str
            The result of the tool.
        """
        pass