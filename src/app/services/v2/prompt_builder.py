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

import textwrap


def _resolve_text(value: str | None, fallback: str) -> str:
    return value if value is not None else fallback


def _validate_inputs(value: Inputs | dict) -> Inputs:
    if isinstance(value, Inputs):
        return value
    if isinstance(value, BaseModel):
        value = value.model_dump()
    return Inputs.model_validate(value)


def _validate_options(value: PromptOptions | dict | None) -> PromptOptions:
    if value is None:
        return PromptOptions()
    if isinstance(value, PromptOptions):
        return value
    if isinstance(value, BaseModel):
        value = value.model_dump()
    return PromptOptions.model_validate(value)


def _validate_non_empty_text(name: str, value: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{name} must be a string")
    text = value.strip()
    if not text:
        raise ValueError(f"{name} must not be empty")
    return text


def generate_builder(inputs: Inputs | dict, options: PromptOptions | dict | None) -> str:
    inputs = _validate_inputs(inputs)
    options = _validate_options(options)
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
    
def retry_builder(previous_context: Inputs | dict, previous_excuse: str, retry_instruction: str) -> str:
    inputs = _validate_inputs(previous_context)
    previous_excuse = _validate_non_empty_text("previous_excuse", previous_excuse)
    retry_instruction = _validate_non_empty_text("retry_instruction", retry_instruction)

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
