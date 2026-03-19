"""Tests for BaZi chart calculation."""

from datetime import datetime

import pytest

from tianji.bazi.chart import (
    BaZiChart,
    compute_year_pillar,
    compute_day_pillar,
    compute_hour_pillar,
)
from tianji.calendar.stem_branch import date_to_day_jiazi


class TestYearPillar:
    """Tests for year pillar (年柱) computation."""

    def test_year_2024(self):
        """2024 (after lichun) should be 甲辰 year."""
        from datetime import date
        pillar = compute_year_pillar(date(2024, 5, 1))
        assert str(pillar) == "甲辰"

    def test_year_2000(self):
        """2000 (after lichun) should be 庚辰 year."""
        from datetime import date
        pillar = compute_year_pillar(date(2000, 6, 1))
        assert str(pillar) == "庚辰"

    def test_before_lichun(self):
        """January date before lichun uses previous year's pillar."""
        from datetime import date
        # 2024-01-15 is before 立春 (~Feb 4), so year is 2023 = 癸卯
        pillar = compute_year_pillar(date(2024, 1, 15))
        assert str(pillar) == "癸卯"


class TestDayPillar:
    """Tests for day pillar (日柱) computation."""

    def test_reference_date(self):
        """1900-01-01 = 甲子."""
        from datetime import date
        pillar = compute_day_pillar(date(1900, 1, 1))
        assert str(pillar) == "甲子"

    def test_day_after_reference(self):
        """1900-01-02 = 乙丑."""
        from datetime import date
        pillar = compute_day_pillar(date(1900, 1, 2))
        assert str(pillar) == "乙丑"

    def test_recent_date(self):
        """Test a recent date for consistency."""
        from datetime import date
        pillar = compute_day_pillar(date(2024, 1, 1))
        # Just verify it returns a valid StemBranch
        assert len(str(pillar)) == 2
        assert pillar.index >= 0 and pillar.index < 60


class TestHourPillar:
    """Tests for hour pillar (时柱) computation."""

    def test_zi_hour_jia_day(self):
        """甲日子时 (甲/己日 → 甲子起) should be 甲子."""
        pillar = compute_hour_pillar(0, 0)  # 0=子时, 0=甲日
        assert str(pillar) == "甲子"

    def test_zi_hour_yi_day(self):
        """乙日子时 (乙/庚日 → 丙子起) should be 丙子."""
        pillar = compute_hour_pillar(0, 1)  # 0=子时, 1=乙日
        assert str(pillar) == "丙子"

    def test_wu_hour_jia_day(self):
        """甲日午时 (hour 11-12) should be 庚午."""
        pillar = compute_hour_pillar(12, 0)  # 午时, 甲日
        assert str(pillar) == "庚午"

    def test_hai_hour(self):
        """Test 亥时 (21-22 o'clock)."""
        pillar = compute_hour_pillar(21, 0)  # 亥时, 甲日
        assert pillar.branch.char == "亥"


class TestBaZiChart:
    """Tests for full BaZi chart."""

    def test_chart_creation(self):
        """BaZiChart can be created without error."""
        chart = BaZiChart(birth_dt=datetime(1990, 5, 15, 14, 30), gender="male")
        assert chart.day_master is not None
        assert len(str(chart.year_pillar)) == 2
        assert len(str(chart.month_pillar)) == 2
        assert len(str(chart.day_pillar)) == 2
        assert len(str(chart.hour_pillar)) == 2

    def test_chart_pillars_tuple(self):
        """pillars property returns 4 items."""
        chart = BaZiChart(birth_dt=datetime(1990, 5, 15, 14, 30))
        assert len(chart.pillars) == 4

    def test_chart_to_dict(self):
        """to_dict returns proper structure."""
        chart = BaZiChart(birth_dt=datetime(1990, 5, 15, 14, 30))
        d = chart.to_dict()
        assert "year_pillar" in d
        assert "month_pillar" in d
        assert "day_pillar" in d
        assert "hour_pillar" in d
        assert "day_master" in d
        assert "stem" in d["year_pillar"]
        assert "branch" in d["year_pillar"]

    def test_all_stems_count(self):
        chart = BaZiChart(birth_dt=datetime(2000, 8, 15, 10, 0))
        assert len(chart.all_stems) == 4

    def test_all_branches_count(self):
        chart = BaZiChart(birth_dt=datetime(2000, 8, 15, 10, 0))
        assert len(chart.all_branches) == 4
