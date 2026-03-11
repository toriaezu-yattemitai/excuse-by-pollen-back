import os
from functools import lru_cache
from upstash_redis import Redis

@lru_cache
def get_redis() -> Redis:
    return Redis(
        url=os.environ["UPSTASH_REDIS_REST_URL"],
        token=os.environ["UPSTASH_REDIS_REST_TOKEN"]
    )