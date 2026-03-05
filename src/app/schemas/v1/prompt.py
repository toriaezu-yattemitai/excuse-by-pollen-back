from typing import Annotated
from pydantic import BaseModel, Field, field_validator


class PromptInputs(BaseModel):
    symptoms: list[str] = Field(..., min_length=1)
    level: int = Field(..., ge=1)
    target: str | None = None
    situation: str | None = None
    nuance: str | None = None

    @field_validator("symptoms")
    @classmethod
    def validate_symptoms(cls, value: list[str]) -> list[str]:
        cleaned = [item.strip() for item in value if item and item.strip()]
        if not cleaned:
            raise ValueError("symptoms must contain at least one non-empty item")
        return cleaned

    @field_validator("target", "situation", "nuance", mode="before")
    @classmethod
    def normalize_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        if not isinstance(value, str):
            raise ValueError("target, situation, and nuance must be a string")
        text = value.strip()
        return text or None


class PromptOptions(BaseModel):
    max_chars: int = Field(default=220, ge=1)


class PromptRequest(BaseModel):
    inputs: PromptInputs
    options: PromptOptions = Field(default_factory=PromptOptions)


class RetryRequest(BaseModel):
    previous_context: PromptInputs
    previous_excuse: str
    retry_instruction: str
    
    @field_validator("previous_excuse", "retry_instruction", mode="before")
    @classmethod
    def normalize_text(cls, value: str | None) -> str | None:
        if value is None or not isinstance(value, str):
            raise ValueError("previous_excuse and retry_instruction must be a string")
        text = value.strip()
        return text
    

class GenerationResult(BaseModel):
    excuse: str
    score: Annotated[int, Field(ge=0, le=100)]
    id: str
    used_inputs: PromptInputs
