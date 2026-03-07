from typing import Annotated
from pydantic import BaseModel, Field, field_validator

from .common import Inputs
from .prompt import PromptOptions


class _LocationValues(BaseModel):
    latitude: float
    longitude: float
    
class APIRequestOptions(BaseModel):
    max_chars: int = Field(default=220, ge=1)
    location: _LocationValues | None = None


class APIResponseOptions(BaseModel):
    badges: PromptOptions


class APIGenerateRequest(BaseModel):
    inputs: Inputs
    options: APIRequestOptions | None = None


class APIRetryRequest(BaseModel):
    previous_context: Inputs
    previous_excuse: str
    retry_instruction: str
    options: APIRequestOptions | None = None
    
    @field_validator("previous_excuse", "retry_instruction", mode="before")
    @classmethod
    def normalize_text(cls, value: str | None) -> str | None:
        if value is None or not isinstance(value, str):
            raise ValueError("previous_excuse and retry_instruction must be a string")
        text = value.strip()
        return text

class APIResult(BaseModel):
    excuse: str
    score: Annotated[int, Field(ge=0, le=100)]
    id: str
    used_inputs: Inputs
    options: APIResponseOptions | None = None