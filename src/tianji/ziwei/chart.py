"""
紫微斗数排盘 (Zi Wei Dou Shu chart calculation).

Basic implementation: palace positioning and major star placement.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from tianji.calendar.earthly_branches import EARTHLY_BRANCHES, EarthlyBranch
from tianji.calendar.heavenly_stems import HEAVENLY_STEMS
from tianji.ziwei.palaces import PALACE_NAMES
from tianji.ziwei.stars import MAJOR_STARS, place_ziwei_group, place_tianfu_group


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

    def __post_init__(self):
        if not self.palaces:
            self._calculate()

    def _calculate(self):
        """Calculate the full chart."""
        # Step 1: Determine Ming Palace (命宫) position
        # Ming palace index = (month + hour_branch_index) mapped to 12 branches
        hour_branch = self._hour_to_branch(self.hour)
        ming_index = (self.month - 1 + hour_branch) % 12
        # Ming palace is counted from 寅 (index 2)
        ming_position = (2 + self.month - 1 - hour_branch) % 12

        # Step 2: Place all 12 palaces starting from Ming
        for i, (palace_name, _english, _meaning) in enumerate(PALACE_NAMES):
            pos = (ming_position + i) % 12
            branch = EARTHLY_BRANCHES[pos]
            self.palaces[palace_name] = ChartPalace(
                name=palace_name,
                position=pos,
                branch=branch.char,
                stars=[],
            )

        # Step 3: Calculate Zi Wei star position from lunar day + wu_xing_ju
        wu_xing_ju = self._get_wu_xing_ju(ming_position)
        ziwei_pos = self._calc_ziwei_position(self.day, wu_xing_ju)

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

    def _hour_to_branch(self, hour: int) -> int:
        """Convert hour (0-23) to earthly branch index (0-11)."""
        # 子时 23-1, 丑时 1-3, ... 亥时 21-23
        return ((hour + 1) // 2) % 12

    def _get_wu_xing_ju(self, ming_pos: int) -> int:
        """Get 五行局 number (2/3/4/5/6) from Ming palace position."""
        # Simplified: based on stem-branch of Ming palace
        # 水二局=2, 木三局=3, 金四局=4, 土五局=5, 火六局=6
        table = [2, 6, 5, 3, 4, 2, 6, 5, 3, 4, 2, 6]
        return table[ming_pos % 12]

    def _calc_ziwei_position(self, lunar_day: int, wu_xing_ju: int) -> int:
        """Calculate Zi Wei star position from lunar day and 五行局."""
        # 紫微星安星法: day / wu_xing_ju, adjust based on remainder
        quotient = lunar_day // wu_xing_ju
        remainder = lunar_day % wu_xing_ju
        if remainder == 0:
            pos = quotient - 1
        elif remainder % 2 == 1:
            pos = quotient + 1
        else:
            pos = quotient
        return (pos + 1) % 12  # offset to branch position

    def display(self) -> str:
        """Format chart for display."""
        lines = [
            f"紫微斗数命盘",
            f"出生：农历{self.year}年{self.month}月{self.day}日 {self.hour}时",
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
) -> ZiWeiChart:
    """Create a Zi Wei Dou Shu chart."""
    return ZiWeiChart(year=year, month=month, day=day, hour=hour, gender=gender)
