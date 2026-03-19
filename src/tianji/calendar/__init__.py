"""
tianji.calendar — 干支历法引擎 (Stem-Branch Calendar Engine)

This package provides the foundational calendar computations:
- 天干 (Heavenly Stems): 甲乙丙丁戊己庚辛壬癸
- 地支 (Earthly Branches): 子丑寅卯辰巳午未申酉戌亥
- 干支 (Stem-Branch pairs): 六十甲子 cycle
- 24节气 (Solar Terms)
- 农历 (Lunar Calendar) via lunardate
"""

from tianji.calendar.heavenly_stems import (
    Element,
    HeavenlyStem,
    HEAVENLY_STEMS,
    Polarity,
    get_stem,
    get_stem_by_char,
    stem_relationship,
    ELEMENT_PRODUCES,
    ELEMENT_CONQUERS,
)
from tianji.calendar.earthly_branches import (
    EarthlyBranch,
    EARTHLY_BRANCHES,
    get_branch,
    get_branch_by_char,
    get_branch_for_hour,
    SIX_CONFLICTS,
    SIX_HARMONIES,
    THREE_HARMONIES,
    THREE_PUNISHMENTS,
    SIX_HARMS,
)
from tianji.calendar.stem_branch import (
    StemBranch,
    JIAZI_CYCLE,
    date_to_day_jiazi,
    get_jiazi,
    get_jiazi_by_char,
    jiazi_index_for_date,
)
from tianji.calendar.solar_terms import (
    SOLAR_TERMS,
    get_solar_term_date,
    lichun_date,
    get_month_boundary_dates,
)
from tianji.calendar.lunar import (
    solar_to_lunar,
    lunar_to_solar,
    format_lunar_date,
    format_lunar_date_traditional,
)

__all__ = [
    # Elements & polarity
    "Element", "Polarity",
    # Heavenly stems
    "HeavenlyStem", "HEAVENLY_STEMS", "get_stem", "get_stem_by_char", "stem_relationship",
    "ELEMENT_PRODUCES", "ELEMENT_CONQUERS",
    # Earthly branches
    "EarthlyBranch", "EARTHLY_BRANCHES", "get_branch", "get_branch_by_char",
    "get_branch_for_hour", "SIX_CONFLICTS", "SIX_HARMONIES", "THREE_HARMONIES",
    "THREE_PUNISHMENTS", "SIX_HARMS",
    # Stem-branch pairs
    "StemBranch", "JIAZI_CYCLE", "date_to_day_jiazi", "get_jiazi",
    "get_jiazi_by_char", "jiazi_index_for_date",
    # Solar terms
    "SOLAR_TERMS", "get_solar_term_date", "lichun_date", "get_month_boundary_dates",
    # Lunar calendar
    "solar_to_lunar", "lunar_to_solar", "format_lunar_date", "format_lunar_date_traditional",
]
