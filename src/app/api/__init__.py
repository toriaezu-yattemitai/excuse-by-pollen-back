"API package"

from fastapi import APIRouter

from app.api.v2 import helloworld, generate, retry
from app.api.v3 import generate as generate_v3, retry as retry_v3

router = APIRouter()

router.include_router(helloworld.router, prefix="", tags=["Test"])
router.include_router(generate.router, prefix="", tags=["GenerateV2"])
router.include_router(retry.router, prefix="", tags=["RetryV2"])
router.include_router(generate_v3.router, prefix="/v3", tags=["GenerateV3"])
router.include_router(retry_v3.router, prefix="/v3", tags=["RetryV3"])
