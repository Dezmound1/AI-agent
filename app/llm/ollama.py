import logging
import httpx

from app.config import settings
from .base import BaseLLMClient

logger = logging.getLogger(__name__)


class LLMOllama(BaseLLMClient):
    """LLM client for Ollama (HTTP API)."""

    def __init__(
        self,
        base_url: str | None = None,
        model: str | None = None,
    ) -> None:
        """Initialize the LLM client."""

        url = base_url or settings.ollama_base_url
        self._base_url = url.rstrip("/")
        self._model = model or settings.ollama_model
        self._timeout = httpx.Timeout(10.0, read=120.0)

    async def chat(self, messages: list[dict], system: str = "") -> str:
        """
        Chat with Ollama; `messages` use OpenAI-style roles (user, assistant, …).
        
        Parameters
        ----------
        messages: list[dict]
            The messages to send to the LLM.
        system: str
            The system prompt to send to the LLM.
            
        Returns
        -------
        str
            The response from the LLM.
        """
        payload_messages: list[dict] = []
        if system:
            payload_messages.append({"role": "system", "content": system})
        payload_messages.extend(messages)

        async with httpx.AsyncClient(base_url=self._base_url, timeout=self._timeout) as client:
            response = await client.post(
                "/api/chat",
                json={
                    "model": self._model,
                    "messages": payload_messages,
                    "stream": False,
                },
            )
            response.raise_for_status()
            data = response.json()
        return data["message"]["content"]

    async def chat_with_tools(self, messages: list[dict], system: str = "", tools: list[dict] = []) -> dict:
        """
        Chat with Ollama with tools.
        
        Parameters
        ----------
        messages: list[dict]
            The messages to send to the LLM.
        system: str
            The system prompt to send to the LLM.
        tools: list[dict]
            The tools to use in the LLM.
            
        Returns
        -------
        str
            The response from the LLM.
        """

        ollama_tools = [
            {
                "type": "function",
                "function": {
                    "name": t["name"],
                    "description": t["description"],
                    "parameters": t["input_schema"],
                }
            }
            for t in tools
        ]

        payload_messages = []
        if system:
            payload_messages.append({"role": "system", "content": system})
        payload_messages.extend(messages)

        async with httpx.AsyncClient(
            base_url=self._base_url, timeout=self._timeout
        ) as client:
            response = await client.post(
                "/api/chat",
                json={
                    "model": self._model,
                    "messages": payload_messages,
                    "tools": ollama_tools,
                    "stream": False,
                },
            )
            response.raise_for_status()
            data = response.json()

        message = data["message"]

        if message.get("tool_calls"):
            tool_call = message["tool_calls"][0]
            func = tool_call["function"]
            return {
                "type": "tool_use",
                "name": func["name"],
                "input": func["arguments"],
                "id": tool_call.get("id", "call_1"),
                "raw": message,
            }

        return {
            "type": "text",
            "content": message["content"],
        }
    
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
        return [
            {
                "role": "assistant",
                "content": "",
                "tool_calls": [{
                    "function": {
                        "name": response["name"],
                        "arguments": response["input"],
                    }
                }],
            },
            {
                "role": "tool",
                "content": result,
            },
        ]