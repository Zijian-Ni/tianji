"""
紫微斗数排盘 (Zi Wei Dou Shu chart calculation).

Basic implementation: palace positioning and major star placement.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from tianji.calendar.lunar import lunar_to_solar
from tianji.calendar.earthly_branches import EARTHLY_BRANCHES, get_branch_by_char, get_branch_for_hour
from tianji.ziwei.palaces import build_palace_ring
from tianji.ziwei.stars import place_tianfu_group, place_ziwei_group


@dataclass
class ChartPalace:
    """A palace in the chart with stars."""
    name: str
    position: int
    branch: str
    stars: list[str] = field(default_factory=list)


@dataclass
class ZiWeiChart:
    """A complete Zi Wei Dou Shu chart."""
    year: int
    month: int  # lunar month
    day: int    # lunar day
    hour: int   # birth hour (0-23)
    gender: str  # 男/女

    palaces: dict[str, ChartPalace] = field(default_factory=dict)

    is_leap: bool = False

    def __post_init__(self):
        if not self.palaces:
            self._calculate()

    def _calculate(self):
        """Calculate the full chart."""
        if not 1 <= self.month <= 12 or not 1 <= self.day <= 30 or not 0 <= self.hour < 24:
            raise ValueError("Expected lunar month 1–12, day 1–30, clock hour 0–23")
        if self.is_leap or 1900 <= self.year <= 2100:
            lunar_to_solar(self.year, self.month, self.day, self.is_leap)
        hour_branch = get_branch_for_hour(self.hour).index
        ming_position = (self.month + 1 - hour_branch) % 12
        for palace in build_palace_ring(EARTHLY_BRANCHES[ming_position].char):
            pos = get_branch_by_char(palace.branch).index
            self.palaces[palace.name] = ChartPalace(palace.name, pos, palace.branch)

        ziwei_pos = self._calc_ziwei_position(self.day, self.wu_xing_ju)
        # Step 4: Place Zi Wei group stars
        ziwei_stars = place_ziwei_group(ziwei_pos)
        for star_name, pos in ziwei_stars.items():
            palace = self._palace_at(pos)
            if palace:
                palace.stars.append(star_name)

        # Step 5: Place Tian Fu group stars
        tianfu_pos = (12 - ziwei_pos + 4) % 12  # 天府与紫微对称于寅-申轴
        tianfu_stars = place_tianfu_group(tianfu_pos)
        for star_name, pos in tianfu_stars.items():
            palace = self._palace_at(pos)
            if palace:
                palace.stars.append(star_name)

    def _palace_at(self, position: int) -> Optional[ChartPalace]:
        for p in self.palaces.values():
            if p.position == position:
                return p
        return None

    @property
    def body_branch(self) -> str:
        return EARTHLY_BRANCHES[(self.month + 1 + get_branch_for_hour(self.hour).index) % 12].char

    @property
    def wu_xing_ju(self) -> int:
        """Five Tigers month stem at the life palace, then its 纳音 element."""
        branch = self.palaces["命宫"].position
        stem = (2 + 2 * ((self.year - 4) % 5) + (branch - 2) % 12) % 10
        return (3, 4, 2, 6, 5)[(stem // 2 + (branch % 6) // 2 + 1) % 5]

    def _calc_ziwei_position(self, lunar_day: int, ju: int) -> int:
        quotient = (lunar_day + ju - 1) // ju
        padding = quotient * ju - lunar_day
        return (1 + quotient + (padding if padding % 2 == 0 else -padding)) % 12

    def display(self) -> str:
        """Format chart for display."""
        lines = [
            "紫微斗数命盘",
            f"出生：农历{self.year}年{'闰' if self.is_leap else ''}{self.month}月{self.day}日 {self.hour}时",
            f"性别：{self.gender}",
            "",
        ]
        for name, palace in self.palaces.items():
            stars_str = "、".join(palace.stars) if palace.stars else "（无主星）"
            lines.append(f"  {name}（{palace.branch}）：{stars_str}")
        return "\n".join(lines)


def create_ziwei_chart(
    year: int,
    month: int,  # lunar month
    day: int,    # lunar day
    hour: int,
    gender: str = "男",
    is_leap: bool = False,
) -> ZiWeiChart:
    """Create a Zi Wei Dou Shu chart."""
    return ZiWeiChart(year=year, month=month, day=day, hour=hour, gender=gender, is_leap=is_leap)
