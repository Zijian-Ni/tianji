#!/usr/bin/env python3
"""
八字排盘示例 — BaZi Reading Example

Demonstrates how to:
1. Create a BaZi chart from a birth datetime
2. Display the four pillars
3. Compute Ten Gods (十神)
4. Analyze Five Elements (五行)
5. Judge Day Master strength (日主强弱)
6. Calculate Luck Pillars (大运)
7. Analyze branch relationships (刑冲合害)
"""

from datetime import datetime
from tianji.bazi import (
    BaZiChart,
    ten_gods_from_chart,
    display_ten_gods,
    elements_from_chart,
    analyze_day_master_strength,
    compute_luck_pillars,
    relationships_from_chart,
)


def main():
    # Example: 1990年5月15日 14:30 男命
    birth_dt = datetime(1990, 5, 15, 14, 30)
    print(f"出生时间: {birth_dt}")
    print(f"性别: 男\n")

    # 1. Create the chart
    chart = BaZiChart(birth_dt=birth_dt, gender="male")
    chart.display()

    # 2. Ten Gods
    print("\n" + "=" * 50)
    display_ten_gods(chart)

    # 3. Five Elements
    print("\n" + "=" * 50)
    elements = elements_from_chart(chart)
    elements.display()
    missing = elements.missing_elements()
    if missing:
        print(f"  ⚠ 五行缺: {', '.join(e.value for e in missing)}")
    print(f"  最旺: {elements.strongest_element().value}")
    print(f"  最弱: {elements.weakest_element().value}")

    # 4. Day Master Strength
    print("\n" + "=" * 50)
    strength = analyze_day_master_strength(chart)
    strength.display()

    # 5. Luck Pillars
    print("\n" + "=" * 50)
    luck = compute_luck_pillars(chart)
    luck.display()

    # 6. Branch Relationships
    print("\n" + "=" * 50)
    rels = relationships_from_chart(chart)
    rels.display()

    # 7. Serialize to dict (for API / LLM use)
    print("\n" + "=" * 50)
    print("\n命盘数据 (JSON-serializable):")
    import json
    print(json.dumps(chart.to_dict(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
