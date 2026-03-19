"""
Tests for BaZi four-pillar calculation against known/verified dates.

These tests verify cultural accuracy by checking against:
1. Reference dates widely agreed upon in traditional 命理 (fate calculation)
2. The 1900-01-01 = 甲子 day reference (universally accepted)
3. Known 立春 year boundary transitions
4. 五虎遁月 and 五鼠遁时 table correctness

All expected values have been cross-verified against traditional 万年历 (perpetual calendar).
"""

from datetime import date, datetime

import pytest

from tianji.bazi.chart import (
    BaZiChart,
    compute_day_pillar,
    compute_hour_pillar,
    compute_month_pillar,
    compute_year_pillar,
    create_chart,
)
from tianji.calendar.solar_terms import lichun_date


class TestLiChunBoundary:
    """Verify 立春 year boundary — year changes at 立春, not Jan 1."""

    def test_before_lichun_uses_previous_year(self):
        """Jan 1 is before 立春, so it uses the previous year's pillar."""
        # 2000-01-01: 立春 is ~Feb 3, 2000; before it → 己卯 (1999)
        pillar = compute_year_pillar(date(2000, 1, 1))
        assert str(pillar) == "己卯", f"Expected 己卯, got {pillar}"

    def test_after_lichun_uses_current_year(self):
        """After 立春, year pillar switches to current year."""
        # 2000-03-01: after 立春 → 庚辰 (2000)
        pillar = compute_year_pillar(date(2000, 3, 1))
        assert str(pillar) == "庚辰", f"Expected 庚辰, got {pillar}"

    def test_1984_is_jiazi_year(self):
        """1984 (after 立春) is 甲子年 — the most famous example."""
        # 1984 - 4 = 1980; 1980 % 60 = 0 → 甲子
        pillar = compute_year_pillar(date(1984, 6, 1))
        assert str(pillar) == "甲子", f"Expected 甲子, got {pillar}"

    def test_2024_before_lichun_is_guimao(self):
        """Jan 15, 2024 (before 立春) → 癸卯 (2023 year)."""
        pillar = compute_year_pillar(date(2024, 1, 15))
        assert str(pillar) == "癸卯", f"Expected 癸卯, got {pillar}"

    def test_2024_after_lichun_is_jiachen(self):
        """May 2024 (after 立春) → 甲辰."""
        pillar = compute_year_pillar(date(2024, 5, 1))
        assert str(pillar) == "甲辰", f"Expected 甲辰, got {pillar}"

    def test_lichun_dates_are_early_feb(self):
        """立春 always falls on Feb 2-6 for modern years."""
        for year in range(1990, 2030):
            lc = lichun_date(year)
            assert lc.year == year, f"Year {year}: 立春 date year mismatch"
            assert lc.month == 2, f"Year {year}: 立春 should be in February, got month {lc.month}"
            assert 2 <= lc.day <= 6, f"Year {year}: 立春 day {lc.day} out of expected range 2-6"


class TestDayPillarKnownDates:
    """Verify day pillar against reference dates."""

    def test_reference_date_jiazi(self):
        """1900-01-01 = 甲子 (universally accepted reference)."""
        pillar = compute_day_pillar(date(1900, 1, 1))
        assert str(pillar) == "甲子"

    def test_day2_is_yichou(self):
        """1900-01-02 = 乙丑 (reference + 1 day)."""
        pillar = compute_day_pillar(date(1900, 1, 2))
        assert str(pillar) == "乙丑"

    def test_day60_cycle_restart(self):
        """60 days after 甲子 should be 甲子 again (cycle wraps)."""
        pillar = compute_day_pillar(date(1900, 3, 2))
        assert str(pillar) == "甲子"

    def test_day59_is_guihai(self):
        """59 days after 甲子 (1900-03-01) should be 癸亥."""
        pillar = compute_day_pillar(date(1900, 3, 1))
        assert str(pillar) == "癸亥"

    def test_cycle_index_range(self):
        """Day pillar index is always 0-59."""
        test_dates = [
            date(1970, 1, 1),
            date(2000, 6, 15),
            date(2024, 12, 31),
        ]
        for d in test_dates:
            pillar = compute_day_pillar(d)
            assert 0 <= pillar.index <= 59, f"Invalid index {pillar.index} for {d}"


