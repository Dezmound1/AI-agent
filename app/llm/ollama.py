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
        logger.warning(f"Ollama thinks: {data['message']['thinking']}")
        return data["message"]["content"]

    async def chat_with_tools(self, messages: list[dict], system: str = "", tools: list[dict] = []) -> str:
        """Chat with Ollama with tools."""
        ... 