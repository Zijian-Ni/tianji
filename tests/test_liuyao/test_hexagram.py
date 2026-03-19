"""Tests for hexagram definitions and lookups."""

import pytest

from tianji.liuyao.hexagram import (
    ALL_HEXAGRAMS,
    TRIGRAMS,
    Trigram,
    Hexagram,
    get_hexagram_by_number,
    get_hexagram_by_trigrams,
    lines_to_hexagram,
    HEXAGRAM_BY_NUMBER,
)


class TestTrigrams:
    """Tests for 八卦 (Eight Trigrams)."""

    def test_count(self):
        """There are exactly 8 trigrams."""
        assert len(TRIGRAMS) == 8

    def test_qian(self):
        """☰ 乾 = 111 = 7."""
        qian = TRIGRAMS[7]
        assert qian.name == "乾"
        assert qian.symbol == "☰"
        assert qian.lines == 7

    def test_kun(self):
        """☷ 坤 = 000 = 0."""
        kun = TRIGRAMS[0]
        assert kun.name == "坤"
        assert kun.symbol == "☷"
        assert kun.lines == 0

    def test_kan(self):
        """☵ 坎 = 010 = 2."""
        kan = TRIGRAMS[2]
        assert kan.name == "坎"
        assert kan.symbol == "☵"

    def test_li(self):
        """☲ 离 = 101 = 5."""
        li = TRIGRAMS[5]
        assert li.name == "离"
        assert li.symbol == "☲"

    def test_line_list(self):
        """Trigram line_list returns bottom-to-top order."""
        qian = TRIGRAMS[7]  # 111
        assert qian.line_list == [1, 1, 1]

        kun = TRIGRAMS[0]  # 000
        assert kun.line_list == [0, 0, 0]

        kan = TRIGRAMS[2]  # 010
        assert kan.line_list == [0, 1, 0]


class TestHexagrams:
    """Tests for 六十四卦 (64 Hexagrams)."""

    def test_count(self):
        """There are exactly 64 hexagrams."""
        assert len(ALL_HEXAGRAMS) == 64

    def test_qian_hexagram(self):
        """First hexagram is 乾 (Heaven over Heaven)."""
        h = get_hexagram_by_number(1)
        assert h.name == "乾"
        assert h.upper.name == "乾"
        assert h.lower.name == "乾"

    def test_kun_hexagram(self):
        """Second hexagram is 坤 (Earth over Earth)."""
        h = get_hexagram_by_number(2)
        assert h.name == "坤"
        assert h.upper.name == "坤"
        assert h.lower.name == "坤"

    def test_weiji_hexagram(self):
        """Last hexagram (#64) is 未济."""
        h = get_hexagram_by_number(64)
        assert h.name == "未济"

    def test_unique_numbers(self):
        """All hexagrams have unique numbers 1–64."""
        numbers = [h.number for h in ALL_HEXAGRAMS]
        assert sorted(numbers) == list(range(1, 65))

    def test_unique_names(self):
        """All hexagrams have unique names."""
        names = [h.name for h in ALL_HEXAGRAMS]
        assert len(set(names)) == 64

    def test_get_by_trigrams(self):
        """Lookup by upper/lower trigram codes."""
        # 乾(7) over 乾(7) = 乾卦 (#1)
        h = get_hexagram_by_trigrams(7, 7)
        assert h.number == 1

        # 坤(0) over 坤(0) = 坤卦 (#2)
        h = get_hexagram_by_trigrams(0, 0)
        assert h.number == 2

    def test_lines_property(self):
        """Hexagram lines returns 6 values."""
        h = get_hexagram_by_number(1)  # 乾: all yang
        assert h.lines == [1, 1, 1, 1, 1, 1]

        h = get_hexagram_by_number(2)  # 坤: all yin
        assert h.lines == [0, 0, 0, 0, 0, 0]

    def test_invalid_number(self):
        with pytest.raises(ValueError):
            get_hexagram_by_number(0)
        with pytest.raises(ValueError):
            get_hexagram_by_number(65)


class TestLinesToHexagram:
    """Tests for lines_to_hexagram conversion."""

    def test_all_yang(self):
        """Six yang lines = 乾."""
        h = lines_to_hexagram([1, 1, 1, 1, 1, 1])
        assert h.number == 1

    def test_all_yin(self):
        """Six yin lines = 坤."""
        h = lines_to_hexagram([0, 0, 0, 0, 0, 0])
        assert h.number == 2

    def test_old_yin_yang(self):
        """Old yin (6) and old yang (7) are normalized correctly."""
        h = lines_to_hexagram([6, 6, 6, 6, 6, 6])  # All old yin → all yin
        assert h.number == 2  # 坤

        h = lines_to_hexagram([7, 7, 7, 7, 7, 7])  # All old yang → all yang
        assert h.number == 1  # 乾

    def test_wrong_length(self):
        with pytest.raises(ValueError):
            lines_to_hexagram([1, 1, 1])
