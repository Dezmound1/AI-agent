import os
import httpx

from .base import BaseLLMClient

DEFAULT_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
DEFAULT_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.1")


class LLMOllama(BaseLLMClient):
    """LLM client for Ollama (HTTP API)."""

    def __init__(
        self,
        base_url: str = DEFAULT_BASE_URL,
        model: str = DEFAULT_MODEL,
    ) -> None:  
        """Initialize the LLM client."""
        self._base_url = base_url.rstrip("/")
        self._model = model
        self._timeout = httpx.Timeout(10.0, read=120.0)

    async def chat(self, messages: list[dict], system: str = "") -> str:
        """Chat with Ollama; `messages` use OpenAI-style roles (user, assistant, …)."""
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
