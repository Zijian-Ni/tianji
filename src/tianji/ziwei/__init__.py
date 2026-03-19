"""
tianji.ziwei — 紫微斗数 (Zi Wei Dou Shu / Purple Star Astrology)

Zi Wei Dou Shu is a Chinese astrological system that maps stars
into 12 palaces to reveal destiny patterns.
"""

from tianji.ziwei.palaces import Palace, build_palace_ring, PALACE_NAMES
from tianji.ziwei.stars import Star, MAJOR_STARS, AUXILIARY_STARS, place_all_major_stars
from tianji.ziwei.chart import ZiWeiChart

__all__ = [
    "Palace", "build_palace_ring", "PALACE_NAMES",
    "Star", "MAJOR_STARS", "AUXILIARY_STARS", "place_all_major_stars",
    "ZiWeiChart",
]
