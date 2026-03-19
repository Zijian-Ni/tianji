"""
日主强弱判断 (Day Master Strength Analysis)

Determines whether the Day Master (日主/日元) is strong (旺/身强) or weak (弱/身弱).
This is fundamental for BaZi interpretation.

Strength factors:
1. 得令 (Season support): Month branch supports day master's element
2. 得地 (Ground support): Day/hour branches support day master
3. 得势 (Momentum): Stems that are same element or that produce day master
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from tianji.calendar.heavenly_stems import Element, HeavenlyStem, ELEMENT_PRODUCES
from tianji.calendar.earthly_branches import EarthlyBranch


class StrengthLevel(str, Enum):
    """Day Master strength levels."""
    VERY_STRONG = "极旺"
    STRONG = "身强"
    NEUTRAL = "中和"
    WEAK = "身弱"
    VERY_WEAK = "极弱"


# Month support: which elements are rooted/strong in which month branch
# Each branch supports certain elements (旺相休囚死)
_MONTH_SUPPORT: dict[str, dict[Element, int]] = {
    # 寅卯月 (Spring / Wood) — Wood旺, Fire相, Water休, Metal囚, Earth死
    "寅": {Element.WOOD: 3, Element.FIRE: 2, Element.WATER: 1, Element.METAL: -1, Element.EARTH: -1},
    "卯": {Element.WOOD: 3, Element.FIRE: 2, Element.WATER: 1, Element.METAL: -1, Element.EARTH: -1},
    # 辰月 — Earth旺
    "辰": {Element.EARTH: 2, Element.WOOD: 1, Element.FIRE: 1, Element.WATER: -1, Element.METAL: 0},
    # 巳午月 (Summer / Fire)
    "巳": {Element.FIRE: 3, Element.EARTH: 2, Element.WOOD: 1, Element.WATER: -1, Element.METAL: -1},
    "午": {Element.FIRE: 3, Element.EARTH: 2, Element.WOOD: 1, Element.WATER: -1, Element.METAL: -1},
    # 未月 — Earth旺
    "未": {Element.EARTH: 2, Element.FIRE: 1, Element.METAL: 1, Element.WOOD: -1, Element.WATER: -1},
    # 申酉月 (Autumn / Metal)
    "申": {Element.METAL: 3, Element.WATER: 2, Element.EARTH: 1, Element.FIRE: -1, Element.WOOD: -1},
    "酉": {Element.METAL: 3, Element.WATER: 2, Element.EARTH: 1, Element.FIRE: -1, Element.WOOD: -1},
    # 戌月 — Earth旺
    "戌": {Element.EARTH: 2, Element.METAL: 1, Element.FIRE: 0, Element.WATER: -1, Element.WOOD: -1},
    # 亥子月 (Winter / Water)
    "亥": {Element.WATER: 3, Element.WOOD: 2, Element.METAL: 1, Element.FIRE: -1, Element.EARTH: -1},
    "子": {Element.WATER: 3, Element.WOOD: 2, Element.METAL: 1, Element.FIRE: -1, Element.EARTH: -1},
    # 丑月 — Earth旺
    "丑": {Element.EARTH: 2, Element.WATER: 1, Element.METAL: 1, Element.FIRE: -1, Element.WOOD: -1},
}


@dataclass
class DayMasterStrength:
    """Result of Day Master strength analysis."""
    day_master: HeavenlyStem
    strength_score: float
    level: StrengthLevel
    is_strong: bool
    factors: list[str]

    def display(self) -> None:
        """Print strength analysis."""
        print("\n日主强弱分析 (Day Master Strength)")
        print("─" * 40)
        print(f"  日主: {self.day_master.char} ({self.day_master.element.value}{self.day_master.polarity.value})")
        print(f"  强弱: {self.level.value} (score={self.strength_score:.2f})")
        print(f"  身{'强' if self.is_strong else '弱'}")
        if self.factors:
            print("  因素:")
            for f in self.factors:
                print(f"    - {f}")
        print("─" * 40)


def analyze_day_master_strength(chart) -> DayMasterStrength:
    """
    Analyze the strength of the Day Master.

    Args:
        chart: A BaZiChart instance

    Returns:
        DayMasterStrength with score and level
    """
    dm = chart.day_master
    dm_element = dm.element
    score = 0.0
    factors = []

    # 1. 得令 — Month branch support
    month_branch = chart.month_pillar.branch
    month_support = _MONTH_SUPPORT.get(month_branch.char, {})
    month_score = month_support.get(dm_element, 0)
    score += month_score
    if month_score > 0:
        factors.append(f"得令: {month_branch.char}月生{dm_element.value} (+{month_score})")
    elif month_score < 0:
        factors.append(f"失令: {month_branch.char}月克{dm_element.value} ({month_score})")

    # 2. 得地 — Branch support (all 4 branches, excluding month)
    for pillar, name in [
        (chart.year_pillar, "年支"),
        (chart.day_pillar, "日支"),
        (chart.hour_pillar, "时支"),
    ]:
        branch = pillar.branch
        hidden = branch.get_hidden_stems()
        for hs in hidden:
            if hs.element == dm_element:
                score += 0.5
                factors.append(f"得地: {name}{branch.char}藏{hs.char}({dm_element.value}) (+0.5)")
            elif ELEMENT_PRODUCES.get(hs.element) == dm_element:
                score += 0.3
                factors.append(f"得地: {name}藏干生日主 (+0.3)")

    # 3. 得势 — Stem support (year, month, hour stems)
    for stem, name in [
        (chart.year_pillar.stem, "年干"),
        (chart.month_pillar.stem, "月干"),
        (chart.hour_pillar.stem, "时干"),
    ]:
        if stem.element == dm_element:
            score += 1.0
            factors.append(f"得势: {name}{stem.char}比劫 (+1.0)")
        elif ELEMENT_PRODUCES.get(stem.element) == dm_element:
            score += 0.7
            factors.append(f"得势: {name}{stem.char}生日主 (+0.7)")

    # Determine level
    if score >= 6:
        level = StrengthLevel.VERY_STRONG
    elif score >= 3:
        level = StrengthLevel.STRONG
    elif score >= 1:
        level = StrengthLevel.NEUTRAL
    elif score >= -1:
        level = StrengthLevel.WEAK
    else:
        level = StrengthLevel.VERY_WEAK

    is_strong = score >= 1.5

    return DayMasterStrength(
        day_master=dm,
        strength_score=score,
        level=level,
        is_strong=is_strong,
        factors=factors,
    )
