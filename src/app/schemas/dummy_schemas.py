from typing import Annotated
from pydantic import BaseModel, Field


class GenerationContext(BaseModel):
    symptoms: list[str]
    level: int
    target: str | None
    situation: str | None
    nuance: str | None


class GenerateRequest(BaseModel):
    inputs: GenerationContext
    options: dict[str, str | int] = Field(default_factory=dict)
    
    
class RetryRequest(BaseModel):
    previous_context: GenerationContext
    previous_excuse: str
    retry_instruction: str
    
    
class GenerationResult(BaseModel):
    excuse: str
    score: Annotated[int, Field(ge=0, le=100)]
    id: str
    used_inputs: GenerationContext
