"""Tests for the calendar stem-branch module."""

from datetime import date

import pytest

from tianji.calendar.heavenly_stems import (
    HEAVENLY_STEMS,
    get_stem,
    get_stem_by_char,
    Element,
    Polarity,
    stem_relationship,
)
from tianji.calendar.earthly_branches import (
    EARTHLY_BRANCHES,
    get_branch,
    get_branch_by_char,
    get_branch_for_hour,
)
from tianji.calendar.stem_branch import (
    JIAZI_CYCLE,
    date_to_day_jiazi,
    get_jiazi,
    get_jiazi_by_char,
)


class TestHeavenlyStems:
    """Tests for 天干 (Heavenly Stems)."""

    def test_count(self):
        """There are exactly 10 heavenly stems."""
        assert len(HEAVENLY_STEMS) == 10

    def test_order(self):
        """Stems are in the correct order: 甲乙丙丁戊己庚辛壬癸."""
        expected = "甲乙丙丁戊己庚辛壬癸"
        actual = "".join(s.char for s in HEAVENLY_STEMS)
        assert actual == expected

    def test_elements(self):
        """Each pair of stems shares the same element."""
        assert HEAVENLY_STEMS[0].element == Element.WOOD  # 甲
        assert HEAVENLY_STEMS[1].element == Element.WOOD  # 乙
        assert HEAVENLY_STEMS[2].element == Element.FIRE  # 丙
        assert HEAVENLY_STEMS[3].element == Element.FIRE  # 丁
        assert HEAVENLY_STEMS[4].element == Element.EARTH  # 戊
        assert HEAVENLY_STEMS[5].element == Element.EARTH  # 己
        assert HEAVENLY_STEMS[6].element == Element.METAL  # 庚
        assert HEAVENLY_STEMS[7].element == Element.METAL  # 辛
        assert HEAVENLY_STEMS[8].element == Element.WATER  # 壬
        assert HEAVENLY_STEMS[9].element == Element.WATER  # 癸

    def test_polarity_alternates(self):
        """Yang and Yin alternate: 甲(阳), 乙(阴), 丙(阳), ..."""
        for i, stem in enumerate(HEAVENLY_STEMS):
            expected = Polarity.YANG if i % 2 == 0 else Polarity.YIN
            assert stem.polarity == expected, f"{stem.char} should be {expected}"

    def test_get_stem_by_index(self):
        assert get_stem(0).char == "甲"
        assert get_stem(9).char == "癸"
        assert get_stem(10).char == "甲"  # wraps around

    def test_get_stem_by_char(self):
        assert get_stem_by_char("甲").index == 0
        assert get_stem_by_char("癸").index == 9

    def test_get_stem_by_char_invalid(self):
        with pytest.raises(ValueError):
            get_stem_by_char("X")


class TestEarthlyBranches:
    """Tests for 地支 (Earthly Branches)."""

    def test_count(self):
        """There are exactly 12 earthly branches."""
        assert len(EARTHLY_BRANCHES) == 12

    def test_order(self):
        """Branches are in the correct order."""
        expected = "子丑寅卯辰巳午未申酉戌亥"
        actual = "".join(b.char for b in EARTHLY_BRANCHES)
        assert actual == expected

    def test_zodiac(self):
        """First and last zodiac animals are correct."""
        assert EARTHLY_BRANCHES[0].zodiac == "鼠"  # 子 = Rat
        assert EARTHLY_BRANCHES[11].zodiac == "猪"  # 亥 = Pig

    def test_get_branch_for_hour(self):
        """Test hour → branch mapping."""
        assert get_branch_for_hour(0).char == "子"
        assert get_branch_for_hour(23).char == "子"
        assert get_branch_for_hour(1).char == "丑"
        assert get_branch_for_hour(2).char == "丑"
        assert get_branch_for_hour(5).char == "卯"
        assert get_branch_for_hour(11).char == "午"
        assert get_branch_for_hour(12).char == "午"  # 11-12 is 午时
        assert get_branch_for_hour(13).char == "未"


