from fastapi import Body, FastAPI

from app.llm.factory import get_llm_client
from app.llm.structured import get_structured_response
from app.schemas.agent import TaskClassification

app = FastAPI()


@app.get("/")
def read_root():

    return {"message": "Hello from ai-agent"}


@app.post("/{model}/chat")
async def chat(model: str, messages: list[dict] = Body(...), system: str = Body(...)):
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
    return await get_structured_response(llm_client, messages, system, TaskClassification)