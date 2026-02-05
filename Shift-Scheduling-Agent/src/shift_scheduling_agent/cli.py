from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict

from .agent import AgentState, ShiftSchedulingAgent
from .config_io import load_schedule, save_schedule
from .domain import Schedule
from .tools import default_registry


def _load_schedule_dict(path: str | Path) -> Dict[str, Any]:
    sch = load_schedule(path)
    return {"assignments": sch.assignments}


def main() -> None:
    parser = argparse.ArgumentParser(prog="shift-agent")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_gen = sub.add_parser("generate", help="Generate a schedule from a config.")
    p_gen.add_argument("--config", required=True)
    p_gen.add_argument("--out", required=True)

    p_val = sub.add_parser("validate", help="Validate a schedule.")
    p_val.add_argument("--config", required=True)
    p_val.add_argument("--schedule", required=True)

    p_score = sub.add_parser("score", help="Score a schedule.")
    p_score.add_argument("--config", required=True)
    p_score.add_argument("--schedule", required=True)

    p_exp = sub.add_parser("explain", help="Explain a schedule.")
    p_exp.add_argument("--config", required=True)
    p_exp.add_argument("--schedule", required=True)
    p_exp.add_argument("--out", default="", help="Optional output markdown path.")

    p_chat = sub.add_parser("chat", help="Run an offline agent-like chat loop.")
    p_chat.add_argument("--config", required=True)
    p_chat.add_argument("--schedule-path", default="outputs/last_schedule.json")

    args = parser.parse_args()
    reg = default_registry()

    if args.cmd == "generate":
        out = reg.call("schedule_generate", config_path=args.config)
        schedule_dict = out["schedule"]
        save_schedule(Schedule(assignments=schedule_dict["assignments"]), args.out)
        print(json.dumps({k: v for k, v in out.items() if k != "schedule"}, indent=2))
        print(f"Wrote schedule to: {args.out}")
        return

    if args.cmd in {"validate", "score", "explain"}:
        schedule_dict = _load_schedule_dict(args.schedule)
        tool = {
            "validate": "schedule_validate",
            "score": "schedule_score",
            "explain": "schedule_explain",
        }[args.cmd]
        out = reg.call(tool, config_path=args.config, schedule=schedule_dict)

        if args.cmd == "explain":
            md = out["markdown"]
            if args.out:
                Path(args.out).write_text(md, encoding="utf-8")
                print(f"Wrote: {args.out}")
            else:
                print(md)
        else:
            print(json.dumps(out, indent=2))
        return

    if args.cmd == "chat":
        agent = ShiftSchedulingAgent(registry=reg)
        state = AgentState(config_path=args.config, last_schedule_path=Path(args.schedule_path))
        agent.run_chat(state)
        return


if __name__ == "__main__":
    main()
