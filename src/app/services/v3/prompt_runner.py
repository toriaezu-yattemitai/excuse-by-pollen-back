import os
import uuid
import json

from typing import Any

from dotenv import load_dotenv

from google import genai
from google.genai import types

from app.services.v3.prompt_builder import generate_builder, retry_builder

from app.schemas.v3.common import Inputs
from app.schemas.v3.api import APIGenerateRequest, APIRetryRequest, APIResult, APIResponseOptions
from app.schemas.v3.prompt import PromptOptions as PollenOptions, PromptResult

from app.prompts.settings import MODEL_NAME


# Private functions
def _load_api_key() -> str:
    load_dotenv()
    
    _api_key = os.getenv("GEMINI_API_KEY")

    if not _api_key:
        raise RuntimeError("GEMINI_API_KEY is not set. Please add it to .env.")
    
    return _api_key
    
# Public functions
class Runner:
    def __init__(self, *, api_key: str | None = None, model_name: str | None = None):
        self._api_key = api_key or _load_api_key()
        self._model_name = model_name or MODEL_NAME
        
        
        self._client = genai.Client(api_key=self._api_key)
        
    def _push_gemini(self, prompt: str):
        return self._client.models.generate_content(
            model= self._model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=PromptResult
            )
        )

    def _to_prompt_result(self, result: Any) -> PromptResult:
        parsed = getattr(result, "parsed", None)
        if parsed is not None:
            if isinstance(parsed, PromptResult):
                return parsed
            return PromptResult.model_validate(parsed)

        text = getattr(result, "text", None)
        if not isinstance(text, str) or not text.strip():
            raise RuntimeError("Gemini response is empty.")

        return PromptResult.model_validate(json.loads(text))
        
    def generate(self, req: APIGenerateRequest, pollen_result: PollenOptions) -> APIResult:
        
        inputs: Inputs = req.inputs
        options = req.options
        
        prompt = generate_builder(inputs, options, pollen_result)

        result = self._push_gemini(prompt)
        prompt_result = self._to_prompt_result(result)
        
        result_id = str(uuid.uuid4())
        return APIResult(
            excuse=prompt_result.excuse,
            score=prompt_result.score,
            id=result_id, 
            used_inputs=inputs,
            options=APIResponseOptions(badges=pollen_result),
        )
        
    def retry(self, req: APIRetryRequest) -> APIResult:
        
        previous_context = req.previous_context
        previous_excuse = req.previous_excuse
        retry_instruction = req.retry_instruction
        
        prompt = retry_builder(previous_context, previous_excuse, retry_instruction)
        
        result = self._push_gemini(prompt)
        prompt_result = self._to_prompt_result(result)
        
        result_id = str(uuid.uuid4())
        return APIResult(
            excuse=prompt_result.excuse,
            score=prompt_result.score,
            id=result_id, 
            used_inputs=previous_context
        )
    
