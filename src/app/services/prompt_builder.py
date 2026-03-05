from app.prompts.templates import (
    FALLBACK_NUANCE,
    FALLBACK_SITUATION,
    FALLBACK_TARGET,
    SYSTEM_INSTRUCTION,
)
from app.schemas.v1 import PromptRequest


def _resolve_text(value: str | None, fallback: str) -> str:
    return value if value is not None else fallback


def build_prompt(payload: PromptRequest | dict) -> str:
    request = payload if isinstance(payload, PromptRequest) else PromptRequest.model_validate(payload)
    inputs = request.inputs
    options = request.options

    target = _resolve_text(inputs.target, FALLBACK_TARGET)
    situation = _resolve_text(inputs.situation, FALLBACK_SITUATION)
    nuance = _resolve_text(inputs.nuance, FALLBACK_NUANCE)
    symptoms = "、".join(inputs.symptoms)

    return (
        f"{SYSTEM_INSTRUCTION}\n\n"
        "以下の条件で、言い訳文を1つ作成してください。\n"
        f"- 症状: {symptoms}\n"
        f"- つらさレベル: {inputs.level}\n"
        f"- 相手: {target}\n"
        f"- 状況: {situation}\n"
        f"- ニュアンス: {nuance}\n"
        f"- 最大文字数: {options.max_chars}文字\n\n"
        "出力条件:\n"
        "- 日本語のみ\n"
        "- 言い訳文だけを返す\n"
        "- 最大文字数を超えない\n"
        "- 不自然な言い回しは避ける\n"
    )
