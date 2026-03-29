from anthropic import AsyncAnthropic

from .base import BaseLLMClient

class LLMClaude(BaseLLMClient):
    """Service for creating masseges using Anthropic API."""

    def __init__(self):
        self._client = AsyncAnthropic()

    async def chat(self, messages: list[dict], system: str = "") -> str:
        """Chat with Anthropic API."""

        response = await self._client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            system="" if not system else system,
            messages=messages
        )
        return response.content[0].text