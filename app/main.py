from fastapi import Body, FastAPI

from app.llm.factory import get_llm_client

app = FastAPI()


@app.get("/")
def read_root():

    return {"message": "Hello from ai-agent"}


@app.post("/{model}/chat")
async def chat(model: str, messages: list[dict] = Body(...), system: str = Body(...)):
    llm_client = get_llm_client(model)
    return await llm_client.chat(messages, system)