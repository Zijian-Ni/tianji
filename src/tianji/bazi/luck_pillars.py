"""
大运 (Luck Pillars) calculation.

大运 are 10-year fortune cycles that begin at different ages depending on:
- Gender: male (男) or female (女)
- Year pillar polarity: Yang (阳) or Yin (阴)

Direction rule:
- Male + Yang year → Forward (顺行): pillars move forward in the 60-cycle
- Male + Yin year → Backward (逆行)
- Female + Yang year → Backward
- Female + Yin year → Forward

Start age calculation:
Count days from birth to the nearest 节 (jie, monthly solar term boundary),
then apply: 3 days = 1 year of luck pillar start age.
"""

from __future__ import annotations

from dataclasses import dataclass
from calendar import monthrange
from datetime import date, datetime

from tianji.calendar.heavenly_stems import Polarity
from tianji.calendar.solar_terms import SOLAR_TERMS, get_solar_term_datetime
from tianji.calendar.stem_branch import StemBranch, get_jiazi

@dataclass
class LuckPillar:
    """Represents one 大运 (10-year luck pillar)."""
    pillar: StemBranch
    start_age: int
    end_age: int

    def __str__(self) -> str:
        return f"{self.pillar.char} ({self.start_age}–{self.end_age}岁)"


@dataclass
class LuckPillarsResult:
    """Complete 大运 calculation result."""
    pillars: list[LuckPillar]
    start_age: int           # Age when luck pillars begin
    direction: str           # "顺行" or "逆行"
    start_date: date         # Approximate date when luck pillars begin

    def display(self) -> None:
        """Print luck pillars."""
        print("\n大运 (Luck Pillars)")
        print("─" * 40)
        print(f"  起运年龄: {self.start_age}岁  行运方向: {self.direction}")
        print("─" * 40)
        for lp in self.pillars:
            print(f"  {lp.pillar.char}  {lp.start_age:2d}–{lp.end_age:2d}岁")
        print("─" * 40)


def _find_nearest_jie(birth: datetime, is_forward: bool) -> datetime:
    month = birth.month - 1
    boundary = get_solar_term_datetime(birth.year, SOLAR_TERMS[month * 2])
    if birth == boundary or (birth < boundary) == is_forward:
        return boundary
    year_offset, month = divmod(month + (1 if is_forward else -1), 12)
    return get_solar_term_datetime(birth.year + year_offset, SOLAR_TERMS[month * 2])


def compute_luck_pillars(
    chart,
    num_pillars: int = 8,
) -> LuckPillarsResult:
    """
    Compute 大运 (Luck Pillars) for a BaZi chart.

    Args:
        chart: A BaZiChart instance
        num_pillars: Number of luck pillars to compute (default 8)

    Returns:
        LuckPillarsResult
    """
    gender = chart.gender
    year_stem = chart.year_pillar.stem
    birth_date = chart.birth_dt.date()

    # Determine direction
    # Yang year + Male = Forward; Yang year + Female = Backward
    # Yin year + Male = Backward; Yin year + Female = Forward
    year_is_yang = year_stem.polarity == Polarity.YANG
    is_male = gender.lower() in ("male", "男")

    is_forward = (year_is_yang and is_male) or (not year_is_yang and not is_male)
    direction = "顺行" if is_forward else "逆行"

    # Find nearest jie boundary
    jie = _find_nearest_jie(chart.birth_dt, is_forward)
    # This API reports completed whole years, with a minimum start age of one.
    start_age = max(1, int(abs((jie - chart.birth_dt).total_seconds()) // (3 * 86400)))
    year = birth_date.year + start_age
    start_date = date(year, birth_date.month, min(birth_date.day, monthrange(year, birth_date.month)[1]))

    # Build luck pillars
    # Start from the month pillar's position in the 60-cycle
    month_sb_index = chart.month_pillar.index

    pillars = []
    for i in range(num_pillars):
        if is_forward:
            idx = (month_sb_index + i + 1) % 60
        else:
            idx = (month_sb_index - i - 1) % 60

        sb = get_jiazi(idx)
        lp_start = start_age + i * 10
        lp_end = lp_start + 9
        pillars.append(LuckPillar(pillar=sb, start_age=lp_start, end_age=lp_end))

    return LuckPillarsResult(
        pillars=pillars,
        start_age=start_age,
        direction=direction,
        start_date=start_date,
    )


def compute_flow_years(
    chart,
    start_year: int | None = None,
    count: int = 10,
) -> list[tuple[int, StemBranch]]:
    """
    Compute 流年 (Flow Years) — the stem-branch for each calendar year.

    Each year in the 60-cycle has its own stem-branch, which interacts
    with the natal chart to produce yearly influences.

    Args:
        chart: A BaZiChart instance
        start_year: Starting year (defaults to birth year)
        count: Number of years to compute

    Returns:
        List of (year, StemBranch) tuples
    """
    if start_year is None:
        start_year = chart.birth_dt.year

    results = []
    for i in range(count):
        year = start_year + i
        year_index = (year - 4) % 60
        sb = get_jiazi(year_index)
        results.append((year, sb))

    return results
