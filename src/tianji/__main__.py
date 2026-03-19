"""
tianji CLI — command-line interface for Chinese metaphysics calculations.

Usage:
    tianji bazi --date 1990-05-15 --time 14:30 --gender male
    tianji liuyao --method time
    tianji liuyao --method number --num1 5 --num2 3
    tianji serve --port 8000
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, date


def cmd_bazi(args: argparse.Namespace) -> None:
    """Run BaZi chart calculation."""
    from tianji.bazi import BaZiChart
    from tianji.bazi.ten_gods import display_ten_gods
    from tianji.bazi.five_elements import elements_from_chart
    from tianji.bazi.day_master import analyze_day_master_strength
    from tianji.bazi.luck_pillars import compute_luck_pillars
    from tianji.bazi.relationships import relationships_from_chart

    # Parse date and time
    birth_date = date.fromisoformat(args.date)
    parts = args.time.split(":")
    hour, minute = int(parts[0]), int(parts[1]) if len(parts) > 1 else 0
    birth_dt = datetime(birth_date.year, birth_date.month, birth_date.day, hour, minute)

    chart = BaZiChart(birth_dt=birth_dt, gender=args.gender)
    chart.display()

    if args.detail:
        display_ten_gods(chart)
        elements_from_chart(chart).display()
        analyze_day_master_strength(chart).display()
        compute_luck_pillars(chart).display()
        relationships_from_chart(chart).display()


def cmd_liuyao(args: argparse.Namespace) -> None:
    """Run Liu Yao hexagram casting."""
    from tianji.liuyao import cast_hexagram, LiuYaoAnalysis

    result = cast_hexagram(
        method=args.method,
        num1=getattr(args, "num1", None),
        num2=getattr(args, "num2", None),
        num3=getattr(args, "num3", None),
        seed=getattr(args, "seed", None),
    )
    result.display()

    if args.detail:
        analysis = LiuYaoAnalysis(result)
        analysis.display()


def cmd_serve(args: argparse.Namespace) -> None:
    """Start the FastAPI server."""
    try:
        import uvicorn
    except ImportError:
        print("Error: uvicorn is required. Install with: pip install uvicorn")
        sys.exit(1)

    uvicorn.run(
        "tianji.api.app:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
    )


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="tianji",
        description="天机 — Chinese Metaphysics CLI (八字/六爻/紫微斗数)",
    )
    parser.add_argument("--version", action="version", version="tianji 0.1.0")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # BaZi subcommand
    bazi_parser = subparsers.add_parser("bazi", help="八字排盘 (BaZi Chart)")
    bazi_parser.add_argument("--date", required=True, help="Birth date (YYYY-MM-DD)")
    bazi_parser.add_argument("--time", default="12:00", help="Birth time (HH:MM)")
    bazi_parser.add_argument("--gender", default="male", choices=["male", "female"])
    bazi_parser.add_argument("--detail", action="store_true", help="Show detailed analysis")

    # Liu Yao subcommand
    liuyao_parser = subparsers.add_parser("liuyao", help="六爻起卦 (Liu Yao Casting)")
    liuyao_parser.add_argument("--method", default="time", choices=["time", "number", "coin"])
    liuyao_parser.add_argument("--num1", type=int, help="First number (for number method)")
    liuyao_parser.add_argument("--num2", type=int, help="Second number")
    liuyao_parser.add_argument("--num3", type=int, help="Third number (optional)")
    liuyao_parser.add_argument("--seed", type=int, help="Random seed (for coin method)")
    liuyao_parser.add_argument("--detail", action="store_true", help="Show full analysis")

    # Serve subcommand
    serve_parser = subparsers.add_parser("serve", help="启动 API 服务")
    serve_parser.add_argument("--host", default="0.0.0.0")
    serve_parser.add_argument("--port", type=int, default=8000)
    serve_parser.add_argument("--reload", action="store_true")

    args = parser.parse_args()

    if args.command == "bazi":
        cmd_bazi(args)
    elif args.command == "liuyao":
        cmd_liuyao(args)
    elif args.command == "serve":
        cmd_serve(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
