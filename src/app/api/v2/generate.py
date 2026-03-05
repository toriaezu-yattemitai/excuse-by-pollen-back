from fastapi import APIRouter

from app.schemas.v2.api import APIGenerateRequest, APIResult
from app.services.v2.prompt_runner import Runner

router = APIRouter()

runner = Runner()

@router.post("/api/v2/generate", response_model=APIResult)
def generate_response(req: APIGenerateRequest) -> APIResult:
    return runner.generate(req)
