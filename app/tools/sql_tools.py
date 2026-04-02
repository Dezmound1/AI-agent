from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import text
from app.tools.registry import ToolRegistry


registry = ToolRegistry()


@registry.register_tool(
    name="execute_sql",
    description="Выполнить SQL SELECT запрос. Только чтение, не модификация данных.",
    schema={
        "type": "object",
        "properties": {
            "query": {
                "type": "string", 
                "description": "SQL SELECT запрос",
            },
            "limit": {
                "type": "integer",
                "description": "Максимум строк (по умолчанию 50)",
            },
        },
        "required": ["query"],
    },
)
async def execute_sql(query: str, limit: int = 50, *, session: AsyncSession) -> dict:
    """
    Execute a SQL SELECT query.

    Parameters
    ----------
    query: str
        The SQL SELECT query to execute.
    limit: int
        The maximum number of rows to return.
    session: AsyncSession
        The session to use to execute the query.

    Returns
    -------
    dict
        The result of the query.
    """
    query = query.strip()

    if not query:
        return {"error": "Query can't be empty"}
    if not query.startswith("SELECT"):
        return {"error": "Only SELECT queries are allowed"}

    query_text = f"{query} LIMIT {limit}"
    rows = [
        dict(row._mapping) for row in await session.execute(text(query_text)).fetchall()
    ]
    return {"result": rows}
