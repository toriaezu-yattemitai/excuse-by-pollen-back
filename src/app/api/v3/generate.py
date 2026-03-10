from fastapi import APIRouter
from functools import lru_cache

from app.schemas.v3.api import APIGenerateRequest, APIRequestOptions, APIResult
from app.schemas.v3.prompt import PromptOptions
from app.services.v3.prompt_runner import Runner
from app.services.v3.pollen_runner import PollenRunner

router = APIRouter()

@lru_cache
def _get_runner() -> Runner:
    return Runner()


@lru_cache
def _get_pollen_runner() -> PollenRunner:
    return PollenRunner()


def _resolve_pollen(options: APIRequestOptions | None) -> PromptOptions | None:
    if options is None:
        return None
    if options.location is None:
        return None
    payload = {"options": options.model_dump()}
    try:
        return _get_pollen_runner().run(payload)
    except Exception:
        return None

@router.post("/generate", response_model=APIResult, response_model_exclude_none=True)
def generate_response(req: APIGenerateRequest) -> APIResult:
    pollen = _resolve_pollen(req.options)
    return _get_runner().generate(req, pollen)
