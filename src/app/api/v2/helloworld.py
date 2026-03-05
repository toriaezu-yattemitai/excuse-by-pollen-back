from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def test_response() -> dict[str, str]:
    return {"message": "Hello World"}
