"""
八字四柱排盘 (BaZi Four-Pillar Chart)

Calculates the year, month, day, and hour pillars (年月日时柱) from a birth datetime.

Key rules:
- Year pillar: Changes at 立春 (Start of Spring), NOT at Lunar New Year or Jan 1
- Month pillar: Changes at the 12 节 (jie) solar terms; stem computed via 五虎遁月
- Day pillar: Computed from reference date 1900-01-01 = 甲戌 (index 10)
- Hour pillar: Based on double-hour (时辰); stem computed via 五鼠遁时
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime

from tianji.calendar.earthly_branches import EarthlyBranch, get_branch, get_branch_for_hour
from tianji.calendar.heavenly_stems import HeavenlyStem, get_stem
from tianji.calendar.almanac import beijing_time
from tianji.calendar.solar_terms import get_jieqi_month, get_solar_term_datetime
from tianji.calendar.stem_branch import StemBranch, date_to_day_jiazi, get_jiazi

# 五虎遁月 — Month stem lookup table
# Maps year stem index (mod 5) → starting stem index for 寅月 (month 1 = 寅)
# 甲/己年 → 丙寅 (stem index 2=丙), 乙/庚年 → 戊寅 (4=戊), etc.
_WUHU_MONTH_STEM_START: dict[int, int] = {
    0: 2,  # 甲/己 → 丙 (index 2)
    1: 4,  # 乙/庚 → 戊 (index 4)
    2: 6,  # 丙/辛 → 庚 (index 6)
    3: 8,  # 丁/壬 → 壬 (index 8)
    4: 0,  # 戊/癸 → 甲 (index 0)
}

# 五鼠遁时 — Hour stem lookup table
# Maps day stem index (mod 5) → starting stem index for 子时 (hour 0 = 子)
_WUSHU_HOUR_STEM_START: dict[int, int] = {
    0: 0,  # 甲/己 → 甲 (index 0)
    1: 2,  # 乙/庚 → 丙 (index 2)
    2: 4,  # 丙/辛 → 戊 (index 4)
    3: 6,  # 丁/壬 → 庚 (index 6)
    4: 8,  # 戊/癸 → 壬 (index 8)
}

def compute_year_pillar(d: date) -> StemBranch:
    """
    Compute the year pillar (年柱).

    The year changes at 立春 (Start of Spring), not at the solar or lunar New Year.
    If the date is before 立春 in the given year, use the previous year's stem-branch.
    """
    d = beijing_time(d) if isinstance(d, datetime) else d
    year = d.year
    lichun = get_solar_term_datetime(year, "立春")
    if d < (lichun if isinstance(d, datetime) else lichun.date()):
        # Before 立春: belongs to previous year
        year -= 1

    # Year 甲子 cycle: year 4 CE was 甲子年
    # So year_index = (year - 4) % 60
    year_index = (year - 4) % 60
    return get_jiazi(year_index)


def compute_month_pillar(d: date, year_stem_index: int) -> StemBranch:
    """
    Compute the month pillar (月柱) using 五虎遁月 (Five Tiger Month Derivation).

    Args:
        d: The date
        year_stem_index: The stem index (0–9) of the year pillar

    The month number (1–12) is determined by which 节 the date falls after:
    - Month 1 starts at 立春 (寅月)
    - Month 2 starts at 惊蛰 (卯月)
    - ...
    - Month 12 starts at 小寒 (丑月)
    """
    month_offset = get_jieqi_month(d) - 1
    branch_idx = (2 + month_offset) % 12
    stem_idx = (_WUHU_MONTH_STEM_START[year_stem_index % 5] + month_offset) % 10

    # Find the StemBranch in the 60-cycle
    for sb in _iter_stem_branch(stem_idx, branch_idx):
        return sb
    raise RuntimeError("Failed to compute month pillar")


def _iter_stem_branch(stem_idx: int, branch_idx: int):
    """Find stem-branch in 60-cycle matching given stem and branch indices."""
    from tianji.calendar.stem_branch import JIAZI_CYCLE
    for sb in JIAZI_CYCLE:
        if sb.stem.index == stem_idx and sb.branch.index == branch_idx:
            yield sb


def compute_day_pillar(d: date) -> StemBranch:
    """
    Compute the day pillar (日柱).

    Reference: 1900-01-01 = 甲戌 (60-cycle index 10).
    """
    return date_to_day_jiazi(d)


def compute_hour_pillar(hour: int, day_stem_index: int) -> StemBranch:
    """
    Compute the hour pillar (时柱) using 五鼠遁时 (Five Rat Hour Derivation).

    Args:
        hour: Clock hour (0–23)
        day_stem_index: The stem index (0–9) of the day pillar

    The double-hour (时辰) branch is determined by the clock hour:
    子 = 23:00–01:00, 丑 = 01:00–03:00, ...
    """
    branch = get_branch_for_hour(hour)
    branch_idx = branch.index

    # 五鼠遁时: base stem for 子时
    base_stem_idx = _WUSHU_HOUR_STEM_START[day_stem_index % 5]

    # Offset by branch index (子=0, 丑=1, ..., 亥=11)
    stem_idx = (base_stem_idx + branch_idx) % 10

    for sb in _iter_stem_branch(stem_idx, branch_idx):
        return sb
    raise RuntimeError("Failed to compute hour pillar")


@dataclass
class BaZiChart:
    """
    八字四柱命盘 (BaZi Four-Pillar Chart).

    Args:
        birth_dt: Birth datetime
        gender: "male" (男) or "female" (女), used for luck pillar direction
    """
    birth_dt: datetime
    gender: str = "male"

    # Computed pillars (set in __post_init__)
    year_pillar: StemBranch = field(init=False)
    month_pillar: StemBranch = field(init=False)
    day_pillar: StemBranch = field(init=False)
    hour_pillar: StemBranch = field(init=False)

    def __post_init__(self) -> None:
        self.birth_dt = beijing_time(self.birth_dt)
        d = self.birth_dt.date()
        h = self.birth_dt.hour

        self.year_pillar = compute_year_pillar(self.birth_dt)
        self.month_pillar = compute_month_pillar(self.birth_dt, self.year_pillar.stem.index)
        self.day_pillar = compute_day_pillar(d)
        self.hour_pillar = compute_hour_pillar(h, self.day_pillar.stem.index)

    @property
    def day_master(self) -> HeavenlyStem:
        """日主 — the Day Master stem (日柱天干)."""
        return self.day_pillar.stem

    @property
    def pillars(self) -> tuple[StemBranch, StemBranch, StemBranch, StemBranch]:
        """Return all four pillars as a tuple (year, month, day, hour)."""
        return (self.year_pillar, self.month_pillar, self.day_pillar, self.hour_pillar)

    @property
    def all_stems(self) -> list[HeavenlyStem]:
        """Return all 4 heavenly stems."""
        return [p.stem for p in self.pillars]

    @property
    def all_branches(self) -> list[EarthlyBranch]:
        """Return all 4 earthly branches."""
        return [p.branch for p in self.pillars]

    def display(self) -> None:
        """Print a formatted chart to stdout."""
        print("╔" + "═" * 42 + "╗")
        print("║" + "    八字命盘 (BaZi Four-Pillar Chart)    " + "║")
        print("╠" + "═" * 10 + "╦" + "═" * 10 + "╦" + "═" * 10 + "╦" + "═" * 10 + "╣")
        print("║   年柱   ║   月柱   ║   日柱   ║   时柱   ║")
        print("║" + "═" * 10 + "╬" + "═" * 10 + "╬" + "═" * 10 + "╬" + "═" * 10 + "║")
        pillars = self.pillars
        stems_row = "".join(f"   {p.stem.char}    ║" for p in pillars)
        branches_row = "".join(f"   {p.branch.char}    ║" for p in pillars)
        print(f"║{stems_row}")
        print(f"║{branches_row}")
        print("╠" + "═" * 42 + "╣")
        print(f"║  日主: {self.day_master.char} ({self.day_master.element.value}{self.day_master.polarity.value})".ljust(43) + "║")
        print("╚" + "═" * 42 + "╝")

    def to_dict(self) -> dict:
        """Serialize chart to dictionary."""
        return {
            "birth_datetime": self.birth_dt.isoformat(),
            "gender": self.gender,
            "year_pillar": {
                "stem": self.year_pillar.stem.char,
                "branch": self.year_pillar.branch.char,
                "combined": str(self.year_pillar),
                "element": self.year_pillar.stem.element.value,
                "polarity": self.year_pillar.stem.polarity.value,
            },
            "month_pillar": {
                "stem": self.month_pillar.stem.char,
                "branch": self.month_pillar.branch.char,
                "combined": str(self.month_pillar),
                "element": self.month_pillar.stem.element.value,
                "polarity": self.month_pillar.stem.polarity.value,
            },
            "day_pillar": {
                "stem": self.day_pillar.stem.char,
                "branch": self.day_pillar.branch.char,
                "combined": str(self.day_pillar),
                "element": self.day_pillar.stem.element.value,
                "polarity": self.day_pillar.stem.polarity.value,
            },
            "hour_pillar": {
                "stem": self.hour_pillar.stem.char,
                "branch": self.hour_pillar.branch.char,
                "combined": str(self.hour_pillar),
                "element": self.hour_pillar.stem.element.value,
                "polarity": self.hour_pillar.stem.polarity.value,
            },
            "day_master": {
                "stem": self.day_master.char,
                "element": self.day_master.element.value,
                "polarity": self.day_master.polarity.value,
            },
        }


def create_chart(
    year: int,
    month: int,
    day: int,
    hour: int = 12,
    gender: str = "male",
    minute: int = 0,
) -> BaZiChart:
    """
    Convenience factory to create a BaZi chart from simple parameters.

    Args:
        year: Birth year (Gregorian)
        month: Birth month (1-12)
        day: Birth day (1-31)
        hour: Birth hour (0-23), default 12
        gender: "male" or "female"

    Returns:
        BaZiChart instance
    """
    from datetime import datetime as dt
    birth = dt(year, month, day, hour, minute)
    return BaZiChart(birth_dt=birth, gender=gender)
