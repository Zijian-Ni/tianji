"""Tests for Zi Wei Dou Shu chart calculation."""

import pytest

from tianji.ziwei import ZiWeiChart, create_ziwei_chart, PALACE_NAMES, MAJOR_STARS


class TestZiWeiPalaces:
    """Tests for 十二宫 (12 Palaces) setup."""

    def test_palace_names_count(self):
        """There are exactly 12 palaces."""
        assert len(PALACE_NAMES) == 12

    def test_palace_name_list(self):
        """Palace names include all 12 standard palaces."""
        expected_names = {
            "命宫", "兄弟宫", "夫妻宫", "子女宫", "财帛宫", "疾厄宫",
            "迁移宫", "奴仆宫", "官禄宫", "田宅宫", "福德宫", "父母宫",
        }
        actual_names = {row[0] for row in PALACE_NAMES}
        assert actual_names == expected_names


class TestZiWeiStars:
    """Tests for major stars."""

    def test_major_stars_count(self):
        """There are exactly 14 major stars (十四主星)."""
        assert len(MAJOR_STARS) == 14

    def test_ziwei_group(self):
        """Zi Wei group includes 紫微."""
        assert "紫微" in MAJOR_STARS

    def test_tianfu_group(self):
        """Tian Fu group includes 天府."""
        assert "天府" in MAJOR_STARS

    def test_all_known_stars_present(self):
        """All 14 major stars are present."""
        expected = {
            "紫微", "天机", "太阳", "武曲", "天同", "廉贞",
            "天府", "太阴", "贪狼", "巨门", "天相", "天梁", "七杀", "破军",
        }
        assert set(MAJOR_STARS) == expected


class TestZiWeiChart:
    """Tests for ZiWeiChart calculation."""

    def test_chart_creation(self):
        """Chart can be created without error."""
        chart = create_ziwei_chart(year=1990, month=4, day=21, hour=14)
        assert chart is not None
        assert len(chart.palaces) == 12

    def test_palace_count(self):
        """Chart has exactly 12 palaces."""
        chart = create_ziwei_chart(year=1990, month=4, day=21, hour=14)
        assert len(chart.palaces) == 12

    def test_palace_names_present(self):
        """All 12 palace names are in the chart."""
        chart = create_ziwei_chart(year=1990, month=4, day=21, hour=14)
        for palace_name, _, _ in PALACE_NAMES:
            assert palace_name in chart.palaces

    def test_stars_placed(self):
        """Stars are placed across palaces."""
        chart = create_ziwei_chart(year=1990, month=4, day=21, hour=14)
        total_stars = sum(len(p.stars) for p in chart.palaces.values())
        # At least some major stars should be placed
        assert total_stars > 0

    def test_display_returns_string(self):
        """display() returns a non-empty string."""
        chart = create_ziwei_chart(year=1990, month=4, day=21, hour=14)
        result = chart.display()
        assert isinstance(result, str)
        assert len(result) > 0
        assert "紫微斗数" in result

    def test_branch_chars_valid(self):
        """Palace branch characters are valid earthly branches."""
        valid_branches = set("子丑寅卯辰巳午未申酉戌亥")
        chart = create_ziwei_chart(year=1990, month=4, day=21, hour=14)
        for palace in chart.palaces.values():
            assert palace.branch in valid_branches, f"Invalid branch: {palace.branch!r}"

    def test_gender_attribute(self):
        """Gender is stored correctly."""
        male_chart = create_ziwei_chart(1990, 4, 21, 14, gender="男")
        female_chart = create_ziwei_chart(1990, 4, 21, 14, gender="女")
        assert male_chart.gender == "男"
        assert female_chart.gender == "女"
