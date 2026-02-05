from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Set

from .domain import Config, Employee, Preferences, Policies, Schedule, Shift, SolverConfig, TimeWindow


def _dt(s: str) -> datetime:
    # ISO without timezone → naive datetime
    return datetime.fromisoformat(s)


def load_config(path: str | Path) -> Config:
    p = Path(path)
    data = json.loads(p.read_text(encoding="utf-8"))

    employees: Dict[str, Employee] = {}
    for e in data["employees"]:
        availability = [TimeWindow(_dt(w["start"]), _dt(w["end"])) for w in e.get("availability", [])]
        employees[e["id"]] = Employee(
            id=e["id"],
            name=e.get("name", e["id"]),
            skills=set(e.get("skills", [])),
            availability=availability,
        )

    shifts: Dict[str, Shift] = {}
    for s in data["shifts"]:
        shifts[s["id"]] = Shift(
            id=s["id"],
            start=_dt(s["start"]),
            end=_dt(s["end"]),
            required_headcount=int(s.get("required_headcount", 1)),
            required_skills=set(s.get("required_skills", [])),
        )

    pol = data.get("policies", {})
    policies = Policies(
        max_shifts_per_week=int(pol.get("max_shifts_per_week", 5)),
        max_consecutive_shifts=int(pol.get("max_consecutive_shifts", 3)),
        min_rest_hours=int(pol.get("min_rest_hours", 10)),
    )

    pref = data.get("preferences", {})
    preferences = Preferences(
        fairness_weight=float(pref.get("fairness_weight", 1.0)),
        preference_weight=float(pref.get("preference_weight", 0.3)),
        employee_shift_preferences=pref.get("employee_shift_preferences", {}) or {},
    )

    sol = data.get("solver", {})
    solver = SolverConfig(
        max_seconds=float(sol.get("max_seconds", 2.0)),
        max_iterations=int(sol.get("max_iterations", 800)),
        random_seed=int(sol.get("random_seed", 7)),
        backtracking_limit=int(sol.get("backtracking_limit", 3000)),
    )

    meta = data.get("meta", {}) or {}

    return Config(
        employees=employees,
        shifts=shifts,
        policies=policies,
        preferences=preferences,
        solver=solver,
        meta=meta,
    )


def load_schedule(path: str | Path) -> Schedule:
    p = Path(path)
    data = json.loads(p.read_text(encoding="utf-8"))
    return Schedule(assignments={k: list(v) for k, v in data.get("assignments", {}).items()})


def save_schedule(schedule: Schedule, path: str | Path) -> None:
    p = Path(path)
    payload = {"assignments": schedule.assignments}
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(payload, indent=2), encoding="utf-8")
