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
from datetime import date, timedelta

from tianji.calendar.stem_branch import StemBranch, get_jiazi
from tianji.calendar.heavenly_stems import Polarity
from tianji.calendar.solar_terms import get_solar_term_date

# The 12 monthly solar terms (节) in order
_MONTHLY_JIEQI = [
    "立春", "惊蛰", "清明", "立夏", "芒种", "小暑",
    "立秋", "白露", "寒露", "立冬", "大雪", "小寒",
]


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


def _find_nearest_jie(birth_date: date, is_forward: bool) -> tuple[date, str]:
    """
    Find the nearest monthly solar term (节) boundary relative to birth date.

    Args:
        birth_date: The birth date
        is_forward: If True, look forward (next jie); if False, look backward (prev jie)

    Returns:
        (jie_date, term_name)
    """
    year = birth_date.year

    # Collect all monthly jie dates for year-1, year, year+1
    jie_dates: list[tuple[date, str]] = []
    for y in [year - 1, year, year + 1]:
        for term in _MONTHLY_JIEQI:
            try:
                d = get_solar_term_date(y, term)
                jie_dates.append((d, term))
            except Exception:
                pass

    jie_dates.sort(key=lambda x: x[0])

    if is_forward:
        # Find first jie AFTER birth date
        for jd, term in jie_dates:
            if jd > birth_date:
                return jd, term
    else:
        # Find last jie BEFORE birth date
        prev = None
        for jd, term in jie_dates:
            if jd < birth_date:
                prev = (jd, term)
            else:
                break
        if prev:
            return prev

    # Fallback
    return jie_dates[0]


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
    jie_date, jie_term = _find_nearest_jie(birth_date, is_forward)

    # Days to/from that jie
    days_diff = abs((jie_date - birth_date).days)

    # 3 days = 1 year of start age (rule of thumb)
    # Plus remainder: 1 day = 4 months
    full_years = days_diff // 3
    remaining_days = days_diff % 3
    extra_months = remaining_days * 4

    start_age = full_years
    if start_age == 0:
        start_age = 1

    # Approximate start date
    start_date = date(
        birth_date.year + start_age,
        birth_date.month,
        birth_date.day,
    )

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