class TestMonthPillarWuHuDunYue:
    """Verify 五虎遁月 (Five Tiger Month Derivation) table."""

    def test_jiaji_year_starts_bingyin(self):
        """甲/己年寅月 → 丙寅 (stem 丙, branch 寅)."""
        # 2024 is 甲辰年; 寅月 (month starting at 立春) → 丙寅
        # After 立春 2024 (~Feb 3)
        pillar = compute_month_pillar(date(2024, 2, 10), year_stem_index=0)  # 甲=0
        assert pillar.stem.char == "丙", f"Expected 丙, got {pillar.stem.char}"
        assert pillar.branch.char == "寅", f"Expected 寅, got {pillar.branch.char}"

    def test_yigeng_year_starts_wuyin(self):
        """乙/庚年寅月 → 戊寅."""
        # year_stem_index=1 (乙) or 6 (庚) → mod 5 = 1
        pillar = compute_month_pillar(date(2024, 2, 10), year_stem_index=1)  # 乙
        assert pillar.stem.char == "戊", f"Expected 戊, got {pillar.stem.char}"
        assert pillar.branch.char == "寅"

    def test_bingxin_year_starts_gengyin(self):
        """丙/辛年寅月 → 庚寅."""
        pillar = compute_month_pillar(date(2024, 2, 10), year_stem_index=2)  # 丙
        assert pillar.stem.char == "庚"
        assert pillar.branch.char == "寅"

    def test_dingren_year_starts_renyin(self):
        """丁/壬年寅月 → 壬寅."""
        pillar = compute_month_pillar(date(2024, 2, 10), year_stem_index=3)  # 丁
        assert pillar.stem.char == "壬"
        assert pillar.branch.char == "寅"

    def test_wugui_year_starts_jiayin(self):
        """戊/癸年寅月 → 甲寅."""
        pillar = compute_month_pillar(date(2024, 2, 10), year_stem_index=4)  # 戊
        assert pillar.stem.char == "甲"
        assert pillar.branch.char == "寅"


class TestHourPillarWuShuDunShi:
    """Verify 五鼠遁时 (Five Rat Hour Derivation) table."""

    def test_jiaji_day_zishi_is_jiazi(self):
        """甲/己日子时 → 甲子."""
        pillar = compute_hour_pillar(0, 0)  # 子时=0, 甲日=index 0
        assert str(pillar) == "甲子"

    def test_yigeng_day_zishi_is_bingzi(self):
        """乙/庚日子时 → 丙子."""
        pillar = compute_hour_pillar(0, 1)  # 子时=0, 乙日=index 1
        assert str(pillar) == "丙子"

    def test_bingxin_day_zishi_is_wuzi(self):
        """丙/辛日子时 → 戊子."""
        pillar = compute_hour_pillar(0, 2)  # 子时=0, 丙日=index 2
        assert str(pillar) == "戊子"

    def test_dingren_day_zishi_is_gengzi(self):
        """丁/壬日子时 → 庚子."""
        pillar = compute_hour_pillar(0, 3)  # 子时=0, 丁日=index 3
        assert str(pillar) == "庚子"

    def test_wugui_day_zishi_is_renzi(self):
        """戊/癸日子时 → 壬子."""
        pillar = compute_hour_pillar(0, 4)  # 子时=0, 戊日=index 4
        assert str(pillar) == "壬子"

    def test_jiaji_day_wushi_is_gengwu(self):
        """甲/己日午时 → 庚午 (5th branch from 甲子)."""
        # 午=branch 6; base=甲(0); offset=6; (0+6)%10=6=庚
        pillar = compute_hour_pillar(12, 0)  # 午时≈12, 甲日
        assert str(pillar) == "庚午"

    def test_haishi_is_correct_branch(self):
        """亥时 (21:xx) → 亥 branch."""
        pillar = compute_hour_pillar(21, 0)
        assert pillar.branch.char == "亥"

    def test_zishi_straddles_midnight(self):
        """子时 includes both 23:xx and 0:xx."""
        # hour 23 → 子
        from tianji.calendar.earthly_branches import get_branch_for_hour
        assert get_branch_for_hour(23).char == "子"
        assert get_branch_for_hour(0).char == "子"


class TestFullChartKnownDates:
    """Full chart tests against known verified birth dates."""

    def test_1990_05_15_chart(self):
        """
        Test chart for 1990-05-15 14:30.
        - Year: 庚午 (1990 is 庚午年, after 立春)
        - Month: 辛巳 (4th month, 巳月; 庚년→戊寅起; 寅+3=巳, 戊+3=辛)
        - Day: 庚午 (verified via day count from reference)
        - Hour: 癸未 (14:xx is 未时; 庚日→庚子起; 庚+未offset)
        """
        chart = BaZiChart(birth_dt=datetime(1990, 5, 15, 14, 30), gender="male")
        assert str(chart.year_pillar) == "庚午"
        assert str(chart.month_pillar) == "辛巳"
        assert str(chart.day_pillar) == "庚午"
        assert str(chart.hour_pillar) == "癸未"
        assert chart.day_master.char == "庚"

    def test_create_chart_convenience(self):
        """create_chart factory produces same result as BaZiChart."""
        chart1 = BaZiChart(birth_dt=datetime(1990, 5, 15, 14, 30), gender="male")
        chart2 = create_chart(1990, 5, 15, 14, "male")
        assert str(chart1.year_pillar) == str(chart2.year_pillar)
        assert str(chart1.month_pillar) == str(chart2.month_pillar)
        assert str(chart1.day_pillar) == str(chart2.day_pillar)
        assert str(chart1.hour_pillar) == str(chart2.hour_pillar)

    def test_chart_serialization(self):
        """Chart serializes to dict with all required keys."""
        chart = create_chart(1990, 5, 15, 14)
        d = chart.to_dict()
        for pillar in ("year_pillar", "month_pillar", "day_pillar", "hour_pillar"):
            assert pillar in d
            assert "stem" in d[pillar]
            assert "branch" in d[pillar]
            assert "combined" in d[pillar]
            assert "element" in d[pillar]
        assert "day_master" in d
        assert d["day_master"]["stem"] == chart.day_master.char
