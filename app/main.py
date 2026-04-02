import json

from fastapi import Body, FastAPI
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.agent.runner import AgentRunner
from app.db.session import get_session

from app.llm.factory import get_llm_client
from app.llm.structured import get_structured_response
from app.schemas.agent import TaskClassification
from app.tools.sql_tools import registry

app = FastAPI()


@app.post("/chat")
async def chat(
    model: str = Body(default="ollama"),
    message: str = Body(...),
    system: str = Body(default=""),
):
    """Свободный чат — модель отвечает текстом."""
    client = get_llm_client(model)
    messages = [{"role": "user", "content": message}]
    reply = await client.chat(messages, system)
    return {"reply": reply, "provider": model}


@app.post("/classify")
async def classify(model: str = Body(default="ollama"), message: str = Body(...)):
    """
    Chat with the LLM.

    Parameters
    ----------
    model: str
        The name of the LLM model to use.
    messages: list[dict]
        The messages to send to the LLM.
    system: str
        The system prompt to send to the LLM.

    Returns
    -------
    dict
        The response from the LLM.
    """
    llm_client = get_llm_client(model)
    system = f"""

    You are a helpful assistant and python expert developer with 10 years of experience.

    Reply ONLY with valid JSON, no explanations.
    Schema: {json.dumps(TaskClassification.model_json_schema(), ensure_ascii=False)}

    Examples:
    Input: "The payment button does not work on mobile"
    Output: {{"category": "bug", "priority": "high", "summary": "Payment button broken on mobile"}}

    Input: "I want to export reports to PDF"
    Output: {{"category": "feature", "priority": "low", "summary": "Request for PDF export of reports"}}
    """

    messages = [{"role": "user", "content": message}]
    result = await get_structured_response(
        llm_client, messages, system, TaskClassification
    )
    return result.model_dump()


@app.post("/agent")
async def agent_endpoint(
    message: str = Body(...),
    provider: str = Body(default="ollama"),
    session: AsyncSession = Depends(get_session),
) -> dict:
    """
    Run the agent.
    
    Parameters
    ----------
    message: str
        The message to run the agent.
    provider: str
        The provider of the LLM.
    session: AsyncSession
        The session of the database.
        
    Returns
    -------
    dict
        The response from the agent.
    """
    system = """
        You are a careful SQL assistant for a PostgreSQL database (schema `public`).

        You can call tools:
        - `list_tables` — list base tables when the schema is unknown.
        - `describe_table` — get column names and types before writing queries.
        - `execute_sql` — run a single read-only query. Parameters: `query` (required, one SELECT only) and optional `limit` (default 50). Do not put a semicolon; do not send multiple statements.

        Rules:
        1. Prefer `list_tables` or `describe_table` before guessing table/column names.
        2. Only SELECT (and read-only constructs the tool allows). Never ask to INSERT, UPDATE, DELETE, DDL, or admin commands.
        3. Use clear, valid PostgreSQL. Qualify names if needed (`public.table_name`).
        4. After tool results, answer in natural language: summarize findings, show key numbers or rows briefly, and mention row counts when useful.
        5. If a tool returns `error`, explain it briefly and suggest a fix (e.g. fix column name, simplify query).
        6. If the user question does not need the database, answer directly without tools.

        Be concise and accurate.
        """.strip()
    client = get_llm_client(provider)
    runner = AgentRunner(client, registry, session)
    return {"response": await runner.run(message, system)}