"""
LLM interpretation for Chinese metaphysics charts.

Supports OpenAI and Anthropic APIs.
"""

from __future__ import annotations

from typing import Optional

from tianji.config import get_config, LLMConfig
from tianji.llm.prompts import (
    BAZI_SYSTEM_PROMPT,
    BAZI_ANALYSIS_TEMPLATE,
    LIUYAO_SYSTEM_PROMPT,
    LIUYAO_ANALYSIS_TEMPLATE,
    DISCLAIMER_ZH,
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
            "No API key configured. Set OPENAI_API_KEY or ANTHROPIC_API_KEY, "
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
    from tianji.bazi.ten_gods import compute_ten_gods
    from tianji.bazi.five_elements import analyze_five_elements

    gods = compute_ten_gods(chart)
    elements = analyze_five_elements(chart)

    user_prompt = BAZI_ANALYSIS_TEMPLATE.format(
        year=chart.year,
        month=chart.month,
        day=chart.day,
        hour=chart.hour,
        gender=getattr(chart, "gender", "男"),
        year_pillar=chart.year_pillar,
        month_pillar=chart.month_pillar,
        day_pillar=chart.day_pillar,
        hour_pillar=chart.hour_pillar,
        day_master=chart.day_pillar.stem,
        ten_gods=gods,
        five_elements=elements,
        missing_elements=elements.get("missing", "无") if isinstance(elements, dict) else "N/A",
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
        analysis: Result from liuyao.analysis.full_analysis()
        question: The question being asked
        config: Optional LLM configuration override

    Returns:
        Natural language interpretation string
    """
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
