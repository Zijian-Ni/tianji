"""
紫微斗数十二宫 (Zi Wei Dou Shu — 12 Palaces)

The 12 palaces form the framework of a Zi Wei chart.
Each palace governs a specific area of life.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Palace:
    """One of the 12 palaces (宫) in Zi Wei Dou Shu."""
    index: int       # 0–11
    name: str        # Palace name (e.g. 命宫)
    english: str     # English name
    branch: str      # Earthly branch associated with this palace position
    meaning: str     # Life domain governed

    def __str__(self) -> str:
        return f"{self.name}({self.branch})"


# 12 Palace definitions (顺序固定，地支随命宫而转)
PALACE_NAMES: list[tuple[str, str, str]] = [
    ("命宫",  "Life/Destiny",    "命主本人，性格、外貌、整体运势"),
    ("兄弟宫", "Siblings",        "兄弟姐妹、朋友、合作关系"),
    ("夫妻宫", "Spouse",          "婚姻、感情、配偶"),
    ("子女宫", "Children",        "子女、下属、创意"),
    ("财帛宫", "Wealth",          "财运、理财、金钱"),
    ("疾厄宫", "Health",          "健康、疾病、意外"),
    ("迁移宫", "Travel/Migration","出行、搬迁、外在表现"),
    ("奴仆宫", "Servants/Friends","朋友、下属、人际关系"),
    ("官禄宫", "Career",          "事业、名誉、官职"),
    ("田宅宫", "Property",        "房产、家宅、家庭环境"),
    ("福德宫", "Fortune/Virtue",  "福气、精神生活、享受"),
    ("父母宫", "Parents",         "父母、上司、长辈"),
]

# Earthly branches in order (子丑寅卯...)
_BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]


def build_palace_ring(life_palace_branch: str) -> list[Palace]:
    """
    Build the 12-palace ring starting from the Life Palace (命宫).

    In Zi Wei, the 命宫 is placed in a specific branch position,
    and the other 11 palaces follow counterclockwise.

    Args:
        life_palace_branch: The branch character where 命宫 is located

    Returns:
        List of 12 palaces in branch order (子→亥)
    """
    if life_palace_branch not in _BRANCHES:
        raise ValueError(f"Unknown branch: {life_palace_branch!r}")

    life_idx = _BRANCHES.index(life_palace_branch)
    palaces = []

    for i in range(12):
        # Palace index: 命宫=0, 兄弟宫=1, ...
        # Palace positions go counterclockwise (逆时针)
        palace_idx = i
        branch_idx = (life_idx - i) % 12  # Counterclockwise

        name, english, meaning = PALACE_NAMES[palace_idx]
        palaces.append(Palace(
            index=palace_idx,
            name=name,
            english=english,
            branch=_BRANCHES[branch_idx],
            meaning=meaning,
        ))

    return palaces
