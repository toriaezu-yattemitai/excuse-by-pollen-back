"API package"

from fastapi import APIRouter

from app.api.v1.endpoints import helloworld, dummy_interface

router = APIRouter()

router.include_router(helloworld.router, prefix="", tags=["Test"])
router.include_router(dummy_interface.router, prefix="", tags=["Dummys"])
