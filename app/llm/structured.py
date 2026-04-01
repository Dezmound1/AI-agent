import json

from pydantic import BaseModel
from .base import BaseLLMClient


def _parse_llm_response(response: str, model_class: type[BaseModel]) -> BaseModel:
    """
    Parse the LLM response and return a Pydantic model.

    Parameters
    ----------
    response: str
        The response from the LLM.
    model_class: type[BaseModel]
        The Pydantic model to parse the response into.

    Returns
    -------
    BaseModel
        The parsed response.
    """
    json_response = response.strip()
    if json_response.startswith("```"):
        json_response = json_response.split("\n", 1)[1]
        json_response = json_response.rsplit("```", 1)[0]
    return model_class.model_validate(json.loads(json_response))


async def get_structured_response(
    client: BaseLLMClient, messages: list[dict], system: str, response_model: type[BaseModel], max_retries: int = 2
) -> BaseModel:
    """Get a structured response from the LLM."""

    history = [messages]

    for retry_iter in range(max_retries + 1):
        response = await client.chat(messages, system)

        try:
            return _parse_llm_response(response, response_model)
        except Exception as e:
            if retry_iter == max_retries:
                raise ValueError("Failed to parse LLM response.")

            history.append({"role": "assistant", "content": response})
            history.append(
                {
                    "role": "user",
                    "content": f"Not valid answer, there is an error {e}. Please try again and return only Json.",
                },
            )
