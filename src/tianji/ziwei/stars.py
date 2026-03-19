"""
紫微斗数星曜 (Zi Wei Dou Shu stars).

Major stars placement based on Zi Wei star position.
"""

from __future__ import annotations


# 紫微星系 (Zi Wei Group) — positions relative to Zi Wei
# These stars follow a fixed pattern from Zi Wei's position
ZIWEI_GROUP_OFFSETS: dict[str, int] = {
    "紫微": 0,
    "天机": -1,
    "太阳": -2,
    "武曲": -3,
    "天同": -4,
    "廉贞": -6,
}

# 天府星系 (Tian Fu Group) — positions relative to Tian Fu
TIANFU_GROUP_OFFSETS: dict[str, int] = {
    "天府": 0,
    "太阴": 1,
    "贪狼": 2,
    "巨门": 3,
    "天相": 4,
    "天梁": 5,
    "七杀": 6,
    "破军": 10,
}

# All 14 major stars (十四主星)
MAJOR_STARS = list(ZIWEI_GROUP_OFFSETS.keys()) + list(TIANFU_GROUP_OFFSETS.keys())


def place_ziwei_group(ziwei_pos: int) -> dict[str, int]:
    """
    Place Zi Wei group stars given Zi Wei's palace position.
    Returns {star_name: palace_position}.
    """
    result = {}
    for star, offset in ZIWEI_GROUP_OFFSETS.items():
        result[star] = (ziwei_pos + offset) % 12
    return result


def place_tianfu_group(tianfu_pos: int) -> dict[str, int]:
    """
    Place Tian Fu group stars given Tian Fu's palace position.
    Returns {star_name: palace_position}.
    """
    result = {}
    for star, offset in TIANFU_GROUP_OFFSETS.items():
        result[star] = (tianfu_pos + offset) % 12
    return result
