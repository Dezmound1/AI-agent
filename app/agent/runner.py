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
    
    async def run(self, message: str, system: str = "") -> str:
        """
        Run the agent.
        
        Parameters
        ----------
        message: str
            The message to run the agent.
        system: str
            The system prompt to use in the agent.
        
        Returns
        -------
        str
            The response from the agent.
        """
        messages = [{"role": "user", "content": message}]

        tools_used = []

        for _ in range(5):
            response = await self._llm_client.chat_with_tools(messages, system, tools=self._registry.schemas)


            if response["type"] == "text":
                return {"reply": response["content"], "tools_used": tools_used}
            
            tools_used.append(response["name"])
            result = await self._registry.execute_tool(response["name"], response["input"], session=self._session)

            history_entries = self._llm_client.format_tool_result(response, result)
            messages.extend(history_entries)

        return {"reply": "Превышен лимит итераций", "tools_used": tools_used}