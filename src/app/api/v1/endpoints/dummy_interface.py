import uuid

from fastapi import APIRouter

from back.src.app.schemas.v1.prompt import GenerationResult, PromptRequest, RetryRequest

router = APIRouter()


@router.post("/generate", response_model=GenerationResult)
async def generate_response(req: PromptRequest) -> GenerationResult:
    return GenerationResult(
        excuse="この後のMTGですが、花粉の影響で鼻水に溺れてしまっているので、少し遅れます。",
        score=60,
        id=str(uuid.uuid4().hex[:10]),
        used_inputs=req.inputs,
    )


@router.post("/retry", response_model=GenerationResult)
async def retry_response(req: RetryRequest) -> GenerationResult:
    return GenerationResult(
        excuse="この後のMTGですが、現在、花粉前線との全面戦争の最中にあり、私の鼻腔が事実上の内海と化して鼻水の大洪水が発生しております。呼吸ひとつに命運を賭ける状況で、ティッシュ消費量は国家備蓄レベルに到達しました。必ず生還して向かいますが、到着が少々遅れます。",
        score=95,
        id=str(uuid.uuid4().hex[:10]),
        used_inputs=req.previous_context,
    )
