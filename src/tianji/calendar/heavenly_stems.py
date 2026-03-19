"""
天干 (Heavenly Stems) module.

The ten Heavenly Stems form the fundamental cycle of Chinese calendar reckoning.
They are paired with Earthly Branches to form the 60-cycle (六十甲子).
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Polarity(str, Enum):
    """阴阳 Yin/Yang polarity."""
    YANG = "阳"
    YIN = "阴"


class Element(str, Enum):
    """五行 Five Elements."""
    WOOD = "木"
    FIRE = "火"
    EARTH = "土"
    METAL = "金"
    WATER = "水"


# Five Elements generation cycle: 相生
ELEMENT_PRODUCES: dict[Element, Element] = {
    Element.WOOD: Element.FIRE,
    Element.FIRE: Element.EARTH,
    Element.EARTH: Element.METAL,
    Element.METAL: Element.WATER,
    Element.WATER: Element.WOOD,
}

# Five Elements conquest cycle: 相克
ELEMENT_CONQUERS: dict[Element, Element] = {
    Element.WOOD: Element.EARTH,
    Element.EARTH: Element.WATER,
    Element.WATER: Element.FIRE,
    Element.FIRE: Element.METAL,
    Element.METAL: Element.WOOD,
}


@dataclass(frozen=True)
class HeavenlyStem:
    """Represents one of the ten Heavenly Stems (天干)."""
    char: str          # Chinese character
    index: int         # 0–9
    element: Element   # 五行
    polarity: Polarity # 阴阳

    def __str__(self) -> str:
        return self.char

    def __repr__(self) -> str:
        return f"HeavenlyStem({self.char}, {self.element.value}{self.polarity.value})"

    def produces(self) -> "HeavenlyStem":
        """Return the stem's element production target (相生)."""
        target_element = ELEMENT_PRODUCES[self.element]
        # Return the Yang stem of the produced element
        for stem in HEAVENLY_STEMS:
            if stem.element == target_element and stem.polarity == self.polarity:
                return stem
        raise ValueError(f"No stem found for {target_element}")

    def conquers(self) -> "HeavenlyStem":
        """Return the stem's element conquest target (相克)."""
        target_element = ELEMENT_CONQUERS[self.element]
        for stem in HEAVENLY_STEMS:
            if stem.element == target_element and stem.polarity == self.polarity:
                return stem
        raise ValueError(f"No stem found for {target_element}")


# The ten Heavenly Stems in order
# 甲乙丙丁戊己庚辛壬癸
HEAVENLY_STEMS: tuple[HeavenlyStem, ...] = (
    HeavenlyStem("甲", 0, Element.WOOD,  Polarity.YANG),  # jiǎ
    HeavenlyStem("乙", 1, Element.WOOD,  Polarity.YIN),   # yǐ
    HeavenlyStem("丙", 2, Element.FIRE,  Polarity.YANG),  # bǐng
    HeavenlyStem("丁", 3, Element.FIRE,  Polarity.YIN),   # dīng
    HeavenlyStem("戊", 4, Element.EARTH, Polarity.YANG),  # wù
    HeavenlyStem("己", 5, Element.EARTH, Polarity.YIN),   # jǐ
    HeavenlyStem("庚", 6, Element.METAL, Polarity.YANG),  # gēng
    HeavenlyStem("辛", 7, Element.METAL, Polarity.YIN),   # xīn
    HeavenlyStem("壬", 8, Element.WATER, Polarity.YANG),  # rén
    HeavenlyStem("癸", 9, Element.WATER, Polarity.YIN),   # guǐ
)

# Lookup by character
STEM_BY_CHAR: dict[str, HeavenlyStem] = {s.char: s for s in HEAVENLY_STEMS}


def get_stem(index: int) -> HeavenlyStem:
    """Get a Heavenly Stem by its 0-based index (mod 10)."""
    return HEAVENLY_STEMS[index % 10]


def get_stem_by_char(char: str) -> HeavenlyStem:
    """Get a Heavenly Stem by its Chinese character."""
    if char not in STEM_BY_CHAR:
        raise ValueError(f"Unknown heavenly stem: {char!r}")
    return STEM_BY_CHAR[char]


def stem_relationship(dm: HeavenlyStem, other: HeavenlyStem) -> str:
    """
    Compute the relationship of `other` stem relative to Day Master (日主) `dm`.
    Returns the Chinese name of the Ten God (十神).
    """
    same_element = dm.element == other.element
    same_polarity = dm.polarity == other.polarity

    # Is other the element that dm produces?
    dm_produces = ELEMENT_PRODUCES[dm.element] == other.element
    # Is other the element that produces dm?
    produces_dm = ELEMENT_PRODUCES[other.element] == dm.element
    # Is other the element that dm conquers?
    dm_conquers = ELEMENT_CONQUERS[dm.element] == other.element
    # Is other the element that conquers dm?
    conquers_dm = ELEMENT_CONQUERS[other.element] == dm.element

    if same_element:
        return "比肩" if same_polarity else "劫财"
    elif dm_produces:
        return "食神" if same_polarity else "伤官"
    elif produces_dm:
        return "偏印" if same_polarity else "正印"
    elif dm_conquers:
        return "偏财" if same_polarity else "正财"
    elif conquers_dm:
        return "七杀" if same_polarity else "正官"
    else:
        raise ValueError(f"Cannot determine relationship between {dm} and {other}")
