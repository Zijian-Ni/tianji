"""
干支 (Stem-Branch) combinations and the 六十甲子 (60-cycle) system.

The 60-cycle (甲子 cycle) is formed by combining 10 Heavenly Stems and 12 Earthly Branches.
Since GCD(10, 12) = 2, only 60 unique combinations exist.

Reference epoch: 1900-01-01 (Gregorian) = 甲子日 (index 0 of 60-cycle)
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta

from tianji.calendar.earthly_branches import EarthlyBranch, get_branch
from tianji.calendar.heavenly_stems import HeavenlyStem, get_stem


@dataclass(frozen=True)
class StemBranch:
    """A Stem-Branch pair (干支), one step of the 60-cycle."""
    stem: HeavenlyStem
    branch: EarthlyBranch
    index: int  # 0–59 in the 甲子 cycle

    def __str__(self) -> str:
        return f"{self.stem.char}{self.branch.char}"

    def __repr__(self) -> str:
        return f"StemBranch({self.stem.char}{self.branch.char}, #{self.index})"

    @property
    def char(self) -> str:
        return f"{self.stem.char}{self.branch.char}"


def _build_jiazi_cycle() -> tuple[StemBranch, ...]:
    """Build the complete 六十甲子 (60-cycle) list."""
    result = []
    for i in range(60):
        stem = get_stem(i % 10)
        branch = get_branch(i % 12)
        result.append(StemBranch(stem=stem, branch=branch, index=i))
    return tuple(result)


JIAZI_CYCLE: tuple[StemBranch, ...] = _build_jiazi_cycle()

# Reverse lookup: char → StemBranch
JIAZI_BY_CHAR: dict[str, StemBranch] = {sb.char: sb for sb in JIAZI_CYCLE}

# Reference epoch for day calculation
# 1900-01-01 (Gregorian) = 甲子 (index 0)
_REFERENCE_DATE = date(1900, 1, 1)
_REFERENCE_INDEX = 0  # 甲子


def get_jiazi(index: int) -> StemBranch:
    """Get a stem-branch by 60-cycle index (0–59, wraps around)."""
    return JIAZI_CYCLE[index % 60]


def get_jiazi_by_char(char: str) -> StemBranch:
    """Get a stem-branch by its two-character string (e.g. '甲子')."""
    if char not in JIAZI_BY_CHAR:
        raise ValueError(f"Unknown stem-branch: {char!r}")
    return JIAZI_BY_CHAR[char]


def date_to_day_jiazi(d: date) -> StemBranch:
    """
    Compute the stem-branch (干支) for a given date.

    Uses the reference: 1900-01-01 = 甲子 (index 0).
    """
    delta = (d - _REFERENCE_DATE).days
    index = (_REFERENCE_INDEX + delta) % 60
    return JIAZI_CYCLE[index]


def jiazi_index_for_date(d: date) -> int:
    """Return the 60-cycle index (0–59) for a given date."""
    delta = (d - _REFERENCE_DATE).days
    return (delta + _REFERENCE_INDEX) % 60


def print_jiazi_table() -> None:
    """Print the full 六十甲子 table for reference."""
    print("六十甲子 (60-Cycle Table)")
    print("=" * 50)
    for i, sb in enumerate(JIAZI_CYCLE):
        print(f"{i+1:3d}. {sb.char}  ({sb.stem.element.value}{sb.stem.polarity.value})")
        if (i + 1) % 10 == 0:
            print()
