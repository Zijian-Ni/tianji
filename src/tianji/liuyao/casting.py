"""
六爻起卦 (Hexagram Casting) methods.

Three methods for casting a hexagram:
1. 时间起卦 (Time-based): Use current datetime numbers
2. 数字起卦 (Number-based): Use any provided numbers
3. 铜钱摇卦 (Coin-based): Simulate three coin tosses per line
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from datetime import datetime

from tianji.liuyao.hexagram import Hexagram, lines_to_hexagram, get_hexagram_by_trigrams, TRIGRAMS


@dataclass
class CastResult:
    """Result of a hexagram casting."""
    method: str                    # "time", "number", "coin"
    primary_hexagram: Hexagram     # 本卦 (primary hexagram)
    changed_hexagram: Hexagram | None  # 变卦 (changed hexagram, if moving lines exist)
    raw_lines: list[int]           # Raw line values (6=old yin, 7=old yang, 8=young yin, 9=young yang)
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
        pol_names = {6: "六(动)", 7: "九(动)", 8: "六", 9: "九"}
        for i, (line, name) in enumerate(zip(self.raw_lines, line_names)):
            # Normalize for display
            is_yang = line in (7, 9, 1)
            is_moving = line in (6, 7)
            sym = "⚊" if is_yang else "⚋"
            moving_mark = " ← 动爻" if is_moving else ""
            print(f"    {name}爻: {sym} {'阳' if is_yang else '阴'}{moving_mark}")
        print("─" * 40)


def _lines_to_hexagram_with_changes(lines: list[int]) -> tuple[Hexagram, Hexagram | None, list[int]]:
    """
    Convert raw line values to primary and changed hexagrams.

    Raw line encoding:
    - 6 = Old Yin (老阴): Changes to Yang
    - 7 = Old Yang (老阳): Changes to Yin
    - 8 = Young Yin (少阴): Stays Yin
    - 9 = Young Yang (少阳): Stays Yang

    Args:
        lines: List of 6 raw line values

    Returns:
        (primary_hexagram, changed_hexagram_or_None, moving_line_positions)
    """
    # Primary hexagram: 6→yin(0), 7→yang(1), 8→yin(0), 9→yang(1)
    primary_lines = []
    for l in lines:
        if l in (6, 8):
            primary_lines.append(0)  # Yin
        else:
            primary_lines.append(1)  # Yang

    primary = lines_to_hexagram(primary_lines)

    # Moving lines
    moving_positions = [i + 1 for i, l in enumerate(lines) if l in (6, 7)]

    # Changed hexagram (if any moving lines)
    changed = None
    if moving_positions:
        changed_lines = []
        for l in lines:
            if l == 6:
                changed_lines.append(1)  # Old Yin → Yang
            elif l == 7:
                changed_lines.append(0)  # Old Yang → Yin
            elif l == 8:
                changed_lines.append(0)  # Young Yin stays Yin
            else:
                changed_lines.append(1)  # Young Yang stays Yang
        changed = lines_to_hexagram(changed_lines)

    return primary, changed, moving_positions


def cast_by_time(dt: datetime | None = None) -> CastResult:
    """
    时间起卦 — Cast hexagram using current or provided datetime.

    Algorithm:
    1. Take year + month + day + hour numbers
    2. Upper trigram = (year + month + day) % 8
    3. Lower trigram = (year + month + day + hour) % 8
    4. Moving line = (year + month + day + hour) % 6 + 1

    Args:
        dt: Datetime to use (defaults to now)

    Returns:
        CastResult
    """
    if dt is None:
        dt = datetime.now()

    year = dt.year
    month = dt.month
    day = dt.day
    hour = dt.hour

    # Sum of all components
    total = year + month + day + hour

    # Compute trigram indices (0–7, mapping to trigram codes)
    # Order: 乾1(7) 兑2(6) 离3(5) 震4(4) 巽5(3) 坎6(2) 艮7(1) 坤8(0)
    _ORDER = [7, 6, 5, 4, 3, 2, 1, 0]  # trigram codes in 先天八卦 order

    upper_idx = (year + month + day) % 8
    lower_idx = total % 8
    moving_line_pos = total % 6 + 1  # 1–6

    upper_code = _ORDER[upper_idx]
    lower_code = _ORDER[lower_idx]

    # Build 6 lines from trigrams
    upper_trigram = TRIGRAMS[upper_code]
    lower_trigram = TRIGRAMS[lower_code]

    raw_lines = []
    for i in range(3):
        raw_lines.append(9 if ((lower_code >> i) & 1) else 8)
    for i in range(3):
        raw_lines.append(9 if ((upper_code >> i) & 1) else 8)

    # Apply moving line
    ml_idx = moving_line_pos - 1
    if raw_lines[ml_idx] == 9:
        raw_lines[ml_idx] = 7  # Young Yang → Old Yang (moving)
    else:
        raw_lines[ml_idx] = 6  # Young Yin → Old Yin (moving)

    primary, changed, moving_positions = _lines_to_hexagram_with_changes(raw_lines)

    return CastResult(
        method="时间起卦",
        primary_hexagram=primary,
        changed_hexagram=changed,
        raw_lines=raw_lines,
        moving_lines=moving_positions,
        input_data={
            "datetime": dt.isoformat(),
            "year": year, "month": month, "day": day, "hour": hour,
        },
    )


def cast_by_numbers(num1: int, num2: int, num3: int | None = None) -> CastResult:
    """
    数字起卦 — Cast hexagram using provided numbers.

    Two-number method:
    - num1 → upper trigram (num1 % 8)
    - num2 → lower trigram (num2 % 8)
    - (num1 + num2) % 6 + 1 → moving line

    Three-number method:
    - num1 → upper trigram
    - num2 → lower trigram
    - num3 → moving line

    Args:
        num1: First number (determines upper trigram)
        num2: Second number (determines lower trigram)
        num3: Optional third number (determines moving line)

    Returns:
        CastResult
    """
    _ORDER = [7, 6, 5, 4, 3, 2, 1, 0]

    upper_idx = num1 % 8
    lower_idx = num2 % 8

    if num3 is not None:
        moving_line_pos = num3 % 6 + 1
    else:
        moving_line_pos = (num1 + num2) % 6 + 1

    upper_code = _ORDER[upper_idx]
    lower_code = _ORDER[lower_idx]

    # Build raw lines
    raw_lines = []
    for i in range(3):
        raw_lines.append(9 if ((lower_code >> i) & 1) else 8)
    for i in range(3):
        raw_lines.append(9 if ((upper_code >> i) & 1) else 8)

    # Apply moving line
    ml_idx = moving_line_pos - 1
    if raw_lines[ml_idx] == 9:
        raw_lines[ml_idx] = 7
    else:
        raw_lines[ml_idx] = 6

    primary, changed, moving_positions = _lines_to_hexagram_with_changes(raw_lines)

    return CastResult(
        method="数字起卦",
        primary_hexagram=primary,
        changed_hexagram=changed,
        raw_lines=raw_lines,
        moving_lines=moving_positions,
        input_data={"num1": num1, "num2": num2, "num3": num3},
    )


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
