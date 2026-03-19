"""
十神 (Ten Gods) — the ten divine stars of BaZi.

The Ten Gods describe the relationship between the Day Master (日主) and
every other heavenly stem in the chart. They reveal personality traits,
relationships, career tendencies, and life patterns.
"""

from __future__ import annotations

from dataclasses import dataclass

from tianji.calendar.heavenly_stems import (
    HeavenlyStem,
    stem_relationship,
    ELEMENT_PRODUCES,
    ELEMENT_CONQUERS,
)


# Ten God names and their meanings
TEN_GOD_INFO: dict[str, dict] = {
    "比肩": {
        "name": "比肩",
        "english": "Companion (Parallel Shoulder)",
        "meaning": "兄弟、朋友、竞争、自我意志",
        "polarity": "same",
    },
    "劫财": {
        "name": "劫财",
        "english": "Rob Wealth (Sibling)",
        "meaning": "兄弟、竞争、劫夺财运",
        "polarity": "different",
    },
    "食神": {
        "name": "食神",
        "english": "Eating God",
        "meaning": "才华、口福、福气、艺术",
        "polarity": "same",
    },
    "伤官": {
        "name": "伤官",
        "english": "Hurting Officer",
        "meaning": "才华横溢、叛逆、克官",
        "polarity": "different",
    },
    "偏财": {
        "name": "偏财",
        "english": "Indirect Wealth",
        "meaning": "偏财运、父亲（男命）、应变能力",
        "polarity": "same",
    },
    "正财": {
        "name": "正财",
        "english": "Direct Wealth",
        "meaning": "正当财富、配偶（男命）、踏实",
        "polarity": "different",
    },
    "七杀": {
        "name": "七杀",
        "english": "Seven Killings",
        "meaning": "权威、压力、危险、军警",
        "polarity": "same",
    },
    "正官": {
        "name": "正官",
        "english": "Direct Officer",
        "meaning": "官职、配偶（女命）、规范",
        "polarity": "different",
    },
    "偏印": {
        "name": "偏印",
        "english": "Indirect Resource",
        "meaning": "偏门学问、宗教、孤僻",
        "polarity": "same",
    },
    "正印": {
        "name": "正印",
        "english": "Direct Resource",
        "meaning": "母亲、学业、正统、慈悲",
        "polarity": "different",
    },
}


@dataclass
class TenGodResult:
    """Result of Ten God calculation for one stem."""
    stem: HeavenlyStem
    ten_god: str
    english: str
    meaning: str

    def __str__(self) -> str:
        return f"{self.stem.char}→{self.ten_god}"


def compute_ten_god(day_master: HeavenlyStem, other_stem: HeavenlyStem) -> TenGodResult:
    """
    Compute the Ten God (十神) of `other_stem` relative to Day Master.

    Args:
        day_master: The Day Master (日主) heavenly stem
        other_stem: Another heavenly stem to compare

    Returns:
        TenGodResult with the ten god name and details
    """
    god_name = stem_relationship(day_master, other_stem)
    info = TEN_GOD_INFO[god_name]
    return TenGodResult(
        stem=other_stem,
        ten_god=god_name,
        english=info["english"],
        meaning=info["meaning"],
    )


def compute_all_ten_gods(
    day_master: HeavenlyStem,
    other_stems: list[HeavenlyStem],
) -> list[TenGodResult]:
    """
    Compute Ten Gods for multiple stems against the Day Master.

    Args:
        day_master: The Day Master stem
        other_stems: List of other stems (year, month, hour stems)

    Returns:
        List of TenGodResult, one per stem
    """
    results = []
    for stem in other_stems:
        result = compute_ten_god(day_master, stem)
        results.append(result)
    return results


def ten_gods_from_chart(chart) -> dict[str, TenGodResult]:
    """
    Extract Ten Gods from a BaZiChart for all non-Day-Master stems.

    Args:
        chart: A BaZiChart instance

    Returns:
        Dictionary mapping position name to TenGodResult
    """
    dm = chart.day_master
    positions = {
        "年干": chart.year_pillar.stem,
        "月干": chart.month_pillar.stem,
        "时干": chart.hour_pillar.stem,
    }

    results = {}
    for pos, stem in positions.items():
        results[pos] = compute_ten_god(dm, stem)

    # Also compute for branch hidden stems
    for pillar_name, pillar in [
        ("年支", chart.year_pillar.branch),
        ("月支", chart.month_pillar.branch),
        ("日支", chart.day_pillar.branch),
        ("时支", chart.hour_pillar.branch),
    ]:
        hidden_stems = pillar.get_hidden_stems()
        if hidden_stems:
            # Primary hidden stem
            results[f"{pillar_name}藏干"] = compute_ten_god(dm, hidden_stems[0])

    return results


def display_ten_gods(chart) -> None:
    """Print a Ten Gods table for a BaZiChart."""
    gods = ten_gods_from_chart(chart)
    print("\n十神对照表 (Ten Gods Reference)")
    print("─" * 40)
    print(f"日主: {chart.day_master.char} ({chart.day_master.element.value}{chart.day_master.polarity.value})")
    print("─" * 40)
    for pos, result in gods.items():
        print(f"  {pos}: {result.stem.char} → {result.ten_god} ({result.english})")
    print("─" * 40)
