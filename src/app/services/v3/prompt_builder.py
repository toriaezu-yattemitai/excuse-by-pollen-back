from pydantic import BaseModel

from app.prompts.templates import (
    FALLBACK_NUANCE,
    FALLBACK_SITUATION,
    FALLBACK_TARGET,
    SYSTEM_INSTRUCTION,
    OUTPUT_SCHEMA,
)
from app.schemas.v3.api import APIRequestOptions
from app.schemas.v3.common import Inputs
from app.schemas.v3.prompt import PromptOptions as PollenOptions

import textwrap


def _resolve_text(value: str | None, fallback: str) -> str:
    return value if value is not None else fallback


def _validate_inputs(value: Inputs | dict) -> Inputs:
    if isinstance(value, Inputs):
        return value
    if isinstance(value, BaseModel):
        value = value.model_dump()
    return Inputs.model_validate(value)


def _validate_options(value: APIRequestOptions | dict | None) -> APIRequestOptions:
    if value is None:
        return APIRequestOptions()
    if isinstance(value, APIRequestOptions):
        return value
    if isinstance(value, BaseModel):
        value = value.model_dump()
    return APIRequestOptions.model_validate(value)


def _validate_non_empty_text(name: str, value: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{name} must be a string")
    text = value.strip()
    if not text:
        raise ValueError(f"{name} must not be empty")
    return text


def _safe_text(value: object, fallback: str = "unknown") -> str:
    if isinstance(value, str):
        text = value.strip()
        if text:
            return text
    return fallback


def _validate_pollen(value: PollenOptions | dict | None) -> PollenOptions | None:
    if value is None:
        return None
    if isinstance(value, PollenOptions):
        return value
    if isinstance(value, BaseModel):
        value = value.model_dump()
    if not isinstance(value, dict):
        return None

    # Backward-compatible keys are accepted so callers can gradually migrate.
    location = _safe_text(value.get("location"))
    pollen_index = _safe_text(
        value.get("pollen_index", value.get("pollen-index", value.get("index")))
    )
    pollen_species = _safe_text(
        value.get("pollen_species", value.get("pollen-species", value.get("species")))
    )

    return PollenOptions(
        location=location,
        pollen_index=pollen_index,
        pollen_species=pollen_species,
    )


def _render_pollen_text(value: PollenOptions | dict | None) -> str:
    pollen = _validate_pollen(value)
    if pollen is None:
        return ""
    return textwrap.dedent(f"""
    花粉情報:
    地域: {pollen.location}
    花粉指数: {pollen.pollen_index}
    花粉の種類: {pollen.pollen_species}
    """)


def generate_builder(inputs: Inputs | dict, options: APIRequestOptions | dict | None, pollen: PollenOptions | dict | None = None) -> str:
    inputs = _validate_inputs(inputs)
    options = _validate_options(options)
    target = _resolve_text(inputs.target, FALLBACK_TARGET)
    situation = _resolve_text(inputs.situation, FALLBACK_SITUATION)
    nuance = _resolve_text(inputs.nuance, FALLBACK_NUANCE)
    symptoms = "、".join(inputs.symptoms)
    pollen_text = _render_pollen_text(pollen)
    
    USER_PROMPT = textwrap.dedent(f"""
    以下の条件で言い訳文を生成してください。
    
    {pollen_text}
    
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
    
def retry_builder(previous_context: Inputs | dict, previous_excuse: str, retry_instruction: str, pollen: PollenOptions | dict | None = None) -> str:
    inputs = _validate_inputs(previous_context)
    previous_excuse = _validate_non_empty_text("previous_excuse", previous_excuse)
    retry_instruction = _validate_non_empty_text("retry_instruction", retry_instruction)

    target = _resolve_text(inputs.target, FALLBACK_TARGET)
    situation = _resolve_text(inputs.situation, FALLBACK_SITUATION)
    nuance = _resolve_text(inputs.nuance, FALLBACK_NUANCE)
    symptoms = "、".join(inputs.symptoms)
    pollen_text = _render_pollen_text(pollen)


    USER_PROMPT = textwrap.dedent(f"""
    以下の条件で作成した前回の言い訳を、同じ設定のまま「もっと面白く」改善してください。
    
    {pollen_text}

    【維持する設定】
    症状: {symptoms}
    つらさレベル: {inputs.level}
    相手: {target}
    状況: {situation}
    ニュアンス: {nuance}
    
    【前回の言い訳】
    {previous_excuse}

    
    この条件で、さらに面白く話を盛ってください。
    新たな条件は以下です。
    
    【今回の追加指示】
    {retry_instruction}
    
    【改善ルール】
    - 前回より「意外性」と「オチ」を強くする
    - 誇張はOKだが、意味不明にはしない（会話として通ること）
    - 1文目で引き込み、最後にクスッとする着地を作る
    - 相手に伝わる自然な日本語にする
    - 不快・攻撃的・差別的な表現は禁止

    """)

    return (
    f"{SYSTEM_INSTRUCTION}"
    f"{USER_PROMPT}"
    f"{OUTPUT_SCHEMA}"
    )
