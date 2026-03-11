from upstash_redis import Redis
from app.schemas.v3.api import APIResult

class ExcuseStore:
    def __init__(self, redis: Redis):
        self._redis = redis
        
    def insert(self, result: APIResult) -> None:
        if not isinstance(result, APIResult):
            raise TypeError("This result type is failed")
        key = result.id
        value = result.model_dump_json()
        
        self._redis.set(key, value)
        
    def get(self, excuse_id: str) -> APIResult | None:
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