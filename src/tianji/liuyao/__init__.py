"""
tianji.liuyao — 六爻 (Liu Yao / Six Lines Divination)

Liu Yao is a divination system based on the I Ching (易经/周易).
It casts a hexagram using coins or time, then analyzes it with
the 六亲 (Six Relatives), 六神 (Six Gods), 世应 (World/Response),
and dynamic line transformations.
"""

from tianji.liuyao.hexagram import (
    Trigram,
    Hexagram,
    TRIGRAMS,
    ALL_HEXAGRAMS,
    HEXAGRAM_BY_NUMBER,
    get_hexagram_by_number,
    get_hexagram_by_trigrams,
    lines_to_hexagram,
)
from tianji.liuyao.casting import (
    CastResult,
    cast_by_time,
    cast_by_numbers,
    cast_by_coins,
    cast_hexagram,
)
from tianji.liuyao.analysis import (
    LineAnalysis,
    LiuYaoAnalysis,
)

__all__ = [
    "Trigram", "Hexagram", "TRIGRAMS", "ALL_HEXAGRAMS", "HEXAGRAM_BY_NUMBER",
    "get_hexagram_by_number", "get_hexagram_by_trigrams", "lines_to_hexagram",
    "CastResult", "cast_by_time", "cast_by_numbers", "cast_by_coins", "cast_hexagram",
    "LineAnalysis", "LiuYaoAnalysis",
]
