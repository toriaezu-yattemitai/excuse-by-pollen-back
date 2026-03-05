"API package"

from fastapi import APIRouter

from app.api.v2 import helloworld, generate, retry

router = APIRouter()

router.include_router(helloworld.router, prefix="", tags=["Test"])
router.include_router(generate.router, prefix="", tags=["GenerateV2"])
router.include_router(retry.router, prefix="", tags=["RetryV2"])
