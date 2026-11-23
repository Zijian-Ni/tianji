"""Cross-runtime regression cases from the HKO almanac and the classical worked examples in README."""

import json
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import pytest

from tianji.bazi.chart import BaZiChart
from tianji.bazi.luck_pillars import compute_luck_pillars
from tianji.calendar import get_solar_term_datetime, lunar_to_solar, solar_to_lunar
from tianji.liuyao.casting import cast_by_numbers, cast_by_time, cast_from_lines
from tianji.ziwei.chart import create_ziwei_chart

CASES = json.loads((Path(__file__).parent / "fixtures/calendar_cases.json").read_text(encoding="utf-8"))


@pytest.mark.parametrize("year,term,expected", CASES["solar_terms"])
def test_published_beijing_minute(year, term, expected):
    assert get_solar_term_datetime(year, term) == datetime.fromisoformat(expected)


@pytest.mark.parametrize("iso,year,month,day,leap", CASES["lunar"])
def test_lunar_date_both_directions(iso, year, month, day, leap):
    solar = date.fromisoformat(iso)
    assert solar_to_lunar(solar) == (year, month, day, leap)
    assert lunar_to_solar(year, month, day, leap) == solar


@pytest.mark.parametrize("iso,year,month", CASES["pillars"])
def test_pillars_change_at_beijing_minute(iso, year, month):
    dt = datetime.fromisoformat(iso)
    chart = BaZiChart(dt)
    assert (chart.year_pillar.char, chart.month_pillar.char) == (year, month)
    utc = dt.replace(tzinfo=timezone(timedelta(hours=8))).astimezone(timezone.utc)
    assert BaZiChart(utc).pillars == chart.pillars


def test_leap_day_luck_start():
    result = compute_luck_pillars(BaZiChart(datetime(2000, 2, 29, 8)))
    assert result.start_date == date(2001, 2, 28)


@pytest.mark.parametrize("n1,n2,n3,primary,changed,moving", CASES["numbers"])
def test_number_cast(n1, n2, n3, primary, changed, moving):
    cast = cast_by_numbers(n1, n2, n3)
    assert (cast.primary_hexagram.number, cast.changed_hexagram.number, cast.moving_lines) == (primary, changed, moving)


def test_plum_blossom_example_and_coins():
    cast = cast_by_time(datetime(2025, 1, 16, 16))
    assert cast.raw_lines == [9, 8, 7, 7, 7, 8]
    assert (cast.primary_hexagram.number, cast.changed_hexagram.number) == (49, 31)
    assert cast_from_lines([7] * 6).changed_hexagram is None
    assert cast_from_lines([9] * 6).changed_hexagram.number == 2


@pytest.mark.parametrize("y,m,d,h,life,body,sibling,ju,ziwei,tianfu", CASES["ziwei"])
def test_classical_palaces(y, m, d, h, life, body, sibling, ju, ziwei, tianfu):
    chart = create_ziwei_chart(y, m, d, h)
    assert (chart.palaces["命宫"].branch, chart.body_branch, chart.palaces["兄弟宫"].branch) == (life, body, sibling)
    assert chart.wu_xing_ju == ju
    stars = {star: palace.branch for palace in chart.palaces.values() for star in palace.stars}
    assert len(stars) == 14
    assert (stars["紫微"], stars["天府"]) == (ziwei, tianfu)
