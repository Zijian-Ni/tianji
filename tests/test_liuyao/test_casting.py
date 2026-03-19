"""Tests for hexagram casting methods."""

from datetime import datetime

import pytest

from tianji.liuyao.casting import (
    cast_by_time,
    cast_by_numbers,
    cast_by_coins,
    cast_hexagram,
    CastResult,
)


class TestCastByTime:
    """Tests for 时间起卦."""

    def test_returns_cast_result(self):
        result = cast_by_time(datetime(2024, 3, 15, 10, 0))
        assert isinstance(result, CastResult)
        assert result.method == "时间起卦"

    def test_has_primary_hexagram(self):
        result = cast_by_time(datetime(2024, 3, 15, 10, 0))
        assert result.primary_hexagram is not None
        assert result.primary_hexagram.number >= 1
        assert result.primary_hexagram.number <= 64

    def test_has_six_raw_lines(self):
        result = cast_by_time(datetime(2024, 3, 15, 10, 0))
        assert len(result.raw_lines) == 6

    def test_has_exactly_one_moving_line(self):
        """Time-based casting always produces exactly 1 moving line."""
        result = cast_by_time(datetime(2024, 3, 15, 10, 0))
        assert len(result.moving_lines) == 1

    def test_has_changed_hexagram(self):
        """With a moving line, there should be a changed hexagram."""
        result = cast_by_time(datetime(2024, 3, 15, 10, 0))
        assert result.changed_hexagram is not None

    def test_deterministic(self):
        """Same datetime should produce same result."""
        r1 = cast_by_time(datetime(2024, 3, 15, 10, 0))
        r2 = cast_by_time(datetime(2024, 3, 15, 10, 0))
        assert r1.primary_hexagram.number == r2.primary_hexagram.number
        assert r1.raw_lines == r2.raw_lines


class TestCastByNumbers:
    """Tests for 数字起卦."""

    def test_basic(self):
        result = cast_by_numbers(5, 3)
        assert isinstance(result, CastResult)
        assert result.method == "数字起卦"

    def test_with_third_number(self):
        result = cast_by_numbers(5, 3, 2)
        assert len(result.moving_lines) == 1

    def test_deterministic(self):
        r1 = cast_by_numbers(123, 456)
        r2 = cast_by_numbers(123, 456)
        assert r1.primary_hexagram.number == r2.primary_hexagram.number

    def test_different_numbers_different_results(self):
        r1 = cast_by_numbers(1, 2)
        r2 = cast_by_numbers(5, 7)
        # Different inputs should usually give different results
        # (not guaranteed, but very likely)
        assert (r1.primary_hexagram.number != r2.primary_hexagram.number) or \
               (r1.moving_lines != r2.moving_lines)


class TestCastByCoins:
    """Tests for 铜钱摇卦."""

    def test_basic(self):
        result = cast_by_coins(seed=42)
        assert isinstance(result, CastResult)
        assert result.method == "铜钱摇卦"

    def test_has_six_raw_lines(self):
        result = cast_by_coins(seed=42)
        assert len(result.raw_lines) == 6

    def test_raw_lines_in_valid_range(self):
        """Raw lines should be 6, 7, 8, or 9."""
        result = cast_by_coins(seed=42)
        for line in result.raw_lines:
            assert line in (6, 7, 8, 9), f"Invalid line value: {line}"

    def test_deterministic_with_seed(self):
        r1 = cast_by_coins(seed=42)
        r2 = cast_by_coins(seed=42)
        assert r1.raw_lines == r2.raw_lines

    def test_different_seeds(self):
        r1 = cast_by_coins(seed=42)
        r2 = cast_by_coins(seed=99)
        # Different seeds should usually give different results
        assert r1.raw_lines != r2.raw_lines


class TestCastHexagram:
    """Tests for the unified casting interface."""

    def test_time_method(self):
        result = cast_hexagram(method="time")
        assert result.method == "时间起卦"

    def test_number_method(self):
        result = cast_hexagram(method="number", num1=5, num2=3)
        assert result.method == "数字起卦"

    def test_coin_method(self):
        result = cast_hexagram(method="coin", seed=42)
        assert result.method == "铜钱摇卦"

    def test_invalid_method(self):
        with pytest.raises(ValueError):
            cast_hexagram(method="invalid")

    def test_number_method_missing_args(self):
        with pytest.raises(ValueError):
            cast_hexagram(method="number")
