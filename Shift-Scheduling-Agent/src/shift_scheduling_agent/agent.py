from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

from .config_io import load_schedule, save_schedule
from .domain import Schedule
from .mock_llm import MockLLM
from .tools import ToolRegistry, default_registry


@dataclass
class AgentState:
    config_path: str
    last_schedule_path: Path
    max_steps: int = 20


class ShiftSchedulingAgent:
    def __init__(self, registry: ToolRegistry | None = None, llm: MockLLM | None = None) -> None:
        self.registry = registry or default_registry()
        self.llm = llm or MockLLM()

    def run_chat(self, state: AgentState) -> None:
        print("ShiftSchedulingAgent (offline) — type 'quit' to exit.")
        print("Try: 'generate schedule', 'validate', 'score', 'explain'")
        print()

        last_schedule: Optional[Dict[str, Any]] = None

        for _ in range(state.max_steps):
            user = input("> ").strip()
            if user.lower() in {"quit", "exit"}:
                return

            call = self.llm.route(user)
            if call is None:
                print("I can: generate | validate | score | explain. (offline router)")
                continue

            if call.name == "schedule_generate":
                out = self.registry.call(call.name, config_path=state.config_path)
                last_schedule = out["schedule"]
                save_schedule(Schedule(assignments=last_schedule["assignments"]), state.last_schedule_path)
                print(f"Generated schedule → {state.last_schedule_path}")
                if out.get("notes"):
                    print("Notes:", "; ".join(out["notes"]))
                continue

            # other tools expect schedule present
            if last_schedule is None:
                if state.last_schedule_path.exists():
                    loaded = load_schedule(state.last_schedule_path)
                    last_schedule = {"assignments": loaded.assignments}
                else:
                    print("No schedule yet. Run 'generate' first.")
                    continue

            out = self.registry.call(call.name, config_path=state.config_path, schedule=last_schedule)
            if call.name == "schedule_explain":
                print(out["markdown"])
            else:
                print(json.dumps(out, indent=2))
