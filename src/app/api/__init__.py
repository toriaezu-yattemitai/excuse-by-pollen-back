"API package"

from fastapi import APIRouter

from app.api.v1.endpoints import helloworld

router = APIRouter()

router.include_router(helloworld.router, prefix="", tags=["Test"])
