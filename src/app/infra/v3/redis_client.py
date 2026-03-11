import os
from functools import lru_cache

from dotenv import load_dotenv
from upstash_redis import Redis


@lru_cache
def get_redis() -> Redis:
    load_dotenv()
    url = os.getenv("UPSTASH_REDIS_REST_URL")
    token = os.getenv("UPSTASH_REDIS_REST_TOKEN")
    if not url or not token:
        raise RuntimeError(
            "UPSTASH_REDIS_REST_URL / UPSTASH_REDIS_REST_TOKEN is not set."
        )

    return Redis(
        url=url,
        token=token,
    )
