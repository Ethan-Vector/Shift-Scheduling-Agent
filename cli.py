from __future__ import annotations
import argparse
import datetime as dt
import sys
from pathlib import Path

from shift_agent.config import ScheduleConfig
from shift_agent.agent import ShiftSchedulingAgent


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Agentic Shift Scheduling CLI",
    )
    parser.add_argument(
        "--staff",
        required=True,
        help="Path to staff YAML file",
    )
    parser.add_argument(
        "--shifts",
        required=True,
        help="Path to shifts YAML file",
    )
    parser.add_argument(
        "--rules",
        required=True,
        help="Path to rules YAML file",
    )
    parser.add_argument(
        "--start-date",
        help="Start date (YYYY-MM-DD). Defaults to Monday of current week.",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=7,
        help="Number of days to schedule (default: 7)",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("draft", help="Generate and print a draft schedule")
    subparsers.add_parser("explain", help="Generate schedule and ask LLM for explanation")

    return parser.parse_args(argv)


def _parse_date(date_str):
    if not date_str:
        return None
    return dt.datetime.strptime(date_str, "%Y-%m-%d").date()


def main(argv=None):
    args = parse_args(argv)

    config = ScheduleConfig.from_files(
        staff_path=args.staff,
        shifts_path=args.shifts,
        rules_path=args.rules,
    )
    agent = ShiftSchedulingAgent(config=config)

    start_date = _parse_date(args.start_date)

    if args.command == "draft":
        result = agent.draft_schedule(start_date=start_date, days=args.days)
        print_schedule(config, result)
    elif args.command == "explain":
        text = agent.explain_schedule(start_date=start_date, days=args.days)
        print(text)
    else:
        raise SystemExit(f"Unknown command: {args.command}")


def print_schedule(config, result):
    print("# Draft schedule")
    for a in result.assignments:
        shift = config.shifts[a.shift_id]
        print(
            f"{a.day.isoformat()} | {shift.label:12} {shift.start}-{shift.end} -> {a.staff_id}"
        )
    if result.violations:
        print("\n# Violations / warnings:")
        for v in result.violations:
            print(f"- {v}")


if __name__ == "__main__":
    main()
