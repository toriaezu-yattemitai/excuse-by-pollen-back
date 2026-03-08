from fastapi import APIRouter
from functools import lru_cache

from app.schemas.v2.api import APIRetryRequest, APIResult
from app.services.v2.prompt_runner import Runner

router = APIRouter()

@lru_cache
def _get_runner() -> Runner:
    return Runner()

@router.post("/retry", response_model=APIResult)
def retry_response(req: APIRetryRequest) -> APIResult:
    return _get_runner().retry(req)
