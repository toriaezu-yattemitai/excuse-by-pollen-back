from typing import Annotated
from pydantic import BaseModel, Field, field_validator


class PromptResult(BaseModel):
    excuse: str
    score: Annotated[int, Field(ge=0, le=100)]

class PromptOptions(BaseModel):
    max_chars: int = Field(default=220, ge=1)
