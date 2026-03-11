from fastapi import APIRouter, HTTPException
from functools import lru_cache
import logging

from app.schemas.v3.api import APIResult
from app.services.v3.excuse_store import ExcuseStore

router = APIRouter()
logger = logging.getLogger(__name__)


@lru_cache
def _get_excuse_store() -> ExcuseStore:
    from app.infra.v3.redis_client import get_redis
    return ExcuseStore(get_redis())


@router.get("/get-excuse/{excuse_id}", response_model=APIResult, response_model_exclude_none=True)
def get_excuse(excuse_id: str) -> APIResult:
    try:
        result = _get_excuse_store().get(excuse_id)
    except Exception:
        logger.exception("Failed to fetch excuse from Redis. id=%s", excuse_id)
        raise HTTPException(503, "Excuse storage is unavailable.")
    if not result:
        raise HTTPException(404, "Not found this excuse")
    return result
