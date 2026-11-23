"""
六爻起卦 (Hexagram Casting) methods.

Three methods for casting a hexagram:
1. 时间起卦 (Time-based): Use current datetime numbers
2. 数字起卦 (Number-based): Use any provided numbers
3. 铜钱摇卦 (Coin-based): Simulate three coin tosses per line
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from datetime import datetime

from tianji.calendar.almanac import BEIJING, beijing_time
from tianji.calendar.lunar import solar_to_lunar
from tianji.liuyao.hexagram import TRIGRAMS, Hexagram, lines_to_hexagram


@dataclass
class CastResult:
    """Result of a hexagram casting."""
    method: str                    # "time", "number", "coin"
    primary_hexagram: Hexagram     # 本卦 (primary hexagram)
    changed_hexagram: Hexagram | None  # 变卦 (changed hexagram, if moving lines exist)
    raw_lines: list[int]           # Raw line values (6=old yin, 7=young yang, 8=young yin, 9=old yang)
    moving_lines: list[int]        # Line positions (1-based) that are moving (动爻)
    input_data: dict               # Original input used for casting

    @property
    def has_moving_lines(self) -> bool:
        return len(self.moving_lines) > 0

    def display(self) -> None:
        """Print the casting result."""
        print("\n六爻起卦结果 (Casting Result)")
        print("─" * 40)
        print(f"  起卦方法: {self.method}")
        print(f"  本卦: {self.primary_hexagram}")
        if self.changed_hexagram:
            print(f"  变卦: {self.changed_hexagram}")
        print(f"  动爻: {self.moving_lines if self.moving_lines else '无'}")
        print("\n  爻象 (从下至上):")
        line_names = ["初", "二", "三", "四", "五", "上"]
        for i, (line, name) in enumerate(zip(self.raw_lines, line_names)):
            # Normalize for display
            is_yang = line in (7, 9, 1)
            is_moving = line in (6, 9)
            sym = "⚊" if is_yang else "⚋"
            moving_mark = " ← 动爻" if is_moving else ""
            print(f"    {name}爻: {sym} {'阳' if is_yang else '阴'}{moving_mark}")
        print("─" * 40)


def _lines_to_hexagram_with_changes(lines: list[int]) -> tuple[Hexagram, Hexagram | None, list[int]]:
    """Only old yin (6) and old yang (9) change, counted from the bottom."""
    if len(lines) != 6 or any(line not in (6, 7, 8, 9) for line in lines):
        raise ValueError("Expected six coin values in 6–9")
    primary = lines_to_hexagram(lines)
    moving = [i + 1 for i, line in enumerate(lines) if line in (6, 9)]
    changed = lines_to_hexagram([int(line in (6, 7)) for line in lines]) if moving else None
    return primary, changed, moving


def cast_from_lines(lines: list[int]) -> CastResult:
    """Read six recorded coin values in bottom-to-top order."""
    primary, changed, moving = _lines_to_hexagram_with_changes(lines)
    return CastResult("铜钱摇卦", primary, changed, list(lines), moving, {})


def _numbered_lines(upper: int, lower: int, moving: int) -> list[int]:
    # 先天 order: 1=乾 (code 7), through 8=坤 (code 0).
    bits = TRIGRAMS[7 - (lower - 1) % 8].line_list + TRIGRAMS[7 - (upper - 1) % 8].line_list
    raw = [7 if bit else 8 for bit in bits]
    position = (moving - 1) % 6
    raw[position] = 9 if bits[position] else 6
    return raw


def cast_by_time(dt: datetime | None = None) -> CastResult:
    """梅花年月日时法: lunar year branch, month, day and double-hour (子=1)."""
    dt = beijing_time(dt if dt is not None else datetime.now(BEIJING))
    lunar_year, month, day, _ = solar_to_lunar(dt.date())
    upper = (lunar_year - 4) % 12 + 1 + month + day
    total = upper + ((dt.hour + 1) // 2) % 12 + 1
    raw = _numbered_lines(upper, total, total)
    primary, changed, moving = _lines_to_hexagram_with_changes(raw)
    return CastResult("时间起卦", primary, changed, raw, moving, {
        "datetime": dt.isoformat(), "year": dt.year, "month": dt.month, "day": dt.day, "hour": dt.hour,
    })


def cast_by_numbers(num1: int, num2: int, num3: int | None = None) -> CastResult:
    """Use num1 for the upper trigram, num2 for the lower, and num3 or their sum for the moving line."""
    raw = _numbered_lines(num1, num2, num1 + num2 if num3 is None else num3)
    primary, changed, moving = _lines_to_hexagram_with_changes(raw)
    return CastResult("数字起卦", primary, changed, raw, moving, {"num1": num1, "num2": num2, "num3": num3})


def cast_by_coins(seed: int | None = None) -> CastResult:
    """
    铜钱摇卦 — Simulate coin toss hexagram casting.

    Three coins are tossed 6 times (once per line).
    Each coin: heads (正面) = 3, tails (反面) = 2.

    Sum of 3 coins:
    - 6 = 老阴 (3 tails): Old Yin, line is Yin, changes to Yang
    - 7 = 少阳 (2 tails + 1 head): Young Yang, stays Yang
    - 8 = 少阴 (1 tail + 2 heads): Young Yin, stays Yin
    - 9 = 老阳 (3 heads): Old Yang, line is Yang, changes to Yin

    Args:
        seed: Random seed for reproducibility (None = truly random)

    Returns:
        CastResult
    """
    rng = random.Random(seed)

    raw_lines = []
    for _ in range(6):
        # Toss 3 coins: heads=3, tails=2
        coins = [rng.choice([2, 3]) for _ in range(3)]
        total = sum(coins)  # 6, 7, 8, or 9
        raw_lines.append(total)

    primary, changed, moving_positions = _lines_to_hexagram_with_changes(raw_lines)

    return CastResult(
        method="铜钱摇卦",
        primary_hexagram=primary,
        changed_hexagram=changed,
        raw_lines=raw_lines,
        moving_lines=moving_positions,
        input_data={"seed": seed},
    )


def cast_hexagram(
    method: str = "time",
    dt: datetime | None = None,
    num1: int | None = None,
    num2: int | None = None,
    num3: int | None = None,
    seed: int | None = None,
) -> CastResult:
    """
    Unified hexagram casting interface.

    Args:
        method: "time", "number", or "coin"
        dt: Datetime for time-based casting
        num1, num2, num3: Numbers for number-based casting
        seed: Random seed for coin casting

    Returns:
        CastResult
    """
    method = method.lower()

    if method in ("time", "时间"):
        return cast_by_time(dt)
    elif method in ("number", "num", "数字"):
        if num1 is None or num2 is None:
            raise ValueError("Number-based casting requires num1 and num2")
        return cast_by_numbers(num1, num2, num3)
    elif method in ("coin", "coins", "铜钱"):
        return cast_by_coins(seed)
    else:
        raise ValueError(f"Unknown casting method: {method!r}. Use 'time', 'number', or 'coin'")
