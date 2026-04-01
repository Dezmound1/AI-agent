from pydantic import BaseModel

class TaskClassification(BaseModel):
    """Schema for task classification."""
    category: str
    priority: str
    summery: str

class AgentDecision(BaseModel):
    """Schema for agent decision."""
    reasoning: str
    action: str
    params: dict

