"API package"

from fastapi import APIRouter

from app.api.v3 import generate, retry, helloworld

router = APIRouter()

router.include_router(helloworld.router, prefix="", tags=["Test"])
router.include_router(generate.router, prefix="", tags=["GenerateV3"])
router.include_router(retry.router, prefix="", tags=["RetryV3"])
