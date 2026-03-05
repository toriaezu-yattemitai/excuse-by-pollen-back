from typing import Annotated
from pydantic import BaseModel, Field, field_validator



class PromptOptions(BaseModel):
    max_chars: int = Field(default=220, ge=1)
