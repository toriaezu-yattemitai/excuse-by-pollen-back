from fastapi import APIRouter
from functools import lru_cache
import logging

from app.schemas.v3.api import APIRetryRequest, APIRequestOptions, APIResult
from app.schemas.v3.prompt import PromptOptions
from app.services.v3.prompt_runner import Runner
from app.services.v3.pollen_runner import PollenRunner
from app.services.v3.excuse_store import ExcuseStore

router = APIRouter()
logger = logging.getLogger(__name__)

@lru_cache
def _get_runner() -> Runner:
    return Runner()


@lru_cache
def _get_pollen_runner() -> PollenRunner:
    return PollenRunner()


@lru_cache
def _get_excuse_store() -> ExcuseStore:
    from app.infra.v3.redis_client import get_redis
    return ExcuseStore(get_redis())


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

@router.post("/retry", response_model=APIResult, response_model_exclude_none=True)
def retry_response(req: APIRetryRequest) -> APIResult:
    pollen = _resolve_pollen(req.options)
    result =  _get_runner().retry(req, pollen)
    try:
        _get_excuse_store().insert(result)
    except Exception:
        logger.exception("Failed to persist retried excuse. id=%s", result.id)
    return result
