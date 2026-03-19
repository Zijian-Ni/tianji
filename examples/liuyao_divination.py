#!/usr/bin/env python3
"""
六爻起卦示例 — Liu Yao Divination Example

Demonstrates how to:
1. Cast a hexagram using different methods
2. Display the hexagram
3. Perform full analysis (装卦)
4. Access individual line data
"""

from datetime import datetime
from tianji.liuyao import (
    cast_hexagram,
    cast_by_time,
    cast_by_numbers,
    cast_by_coins,
    LiuYaoAnalysis,
    get_hexagram_by_number,
)


def main():
    print("=" * 60)
    print("六爻起卦示例 — Liu Yao Divination Demo")
    print("=" * 60)

    # Method 1: Time-based casting
    print("\n📅 方法一: 时间起卦")
    print("-" * 40)
    result = cast_by_time(datetime(2024, 6, 15, 14, 30))
    result.display()

    # Full analysis
    analysis = LiuYaoAnalysis(result)
    analysis.display()

    # Method 2: Number-based casting
    print("\n\n🔢 方法二: 数字起卦 (num1=5, num2=3)")
    print("-" * 40)
    result2 = cast_by_numbers(5, 3)
    result2.display()

    analysis2 = LiuYaoAnalysis(result2)
    analysis2.display()

    # Method 3: Coin-based casting
    print("\n\n🪙 方法三: 铜钱摇卦 (seed=42)")
    print("-" * 40)
    result3 = cast_by_coins(seed=42)
    result3.display()

    analysis3 = LiuYaoAnalysis(result3)
    analysis3.display()

    # Using unified interface
    print("\n\n🔮 统一接口 cast_hexagram()")
    print("-" * 40)
    result4 = cast_hexagram(method="coin", seed=123)
    print(f"  本卦: {result4.primary_hexagram}")
    if result4.changed_hexagram:
        print(f"  变卦: {result4.changed_hexagram}")
    print(f"  动爻: {result4.moving_lines}")

    # Browse hexagrams
    print("\n\n📖 浏览卦象")
    print("-" * 40)
    for num in [1, 2, 29, 30, 63, 64]:
        h = get_hexagram_by_number(num)
        print(f"  第{num:2d}卦: {h.symbol} {h.name} — {h.description}")

    # Serialize to dict
    print("\n\n📋 卦象数据 (JSON-serializable):")
    import json
    print(json.dumps(analysis.to_dict(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