class TestStemBranch:
    """Tests for 干支 (Stem-Branch) combinations."""

    def test_jiazi_cycle_count(self):
        """The 六十甲子 cycle has exactly 60 entries."""
        assert len(JIAZI_CYCLE) == 60

    def test_first_is_jiazi(self):
        """First entry is 甲子."""
        assert str(JIAZI_CYCLE[0]) == "甲子"

    def test_last_is_guihai(self):
        """Last entry (index 59) is 癸亥."""
        assert str(JIAZI_CYCLE[59]) == "癸亥"

    def test_no_duplicates(self):
        """All 60 entries are unique."""
        chars = [str(sb) for sb in JIAZI_CYCLE]
        assert len(set(chars)) == 60

    def test_reference_date(self):
        """1900-01-01 should be 甲子 day."""
        sb = date_to_day_jiazi(date(1900, 1, 1))
        assert str(sb) == "甲子"

    def test_known_date_1(self):
        """1900-01-02 should be 乙丑 day."""
        sb = date_to_day_jiazi(date(1900, 1, 2))
        assert str(sb) == "乙丑"

    def test_known_date_60(self):
        """1900-03-01 (day 60 from 1900-01-01) should be 癸亥."""
        sb = date_to_day_jiazi(date(1900, 3, 1))
        # 1900-03-01 is 59 days after 1900-01-01
        assert sb.index == 59
        assert str(sb) == "癸亥"

    def test_known_date_cycle(self):
        """60 days after 甲子 should be 甲子 again."""
        sb = date_to_day_jiazi(date(1900, 3, 2))
        assert str(sb) == "甲子"

    def test_get_jiazi_by_char(self):
        sb = get_jiazi_by_char("甲子")
        assert sb.index == 0
        assert sb.stem.char == "甲"
        assert sb.branch.char == "子"

    def test_get_jiazi_by_char_invalid(self):
        with pytest.raises(ValueError):
            get_jiazi_by_char("甲丑")  # Not a valid combo


class TestStemRelationship:
    """Tests for 十神 (Ten Gods) stem relationships."""

    def test_bijian(self):
        """Same element, same polarity → 比肩."""
        dm = get_stem_by_char("甲")  # Wood, Yang
        other = get_stem_by_char("甲")  # Wood, Yang
        assert stem_relationship(dm, other) == "比肩"

    def test_jiecai(self):
        """Same element, different polarity → 劫财."""
        dm = get_stem_by_char("甲")  # Wood, Yang
        other = get_stem_by_char("乙")  # Wood, Yin
        assert stem_relationship(dm, other) == "劫财"

    def test_shishen(self):
        """I produce, same polarity → 食神."""
        dm = get_stem_by_char("甲")  # Wood, Yang → produces Fire
        other = get_stem_by_char("丙")  # Fire, Yang
        assert stem_relationship(dm, other) == "食神"

    def test_shangguan(self):
        """I produce, different polarity → 伤官."""
        dm = get_stem_by_char("甲")  # Wood, Yang → produces Fire
        other = get_stem_by_char("丁")  # Fire, Yin
        assert stem_relationship(dm, other) == "伤官"

    def test_piancai(self):
        """I overcome, same polarity → 偏财."""
        dm = get_stem_by_char("甲")  # Wood → overcomes Earth
        other = get_stem_by_char("戊")  # Earth, Yang
        assert stem_relationship(dm, other) == "偏财"

    def test_zhengcai(self):
        """I overcome, different polarity → 正财."""
        dm = get_stem_by_char("甲")  # Wood → overcomes Earth
        other = get_stem_by_char("己")  # Earth, Yin
        assert stem_relationship(dm, other) == "正财"

    def test_qisha(self):
        """Overcomes me, same polarity → 七杀."""
        dm = get_stem_by_char("甲")  # Wood ← overcome by Metal
        other = get_stem_by_char("庚")  # Metal, Yang
        assert stem_relationship(dm, other) == "七杀"

    def test_zhengguan(self):
        """Overcomes me, different polarity → 正官."""
        dm = get_stem_by_char("甲")  # Wood ← overcome by Metal
        other = get_stem_by_char("辛")  # Metal, Yin
        assert stem_relationship(dm, other) == "正官"

    def test_pianyin(self):
        """Produces me, same polarity → 偏印."""
        dm = get_stem_by_char("甲")  # Wood ← produced by Water
        other = get_stem_by_char("壬")  # Water, Yang
        assert stem_relationship(dm, other) == "偏印"

    def test_zhengyin(self):
        """Produces me, different polarity → 正印."""
        dm = get_stem_by_char("甲")  # Wood ← produced by Water
        other = get_stem_by_char("癸")  # Water, Yin
        assert stem_relationship(dm, other) == "正印"
