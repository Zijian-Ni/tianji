"""
tianji.ziwei — 紫微斗数 (Zi Wei Dou Shu / Purple Star Astrology)

Zi Wei Dou Shu is a Chinese astrological system that maps stars
into 12 palaces to reveal destiny patterns.
"""

from tianji.ziwei.palaces import Palace, build_palace_ring, PALACE_NAMES
from tianji.ziwei.stars import MAJOR_STARS, place_ziwei_group, place_tianfu_group
from tianji.ziwei.chart import ZiWeiChart, create_ziwei_chart

__all__ = [
    "Palace", "build_palace_ring", "PALACE_NAMES",
    "MAJOR_STARS", "place_ziwei_group", "place_tianfu_group",
    "ZiWeiChart", "create_ziwei_chart",
]
