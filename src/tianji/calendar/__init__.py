"""
tianji.calendar — 干支历法引擎 (Stem-Branch Calendar Engine)

This package provides the foundational calendar computations:
- 天干 (Heavenly Stems): 甲乙丙丁戊己庚辛壬癸
- 地支 (Earthly Branches): 子丑寅卯辰巳午未申酉戌亥
- 干支 (Stem-Branch pairs): 六十甲子 cycle
- 24节气 (Solar Terms)
- 农历 (Lunar Calendar)
"""

from tianji.calendar.earthly_branches import (
    EARTHLY_BRANCHES,
    SIX_CONFLICTS,
    SIX_HARMONIES,
    SIX_HARMS,
    THREE_HARMONIES,
    THREE_PUNISHMENTS,
    EarthlyBranch,
    get_branch,
    get_branch_by_char,
    get_branch_for_hour,
)
from tianji.calendar.heavenly_stems import (
    ELEMENT_CONQUERS,
    ELEMENT_PRODUCES,
    HEAVENLY_STEMS,
    Element,
    HeavenlyStem,
    Polarity,
    get_stem,
    get_stem_by_char,
    stem_relationship,
)
from tianji.calendar.lunar import (
    format_lunar_date,
    format_lunar_date_traditional,
    lunar_to_solar,
    solar_to_lunar,
)
from tianji.calendar.solar_terms import (
    SOLAR_TERMS,
    get_month_boundary_dates,
    get_solar_term_date,
    get_solar_term_datetime,
    lichun_date,
)
from tianji.calendar.stem_branch import (
    JIAZI_CYCLE,
    StemBranch,
    date_to_day_jiazi,
    get_jiazi,
    get_jiazi_by_char,
    jiazi_index_for_date,
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
    "SOLAR_TERMS", "get_solar_term_date", "get_solar_term_datetime", "lichun_date", "get_month_boundary_dates",
    # Lunar calendar
    "solar_to_lunar", "lunar_to_solar", "format_lunar_date", "format_lunar_date_traditional",
]
