import os

from upstash_redis import Redis
from app.schemas.v3.api import APIResult


class ExcuseStore:
    _USE_RELEASE_PREFIX_ENV = "REDIS_USE_RELEASE_PREFIX"

    def __init__(self, redis: Redis):
        self._redis = redis
        self._key_prefix = self._resolve_key_prefix()

    def _resolve_key_prefix(self) -> str:
        # Default to debug namespace unless release prefix is explicitly enabled.
        if os.getenv(self._USE_RELEASE_PREFIX_ENV) is not None:
            return "v3:"
        return "v3-debug:"

    def _key(self, excuse_id: str) -> str:
        if excuse_id.startswith(self._key_prefix):
            return excuse_id
        return f"{self._key_prefix}{excuse_id}"
        
    def insert(self, result: APIResult) -> None:
        if not isinstance(result, APIResult):
            raise TypeError("This result type is failed")
        key = self._key(result.id)
        value = result.model_dump_json()
        
        self._redis.set(key, value)
        
    def get(self, excuse_id: str) -> APIResult | None:
        raw = self._redis.get(self._key(excuse_id))
        # Backward compatibility for records saved before key prefixing.
        if raw is None:
            raw = self._redis.get(excuse_id)
        if not raw:
            return None
        
        if isinstance(raw, APIResult):
            return raw
        if isinstance(raw, dict):
            return APIResult.model_validate(raw)
        if isinstance(raw, bytes):
            return APIResult.model_validate_json(raw.decode("utf-8"))
        if isinstance(raw, str):
            return APIResult.model_validate_json(raw)
        
        return APIResult.model_validate(raw)
