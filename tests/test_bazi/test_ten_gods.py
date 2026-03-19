"""Tests for Ten Gods (十神) computation."""

import pytest

from tianji.calendar.heavenly_stems import get_stem_by_char
from tianji.bazi.ten_gods import compute_ten_god, compute_all_ten_gods, TenGodResult


class TestTenGods:
    """Tests for compute_ten_god with 甲木 as Day Master."""

    def setup_method(self):
        """甲 (Wood, Yang) as Day Master for all tests."""
        self.dm = get_stem_by_char("甲")

    def test_bijian(self):
        result = compute_ten_god(self.dm, get_stem_by_char("甲"))
        assert result.ten_god == "比肩"

    def test_jiecai(self):
        result = compute_ten_god(self.dm, get_stem_by_char("乙"))
        assert result.ten_god == "劫财"

    def test_shishen(self):
        result = compute_ten_god(self.dm, get_stem_by_char("丙"))
        assert result.ten_god == "食神"

    def test_shangguan(self):
        result = compute_ten_god(self.dm, get_stem_by_char("丁"))
        assert result.ten_god == "伤官"

    def test_piancai(self):
        result = compute_ten_god(self.dm, get_stem_by_char("戊"))
        assert result.ten_god == "偏财"

    def test_zhengcai(self):
        result = compute_ten_god(self.dm, get_stem_by_char("己"))
        assert result.ten_god == "正财"

    def test_qisha(self):
        result = compute_ten_god(self.dm, get_stem_by_char("庚"))
        assert result.ten_god == "七杀"

    def test_zhengguan(self):
        result = compute_ten_god(self.dm, get_stem_by_char("辛"))
        assert result.ten_god == "正官"

    def test_pianyin(self):
        result = compute_ten_god(self.dm, get_stem_by_char("壬"))
        assert result.ten_god == "偏印"

    def test_zhengyin(self):
        result = compute_ten_god(self.dm, get_stem_by_char("癸"))
        assert result.ten_god == "正印"

    def test_result_has_english(self):
        result = compute_ten_god(self.dm, get_stem_by_char("庚"))
        assert result.english != ""

    def test_result_has_meaning(self):
        result = compute_ten_god(self.dm, get_stem_by_char("庚"))
        assert result.meaning != ""


class TestTenGodsWithDifferentDM:
    """Tests with different Day Masters."""

    def test_bing_fire_dm(self):
        """丙火日主: 壬水 → 七杀 (Water conquers Fire, same Yang polarity)."""
        dm = get_stem_by_char("丙")  # Fire, Yang
        result = compute_ten_god(dm, get_stem_by_char("壬"))  # Water, Yang
        assert result.ten_god == "七杀"

    def test_bing_fire_dm_gui(self):
        """丙火日主: 癸水 → 正官 (Water conquers Fire, different polarity)."""
        dm = get_stem_by_char("丙")
        result = compute_ten_god(dm, get_stem_by_char("癸"))
        assert result.ten_god == "正官"

    def test_compute_all(self):
        """compute_all_ten_gods returns correct count."""
        dm = get_stem_by_char("甲")
        others = [get_stem_by_char(c) for c in "丙庚壬"]
        results = compute_all_ten_gods(dm, others)
        assert len(results) == 3
        assert results[0].ten_god == "食神"
        assert results[1].ten_god == "七杀"
        assert results[2].ten_god == "偏印"
