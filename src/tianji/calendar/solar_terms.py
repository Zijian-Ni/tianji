"""Solar terms in Beijing standard time."""

from __future__ import annotations

from datetime import date, datetime, time, timedelta

from tianji.calendar.almanac import DATA, beijing_time

# 24 Solar Terms in order, starting from 小寒
SOLAR_TERMS: tuple[str, ...] = (
    "小寒", "大寒", "立春", "雨水", "惊蛰", "春分",
    "清明", "谷雨", "立夏", "小满", "芒种", "夏至",
    "小暑", "大暑", "立秋", "处暑", "白露", "秋分",
    "寒露", "霜降", "立冬", "小雪", "大雪", "冬至",
)

# Solar longitude (degrees) for each term, starting from 小寒
# 小寒=285°, 大寒=300°, 立春=315°, ..., 冬至=270°
_TERM_LONGITUDES: dict[str, int] = {}
for i, name in enumerate(SOLAR_TERMS):
    _TERM_LONGITUDES[name] = (285 + i * 15) % 360


def _solar_longitude_to_jde(year: int, target_lon: float) -> float:
    """
    Approximate Julian Day when the sun reaches a given ecliptic longitude.

    Uses a simplified approach based on the mean sun position with
    first-order equation of center correction.
    """
    # Spring equinox (lon=0°) approximate JDE for given year
    # Using Meeus simplified formula for vernal equinox
    Y = (year - 2000) / 1000.0
    jde_equinox = (2451623.80984
                   + 365242.37404 * Y
                   + 0.05169 * Y * Y
                   - 0.00411 * Y * Y * Y
                   - 0.00057 * Y * Y * Y * Y)

    # Estimate: days from equinox to target longitude
    # Sun moves ~0.9856° per day (360/365.25)
    # But the motion is not uniform — use mean motion as first approximation
    delta_lon = target_lon  # degrees from spring equinox (lon=0)
    if delta_lon < 0:
        delta_lon += 360
    if delta_lon > 180:
        # This longitude is before the equinox (previous year's portion)
        delta_lon -= 360

    days_approx = delta_lon / (360.0 / 365.25)
    return jde_equinox + days_approx


def _jde_to_date(jde: float) -> date:
    """Convert Julian Day Number to Python date."""
    # JDE 2451545.0 = 2000-01-01 12:00 UTC
    delta_days = jde - 2451545.0
    base = datetime(2000, 1, 1, 12, 0, 0)
    dt = base + timedelta(days=delta_days)
    return dt.date()


def _approximate_date(year: int, term: str) -> date:
    """Legacy whole-day estimate for dates outside the packaged ephemeris."""
    if term not in _TERM_LONGITUDES:
        raise ValueError(f"Unknown solar term: {term!r}")

    lon = _TERM_LONGITUDES[term]
    jde = _solar_longitude_to_jde(year, lon)
    d = _jde_to_date(jde)

    # Sanity check: the date should be in or near the expected year
    # For terms in the first quarter (小寒, 大寒, 立春, etc.) with
    # longitude > 180°, they occur in Jan–Mar of 'year'
    # For terms with longitude < 180°, they occur in Mar–Dec of 'year'

    # If the computed date is in a clearly wrong year, adjust
    if d.year != year:
        # Try shifting by ±365 days
        if d.year < year:
            jde2 = _solar_longitude_to_jde(year + 1, lon)
            d2 = _jde_to_date(jde2)
            if abs(d2.year - year) < abs(d.year - year):
                d = d2
        elif d.year > year:
            jde2 = _solar_longitude_to_jde(year - 1, lon)
            d2 = _jde_to_date(jde2)
            if abs(d2.year - year) < abs(d.year - year):
                d = d2

    return d


def get_solar_term_datetime(year: int, term: str) -> datetime:
    """UTC+8 wall time, rounded to the nearest minute in the packaged ephemeris."""
    if term not in _TERM_LONGITUDES:
        raise ValueError(f"Unknown solar term: {term!r}")
    index = year - DATA["termStart"]
    if 0 <= index < len(DATA["termMinutes"]):
        minutes = DATA["termMinutes"][index][SOLAR_TERMS.index(term)]
        return datetime(year, 1, 1) + timedelta(minutes=minutes)
    # Retain the historical date-only approximation outside the ephemeris.
    return datetime.combine(_approximate_date(year, term), time.min)


def get_solar_term_date(year: int, term: str) -> date:
    return get_solar_term_datetime(year, term).date()


def lichun_date(year: int) -> date:
    return get_solar_term_date(year, "立春")


def get_month_boundary_dates(year: int) -> list[tuple[str, date]]:
    return [(name, get_solar_term_date(year, name)) for name in SOLAR_TERMS[::2]]


def get_jieqi_month(d: date) -> int:
    """BaZi month, with 寅 as 1. Date-only callers include the whole boundary day."""
    moment = beijing_time(d) if isinstance(d, datetime) else datetime.combine(d, time.max)
    boundary = get_solar_term_datetime(moment.year, SOLAR_TERMS[(moment.month - 1) * 2])
    return (moment.month - (2 if moment >= boundary else 3)) % 12 + 1
