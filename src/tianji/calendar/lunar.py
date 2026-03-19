"""
Lunar calendar utilities using the lunardate library.

This module wraps lunardate to provide Chinese lunar date conversions
used in various metaphysical calculations.
"""

from __future__ import annotations

from datetime import date

try:
    from lunardate import LunarDate
    _LUNARDATE_AVAILABLE = True
except ImportError:
    _LUNARDATE_AVAILABLE = False
    LunarDate = None  # type: ignore


def require_lunardate() -> None:
    """Raise ImportError if lunardate is not installed."""
    if not _LUNARDATE_AVAILABLE:
        raise ImportError(
            "lunardate is required for lunar calendar features. "
            "Install it with: pip install lunardate"
        )


def solar_to_lunar(d: date) -> tuple[int, int, int, bool]:
    """
    Convert a Gregorian date to Chinese lunar date.

    Returns:
        (year, month, day, is_leap_month)
    """
    require_lunardate()
    ld = LunarDate.fromSolarDate(d.year, d.month, d.day)
    return ld.year, ld.month, ld.day, ld.isLeapMonth


def lunar_to_solar(year: int, month: int, day: int, is_leap: bool = False) -> date:
    """
    Convert a Chinese lunar date to Gregorian date.

    Args:
        year: Lunar year
        month: Lunar month (1–12)
        day: Lunar day (1–30)
        is_leap: Whether this is a leap month

    Returns:
        Gregorian date
    """
    require_lunardate()
    ld = LunarDate(year, month, day, is_leap)
    sd = ld.toSolarDate()
    return date(sd.year, sd.month, sd.day)


def get_lunar_year(d: date) -> int:
    """Get the Chinese lunar year for a Gregorian date."""
    require_lunardate()
    ld = LunarDate.fromSolarDate(d.year, d.month, d.day)
    return ld.year


def get_lunar_month(d: date) -> int:
    """Get the Chinese lunar month for a Gregorian date."""
    require_lunardate()
    ld = LunarDate.fromSolarDate(d.year, d.month, d.day)
    return ld.month


def get_lunar_day(d: date) -> int:
    """Get the Chinese lunar day for a Gregorian date."""
    require_lunardate()
    ld = LunarDate.fromSolarDate(d.year, d.month, d.day)
    return ld.day


def format_lunar_date(d: date) -> str:
    """Return a human-readable Chinese lunar date string."""
    year, month, day, is_leap = solar_to_lunar(d)
    leap_str = "闰" if is_leap else ""
    return f"农历{year}年{leap_str}{month}月{day}日"


# Chinese number characters for lunar day display
_LUNAR_DAY_NAMES = [
    "初一", "初二", "初三", "初四", "初五", "初六", "初七", "初八", "初九", "初十",
    "十一", "十二", "十三", "十四", "十五", "十六", "十七", "十八", "十九", "二十",
    "廿一", "廿二", "廿三", "廿四", "廿五", "廿六", "廿七", "廿八", "廿九", "三十",
]

_LUNAR_MONTH_NAMES = [
    "正", "二", "三", "四", "五", "六",
    "七", "八", "九", "十", "冬", "腊",
]


def format_lunar_date_traditional(d: date) -> str:
    """Return a traditional Chinese lunar date string."""
    year, month, day, is_leap = solar_to_lunar(d)
    leap_str = "闰" if is_leap else ""
    month_name = _LUNAR_MONTH_NAMES[month - 1]
    day_name = _LUNAR_DAY_NAMES[day - 1]
    return f"农历{year}年{leap_str}{month_name}月{day_name}"
