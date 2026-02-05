from __future__ import annotations

from dataclasses import asdict
from typing import Any, Callable, Dict

from .config_io import load_config
from .constraints import ConstraintSuite
from .domain import Schedule
from .scoring import score_schedule
from .solver import solve


ToolFn = Callable[..., Dict[str, Any]]


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: Dict[str, ToolFn] = {}

    def register(self, name: str, fn: ToolFn) -> None:
        self._tools[name] = fn

    def call(self, name: str, **kwargs: Any) -> Dict[str, Any]:
        if name not in self._tools:
            raise KeyError(f"Tool not found: {name}")
        return self._tools[name](**kwargs)

    def list(self) -> Dict[str, str]:
        return {k: (v.__doc__ or "").strip() for k, v in self._tools.items()}


def schedule_generate(config_path: str) -> Dict[str, Any]:
    """Generate a schedule from a config path."""
    config = load_config(config_path)
    result = solve(config)
    return {
        "ok": result.ok,
        "iterations": result.iterations,
        "seconds": result.seconds,
        "notes": result.notes,
        "schedule": {"assignments": result.schedule.assignments},
    }


def schedule_validate(config_path: str, schedule: Dict[str, Any]) -> Dict[str, Any]:
    """Validate a schedule against hard constraints."""
    config = load_config(config_path)
    sch = Schedule(assignments={k: list(v) for k, v in schedule.get("assignments", {}).items()})
    report = ConstraintSuite.default().validate(config, sch)
    return report.to_dict()


def schedule_score(config_path: str, schedule: Dict[str, Any]) -> Dict[str, Any]:
    """Score a schedule with soft preferences."""
    config = load_config(config_path)
    sch = Schedule(assignments={k: list(v) for k, v in schedule.get("assignments", {}).items()})
    report = score_schedule(config, sch)
    return report.to_dict()


def schedule_explain(config_path: str, schedule: Dict[str, Any]) -> Dict[str, Any]:
    """Explain the schedule and major trade-offs."""
    config = load_config(config_path)
    sch = Schedule(assignments={k: list(v) for k, v in schedule.get("assignments", {}).items()})
    v = ConstraintSuite.default().validate(config, sch)
    s = score_schedule(config, sch)

    lines = []
    lines.append(f"# Schedule explanation — {config.meta.get('name','')}".strip())
    lines.append("")
    lines.append(f"- Valid: **{v.ok}**")
    lines.append(f"- Score: **{s.total:.3f}** (components: {s.components})")
    if s.notes:
        lines.append(f"- Notes: {', '.join(s.notes)}")

    lines.append("")
    lines.append("## Assignments")
    for sid in sorted(config.shifts.keys()):
        shift = config.shifts[sid]
        eids = sch.assignments.get(sid, [])
        lines.append(f"- `{sid}` {shift.start.isoformat()} → {shift.end.isoformat()} : {', '.join(eids) if eids else '(unfilled)'}")

    if not v.ok:
        lines.append("")
        lines.append("## Violations")
        for viol in v.violations[:50]:
            lines.append(f"- **{viol.code}**: {viol.message}")

    return {"markdown": "\n".join(lines)}


def default_registry() -> ToolRegistry:
    reg = ToolRegistry()
    reg.register("schedule_generate", schedule_generate)
    reg.register("schedule_validate", schedule_validate)
    reg.register("schedule_score", schedule_score)
    reg.register("schedule_explain", schedule_explain)
    return reg
