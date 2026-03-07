from app.prompts.templates import (
    FALLBACK_NUANCE,
    FALLBACK_SITUATION,
    FALLBACK_TARGET,
    SYSTEM_INSTRUCTION,
    OUTPUT_SCHEMA,
)
from app.schemas.v1 import PromptRequest

import textwrap

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


    USER_PROMPT = textwrap.dedent(f"""
    以下の条件で言い訳文を生成してください。

    症状: {symptoms}
    つらさレベル: {inputs.level}
    相手: {target}
    状況: {situation}
    ニュアンス: {nuance}
    最大文字数: {options.max_chars}
    """)

    return (
    f"{SYSTEM_INSTRUCTION}"
    f"{USER_PROMPT}"
    f"{OUTPUT_SCHEMA}"
    )
