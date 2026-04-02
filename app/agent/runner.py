from httpx import Response
from sqlalchemy.ext.asyncio import AsyncSession
from app.llm.base import BaseLLMClient
from app.tools.registry import ToolRegistry


class AgentRunner:
    """Runner for agents."""
    def __init__(self, llm_client: BaseLLMClient, registry: ToolRegistry, session: AsyncSession) -> None: 
        """
        Initialize the agent runner.

        Parameters
        ----------
        llm_client: BaseLLMClient
            The LLM client to use.
        registry: ToolRegistry
            The registry of tools to use.
        """
        self._llm_client = llm_client
        self._registry = registry
        self._session = session
    
    async def run(self, message: str) -> str:
        """
        Run the agent.
        
        Parameters
        ----------
        message: str
            The message to run the agent.
            
        Returns
        -------
        str
            The response from the agent.
        """
        messages = [{"role": "user", "content": message}]
        return await self._llm_client.chat_with_tools(messages, tools=self._registry)