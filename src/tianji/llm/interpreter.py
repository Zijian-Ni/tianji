"""
LLM interpretation for Chinese metaphysics charts.

Supports OpenAI and Anthropic APIs.
"""

from __future__ import annotations

from typing import Optional

from tianji.config import LLMConfig, get_config
from tianji.llm.prompts import (
    BAZI_ANALYSIS_TEMPLATE,
    BAZI_SYSTEM_PROMPT,
    DISCLAIMER_ZH,
    LIUYAO_ANALYSIS_TEMPLATE,
    LIUYAO_SYSTEM_PROMPT,
)


def _call_openai(system: str, user: str, config: LLMConfig) -> str:
    """Call OpenAI API."""
    try:
        from openai import OpenAI
    except ImportError:
        raise ImportError("pip install openai  — required for LLM interpretation")

    client = OpenAI(api_key=config.api_key, base_url=config.base_url)
    response = client.chat.completions.create(
        model=config.model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=config.temperature,
        max_tokens=config.max_tokens,
    )
    return response.choices[0].message.content or ""


def _call_anthropic(system: str, user: str, config: LLMConfig) -> str:
    """Call Anthropic API."""
    try:
        import anthropic
    except ImportError:
        raise ImportError("pip install anthropic  — required for LLM interpretation")

    client = anthropic.Anthropic(api_key=config.api_key)
    response = client.messages.create(
        model=config.model,
        max_tokens=config.max_tokens,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    return response.content[0].text


def _call_llm(system: str, user: str, config: Optional[LLMConfig] = None) -> str:
    """Route to the appropriate LLM provider."""
    cfg = config or get_config().llm
    if not cfg.api_key:
        raise ValueError(
            "No API key configured. Set OPENAI_API_KEY, "
            "or pass LLMConfig with api_key."
        )

    if cfg.provider == "anthropic":
        return _call_anthropic(system, user, cfg)
    else:
        return _call_openai(system, user, cfg)


def interpret_bazi(
    chart,
    config: Optional[LLMConfig] = None,
) -> str:
    """
    Interpret a BaZi chart using LLM.

    Args:
        chart: A BaZiChart instance
        config: Optional LLM configuration override

    Returns:
        Natural language interpretation string
    """
    from tianji.bazi.five_elements import elements_from_chart
    from tianji.bazi.ten_gods import ten_gods_from_chart

    gods = ten_gods_from_chart(chart)
    elements = elements_from_chart(chart)

    user_prompt = BAZI_ANALYSIS_TEMPLATE.format(
        year=chart.birth_dt.year,
        month=chart.birth_dt.month,
        day=chart.birth_dt.day,
        hour=chart.birth_dt.hour,
        gender=getattr(chart, "gender", "男"),
        year_pillar=chart.year_pillar,
        month_pillar=chart.month_pillar,
        day_pillar=chart.day_pillar,
        hour_pillar=chart.hour_pillar,
        day_master=chart.day_pillar.stem,
        ten_gods="、".join(f"{pos} {god.ten_god}" for pos, god in gods.items()),
        five_elements=elements.summary(),
        missing_elements="、".join(e.value for e in elements.missing_elements()) or "无",
    )

    result = _call_llm(BAZI_SYSTEM_PROMPT, user_prompt, config)
    return result + DISCLAIMER_ZH


def interpret_liuyao(
    analysis: dict,
    question: str = "综合运势",
    config: Optional[LLMConfig] = None,
) -> str:
    """
    Interpret a Liu Yao hexagram using LLM.

    Args:
        analysis: LiuYaoAnalysis.to_dict() result or a legacy flat result
        question: The question being asked
        config: Optional LLM configuration override

    Returns:
        Natural language interpretation string
    """
    from tianji.liuyao.hexagram import get_hexagram_by_number

    primary = analysis.get("primary_hexagram") or {}
    if primary.get("number"):
        hexagram = get_hexagram_by_number(primary["number"])
        changed = analysis.get("changed_hexagram") or {}
        analysis = {**analysis, "hexagram_name": hexagram.name, "hexagram_symbol": hexagram.symbol,
                    "upper_trigram": hexagram.upper.name, "lower_trigram": hexagram.lower.name,
                    "transformed_name": changed.get("name", "")}

    transformed_section = ""
    if analysis.get("transformed_name"):
        transformed_section = f"**变卦**：{analysis['transformed_name']}（{analysis.get('transformed_symbol', '')}）"

    lines_detail = "\n".join(
        f"  {i+1}. {line}" for i, line in enumerate(analysis.get("lines", []))
    )

    user_prompt = LIUYAO_ANALYSIS_TEMPLATE.format(
        hexagram_name=analysis.get("hexagram_name", ""),
        hexagram_symbol=analysis.get("hexagram_symbol", ""),
        upper_trigram=analysis.get("upper_trigram", ""),
        lower_trigram=analysis.get("lower_trigram", ""),
        transformed_section=transformed_section,
        lines_detail=lines_detail,
        moving_lines=analysis.get("moving_lines", "无"),
    )

    user_prompt = f"问事：{question}\n\n{user_prompt}"

    result = _call_llm(LIUYAO_SYSTEM_PROMPT, user_prompt, config)
    return result + DISCLAIMER_ZH
