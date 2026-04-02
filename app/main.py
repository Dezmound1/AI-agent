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
        - `execute_sql` — run a single read-only query.

        Rules:
        1. ALWAYS call list_tables and describe_table before writing SQL.
        2. ALWAYS execute SQL through execute_sql tool. NEVER write SQL in your text response.
        3. If you need multiple queries — call execute_sql multiple times, one query per call.
        4. Only SELECT queries. Never INSERT, UPDATE, DELETE, DDL.
        5. After getting results, summarize findings in natural language with key numbers.
        6. If a tool returns error, fix the query and try again.

        IMPORTANT: You must CALL tools to get data. Do not show SQL code to the user — execute it.
        CRITICAL: Your answer MUST be based ONLY on data returned by tools.
        Do not invent names, numbers, or text that was not in the tool results.
        If execute_sql returned specific rows — quote them exactly, do not paraphrase.
        """.strip()
    client = get_llm_client(provider)
    runner = AgentRunner(client, registry, session)
    return {"response": await runner.run(message, system)}