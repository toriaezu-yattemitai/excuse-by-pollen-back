from pydantic import BaseModel

from app.prompts.templates import (
    FALLBACK_NUANCE,
    FALLBACK_SITUATION,
    FALLBACK_TARGET,
    SYSTEM_INSTRUCTION,
    OUTPUT_SCHEMA,
)
from app.schemas.v2.common import Inputs
from app.schemas.v2.prompt import PromptOptions
from app.schemas.v2.api import APIGenerateRequest

import textwrap

def _resolve_text(value: str | None, fallback: str) -> str:
    return value if value is not None else fallback

def _model_validate(obj, cls):
    if not isinstance(obj, BaseModel):
        return TypeError("")
    
    return obj if isinstance(obj, cls) else APIGenerateRequest.model_validate(obj)


def generate_builder(inputs: Inputs, options: PromptOptions) -> str:
    inputs = inputs
    options = options
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
    
def retry_builder(previous_context: Inputs, previous_excuse: str, retry_instruction: str) -> str:
    previous_excuse = previous_excuse
    retry_instruction = retry_instruction
    
    inputs = previous_context
    target = _resolve_text(inputs.target, FALLBACK_TARGET)
    situation = _resolve_text(inputs.situation, FALLBACK_SITUATION)
    nuance = _resolve_text(inputs.nuance, FALLBACK_NUANCE)
    symptoms = "、".join(inputs.symptoms)


    USER_PROMPT = textwrap.dedent(f"""
    以下の条件で言い訳文を生成したところ、以下のようになりました。

    条件
    症状: {symptoms}
    つらさレベル: {inputs.level}
    相手: {target}
    状況: {situation}
    ニュアンス: {nuance}
    
    生成結果
    {previous_excuse}
    
    この条件で、さらに面白く話を盛ってください。
    新たな条件は以下です。
    
    新たな条件
    {retry_instruction}
    """)

    return (
    f"{SYSTEM_INSTRUCTION}"
    f"{USER_PROMPT}"
    f"{OUTPUT_SCHEMA}"
    )
