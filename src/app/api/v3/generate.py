from fastapi import APIRouter

from app.schemas.v3.api import APIGenerateRequest, APIRequestOptions, APIResult
from app.schemas.v3.prompt import PromptOptions
from app.services.v3.prompt_runner import Runner
from app.services.v3.pollen_runner import PollenRunner

router = APIRouter()

runner = Runner()
pollen_runner = PollenRunner()


def _resolve_pollen(options: APIRequestOptions | None) -> PromptOptions:
    if options is None:
        return PromptOptions(location="unknown", pollen_index="unknown", pollen_species="unknown")
    payload = {"options": options.model_dump()}
    try:
        return pollen_runner.run(payload)
    except Exception:
        return PromptOptions(location="unknown", pollen_index="unknown", pollen_species="unknown")

@router.post("/generate", response_model=APIResult)
def generate_response(req: APIGenerateRequest) -> APIResult:
    pollen = _resolve_pollen(req.options)
    return runner.generate(req, pollen)
