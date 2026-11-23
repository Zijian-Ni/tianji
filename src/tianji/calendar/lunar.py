"""Gregorian / Chinese lunar conversions from the packaged new-moon calendar."""

from bisect import bisect_right
from datetime import date, timedelta
from itertools import accumulate

from tianji.calendar.almanac import DATA

_BASE = date.fromisoformat(DATA["lunarStart"])
_MONTHS = DATA["lunarMonths"]
_YEAR_STARTS = list(accumulate((sum(map(abs, row)) for row in _MONTHS), initial=0))


def solar_to_lunar(d: date) -> tuple[int, int, int, bool]:
    offset = (d - _BASE).days
    if not 0 <= offset < _YEAR_STARTS[-1]:
        raise ValueError("Date outside the lunar calendar (lunar years 1900–2100)")
    index = bisect_right(_YEAR_STARTS, offset) - 1
    offset -= _YEAR_STARTS[index]
    month = 0
    for length in _MONTHS[index]:
        month += length > 0
        if offset < abs(length):
            return _BASE.year + index, month, offset + 1, length < 0
        offset -= abs(length)
    raise RuntimeError("Incomplete lunar year")


def lunar_to_solar(year: int, month: int, day: int, is_leap: bool = False) -> date:
    index = year - _BASE.year
    if not 0 <= index < len(_MONTHS):
        raise ValueError("Lunar year must be in 1900–2100")
    offset = _YEAR_STARTS[index]
    number = 0
    for length in _MONTHS[index]:
        number += length > 0
        if number == month and (length < 0) == is_leap:
            if not 1 <= day <= abs(length):
                raise ValueError("Invalid day for this lunar month")
            return _BASE + timedelta(days=offset + day - 1)
        offset += abs(length)
    raise ValueError("Invalid month or leap month for this lunar year")


def get_lunar_year(d: date) -> int:
    return solar_to_lunar(d)[0]


def get_lunar_month(d: date) -> int:
    return solar_to_lunar(d)[1]


def get_lunar_day(d: date) -> int:
    return solar_to_lunar(d)[2]


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
