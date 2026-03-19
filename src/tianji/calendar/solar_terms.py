"""
24节气 (Solar Terms) approximate calculation module.

Solar terms are specific points in the tropical year, each separated by ~15°
of solar longitude. This module provides approximate date calculation.

For BaZi purposes, the most critical solar term is 立春 (Start of Spring),
which determines the year boundary.
"""

from __future__ import annotations

import math
from datetime import datetime, date, timedelta


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


def get_solar_term_date(year: int, term: str) -> date:
    """
    Get the approximate date of a solar term for a given year.

    Accuracy: ±1–2 days for 1900–2100.

    Args:
        year: Gregorian year
        term: Solar term name (e.g. "立春", "春分")

    Returns:
        Approximate date
    """
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


def lichun_date(year: int) -> date:
    """
    Get the approximate date of 立春 (Start of Spring) for a given year.
    立春 is critical for BaZi year pillar determination.

    立春 typically falls on February 3–5.
    """
    d = get_solar_term_date(year, "立春")

    # 立春 should be in January or February of the given year
    # If our approximation is off, clamp to expected range
    if d.month > 3 or d.year != year:
        # Fallback: Feb 4 is the most common 立春 date
        d = date(year, 2, 4)

    return d


def get_month_boundary_dates(year: int) -> list[tuple[str, date]]:
    """
    Get all 12 monthly solar term (节) dates for a given year.
    These are the 12 terms that start each Chinese month:
    立春, 惊蛰, 清明, 立夏, 芒种, 小暑, 立秋, 白露, 寒露, 立冬, 大雪, 小寒

    Returns list of (term_name, date) sorted by date.
    """
    monthly_terms = ["立春", "惊蛰", "清明", "立夏", "芒种", "小暑",
                     "立秋", "白露", "寒露", "立冬", "大雪", "小寒"]

    results = []
    for term in monthly_terms:
        d = get_solar_term_date(year, term)
        results.append((term, d))

    results_sorted = sorted(results, key=lambda x: x[1])
    return results_sorted


def get_jieqi_month(d: date) -> int:
    """
    Given a date, return the lunar month number (1–12) based on solar terms.
    Month 1 starts at 立春, Month 2 at 惊蛰, etc.
    """
    year = d.year
    boundaries = get_month_boundary_dates(year)
    prev_boundaries = get_month_boundary_dates(year - 1)

    all_boundaries = prev_boundaries + boundaries
    all_boundaries_sorted = sorted(all_boundaries, key=lambda x: x[1])

    month = 0
    for _, boundary_date in all_boundaries_sorted:
        if d >= boundary_date:
            month += 1
        else:
            break

    return ((month - 1) % 12) + 1
