from typing import Annotated
from pydantic import BaseModel, Field


class GenerationContext(BaseModel):
    symptpms: list[str]
    level: int
    target: str | None
    sotiatopm: str | None
    nuance: str | None


class GenerateRequest(BaseModel):
    inputs: GenerationContext
    options: dict[str, str]
    
    
class RetryRequest(BaseModel):
    previous_context: GenerationContext
    previous_excuse: str
    retry_instruction: str
    
    
class GenerationResult(BaseModel):
    excuse: str
    score: Annotated[int, Field(ge=0, le=100)]
    id: str
    user_inputs: GenerationContext