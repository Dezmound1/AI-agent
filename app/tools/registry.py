import json
from typing import Any

class ToolRegistry:
    """Registry of tools."""

    def __init__(self):
        self._tools: dict[str, callable] = {}
        self._schemas: list[dict] = []
    
    def register_tool(self, name: str, description: str, schema: dict) -> None:
        """Register a tool."""

        def decorator(func: callable) -> callable:
            self._tools[name] = func            
            self._schemas.append({
                "name": name,
                "description": description,
                "input_schema": schema
            })
            return func
        return decorator
    
    async def execute_tool(self, name: str, params: dict, **context: Any) -> dict:
        """Execute a tool."""
        tool = self._tools.get(name)
        if not tool:
            raise ValueError(f"Tool {name} not found")
        result = await tool(**params, **context)
        return json.dumps(result)

    @property
    def schemas(self) -> list[dict]:
        """Get the schemas of the tools."""
        return self._schemas