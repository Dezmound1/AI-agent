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
    query = query.strip().rstrip(";")

    if ";" in query:
        return {"error": "Only one SQL statement allowed"}

    if not query.upper().startswith("SELECT"):
        return {"error": "Only SELECT queries are allowed"}

    if "LIMIT" not in query.upper():
        query = f"{query} LIMIT {limit}"

    try:
        result = await session.execute(text(query))
        rows = [dict(row._mapping) for row in result.fetchall()]
        return {"rows": rows, "count": len(rows)}
    except Exception as e:
        await session.rollback()
        return {"error": str(e)}


@registry.register_tool(
    name="list_tables",
    description="Показать все таблицы в базе данных",
    schema={
        "type": "object", 
        "properties": {}, 
        "required": [],
        },
)
async def list_tables(*, session: AsyncSession) -> dict:
    result = await session.execute(
        text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
    )
    tables = [row[0] for row in result.fetchall()]
    return {"tables": tables}


@registry.register_tool(
    name="describe_table",
    description="Показать колонки и типы данных таблицы",
    schema={
        "type": "object",
        "properties": {
            "table_name": {"type": "string", "description": "Имя таблицы"}
        },
        "required": ["table_name"],
    },
)
async def describe_table(table_name: str, *, session: AsyncSession) -> dict:
    result = await session.execute(
        text(
            "SELECT column_name, data_type, is_nullable "
            "FROM information_schema.columns "
            "WHERE table_name = :t"
        ),
        {"t": table_name},
    )
    columns = [dict(row._mapping) for row in result.fetchall()]
    return {"table": table_name, "columns": columns}