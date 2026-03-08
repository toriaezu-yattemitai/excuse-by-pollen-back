from fastapi import APIRouter
from functools import lru_cache

from app.schemas.v2.api import APIGenerateRequest, APIResult
from app.services.v2.prompt_runner import Runner

router = APIRouter()

@lru_cache
def _get_runner() -> Runner:
    return Runner()

@router.post("/generate", response_model=APIResult)
def generate_response(req: APIGenerateRequest) -> APIResult:
    return _get_runner().generate(req)
