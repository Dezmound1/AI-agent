from pydantic import BaseModel, Field

class TaskClassification(BaseModel):
    category: str = Field(description="Категория: bug, feature, support, question")
    priority: str = Field(description="Приоритет: high, medium, low")
    summary: str = Field(description="Краткое описание в 1 предложение")

class AgentDecision(BaseModel):
    """Schema for agent decision."""
    reasoning: str
    action: str
    params: dict

