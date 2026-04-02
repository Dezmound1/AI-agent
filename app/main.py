import json
from fastapi import Body, FastAPI

from app.llm.factory import get_llm_client
from app.llm.structured import get_structured_response
from app.schemas.agent import TaskClassification

app = FastAPI()


@app.get("/")
def read_root():

    return {"message": "Hello from ai-agent"}


@app.post("/chat")
async def chat(model: str = Body(default="ollama"), message: str = Body(...)):
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

    messages = [{"role": "user", "prompt": message}]
    return await get_structured_response(
        llm_client, messages, system, TaskClassification
    )
