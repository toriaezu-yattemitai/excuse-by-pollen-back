from fastapi import APIRouter


from app.schemas.dummy_schemas import GenerationContext, GenerationResult, GenerateRequest, RetryRequest

router = APIRouter()


@router.post("/generate")
async def generate_response(req: GenerateRequest):
    
    
    return {
        "excuse": "この後のMTGですが、花粉の影響で鼻水に溺れてしまっているので、少し遅れます。",
        "score": 60,
        "id": "abc-123",
        "user_inputs": dict(req.inputs)
    }
    
@router.post("/retry")
async def retry_response(req: RetryRequest):
    
    return {
        "excuse": "この後のMTGですが、現在、花粉前線との全面戦争の最中にあり、私の鼻腔が事実上の内海と化して鼻水の大洪水が発生しております。呼吸ひとつに命運を賭ける状況で、ティッシュ消費量は国家備蓄レベルに到達しました。必ず生還して向かいますが、到着が少々遅れます。",
        "score": 95,
        "id": "abc-123",
        "user_inputs": dict(req.previous_context)
    }
    