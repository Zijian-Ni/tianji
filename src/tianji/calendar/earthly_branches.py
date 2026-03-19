"""
地支 (Earthly Branches) module.

The twelve Earthly Branches correspond to the zodiac animals, hours of the day,
and months of the lunar year.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from tianji.calendar.heavenly_stems import Element, HeavenlyStem, Polarity, get_stem_by_char


@dataclass(frozen=True)
class EarthlyBranch:
    """Represents one of the twelve Earthly Branches (地支)."""
    char: str               # Chinese character
    index: int              # 0–11, starting from 子
    element: Element        # Primary 五行
    polarity: Polarity      # 阴阳
    zodiac: str             # 生肖 (zodiac animal)
    hour_range: str         # 时辰 range (e.g. "23:00–01:00")
    hidden_stems: tuple[str, ...]  # 藏干 (hidden heavenly stems, chars)

    def __str__(self) -> str:
        return self.char

    def __repr__(self) -> str:
        return f"EarthlyBranch({self.char}, {self.zodiac}, {self.element.value})"

    def get_hidden_stems(self) -> list[HeavenlyStem]:
        """Return the hidden heavenly stems (藏干) of this branch."""
        return [get_stem_by_char(c) for c in self.hidden_stems]

    def hour_index(self) -> int:
        """Return the double-hour index (0=子时, 1=丑时, ..., 11=亥时)."""
        return self.index


# The twelve Earthly Branches in order: 子丑寅卯辰巳午未申酉戌亥
EARTHLY_BRANCHES: tuple[EarthlyBranch, ...] = (
    EarthlyBranch("子", 0,  Element.WATER, Polarity.YANG, "鼠", "23:00–01:00", ("癸",)),
    EarthlyBranch("丑", 1,  Element.EARTH, Polarity.YIN,  "牛", "01:00–03:00", ("己", "癸", "辛")),
    EarthlyBranch("寅", 2,  Element.WOOD,  Polarity.YANG, "虎", "03:00–05:00", ("甲", "丙", "戊")),
    EarthlyBranch("卯", 3,  Element.WOOD,  Polarity.YIN,  "兔", "05:00–07:00", ("乙",)),
    EarthlyBranch("辰", 4,  Element.EARTH, Polarity.YANG, "龙", "07:00–09:00", ("戊", "乙", "癸")),
    EarthlyBranch("巳", 5,  Element.FIRE,  Polarity.YIN,  "蛇", "09:00–11:00", ("丙", "庚", "戊")),
    EarthlyBranch("午", 6,  Element.FIRE,  Polarity.YANG, "马", "11:00–13:00", ("丁", "己")),
    EarthlyBranch("未", 7,  Element.EARTH, Polarity.YIN,  "羊", "13:00–15:00", ("己", "丁", "乙")),
    EarthlyBranch("申", 8,  Element.METAL, Polarity.YANG, "猴", "15:00–17:00", ("庚", "壬", "戊")),
    EarthlyBranch("酉", 9,  Element.METAL, Polarity.YIN,  "鸡", "17:00–19:00", ("辛",)),
    EarthlyBranch("戌", 10, Element.EARTH, Polarity.YANG, "狗", "19:00–21:00", ("戊", "辛", "丁")),
    EarthlyBranch("亥", 11, Element.WATER, Polarity.YIN,  "猪", "21:00–23:00", ("壬", "甲")),
)

# Lookups
BRANCH_BY_CHAR: dict[str, EarthlyBranch] = {b.char: b for b in EARTHLY_BRANCHES}
BRANCH_BY_ZODIAC: dict[str, EarthlyBranch] = {b.zodiac: b for b in EARTHLY_BRANCHES}


def get_branch(index: int) -> EarthlyBranch:
    """Get an Earthly Branch by its 0-based index (mod 12)."""
    return EARTHLY_BRANCHES[index % 12]


def get_branch_by_char(char: str) -> EarthlyBranch:
    """Get an Earthly Branch by its Chinese character."""
    if char not in BRANCH_BY_CHAR:
        raise ValueError(f"Unknown earthly branch: {char!r}")
    return BRANCH_BY_CHAR[char]


def get_branch_for_hour(hour: int) -> EarthlyBranch:
    """
    Get the Earthly Branch (时辰) for a given clock hour (0–23).

    双时辰 mapping:
    子 23,0 | 丑 1,2 | 寅 3,4 | 卯 5,6 | 辰 7,8 | 巳 9,10
    午 11,12 | 未 13,14 | 申 15,16 | 酉 17,18 | 戌 19,20 | 亥 21,22
    """
    if hour == 23:
        return EARTHLY_BRANCHES[0]  # 子
    return EARTHLY_BRANCHES[(hour + 1) // 2]


# Six Harmonies (六合): pairs of branches that combine
SIX_HARMONIES: list[tuple[str, str, Element]] = [
    ("子", "丑", Element.EARTH),
    ("寅", "亥", Element.WOOD),
    ("卯", "戌", Element.FIRE),
    ("辰", "酉", Element.METAL),
    ("巳", "申", Element.WATER),
    ("午", "未", Element.FIRE),   # Fire/Earth (minor)
]

# Three Harmonies (三合): triads forming strong element combinations
THREE_HARMONIES: list[tuple[str, str, str, Element]] = [
    ("申", "子", "辰", Element.WATER),
    ("亥", "卯", "未", Element.WOOD),
    ("寅", "午", "戌", Element.FIRE),
    ("巳", "酉", "丑", Element.METAL),
]

# Six Conflicts (六冲): opposing branches
SIX_CONFLICTS: list[tuple[str, str]] = [
    ("子", "午"),
    ("丑", "未"),
    ("寅", "申"),
    ("卯", "酉"),
    ("辰", "戌"),
    ("巳", "亥"),
]

# Three Punishments (三刑)
THREE_PUNISHMENTS: list[tuple[str, ...]] = [
    ("寅", "巳", "申"),   # 无恩之刑
    ("丑", "戌", "未"),   # 持势之刑
    ("子", "卯"),          # 无礼之刑
    ("辰", "辰"),          # 自刑
    ("午", "午"),
    ("酉", "酉"),
    ("亥", "亥"),
]

# Six Harms (六害)
SIX_HARMS: list[tuple[str, str]] = [
    ("子", "未"),
    ("丑", "午"),
    ("寅", "巳"),
    ("卯", "辰"),
    ("申", "亥"),
    ("酉", "戌"),
]
