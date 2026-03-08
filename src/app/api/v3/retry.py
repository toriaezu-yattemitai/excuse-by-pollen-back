from fastapi import APIRouter

from app.schemas.v3.api import APIRetryRequest, APIRequestOptions, APIResult
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

@router.post("/retry", response_model=APIResult)
def retry_response(req: APIRetryRequest) -> APIResult:
    pollen = _resolve_pollen(req.options)
    return runner.retry(req, pollen)
