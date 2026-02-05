from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
from typing import Callable, Dict, List, Sequence, Tuple

from .domain import Config, Schedule


@dataclass(frozen=True)
class Violation:
    code: str
    message: str
    shift_id: str | None = None
    employee_id: str | None = None


ConstraintFn = Callable[[Config, Schedule], List[Violation]]


def _employee_availability_violation(config: Config, schedule: Schedule) -> List[Violation]:
    out: List[Violation] = []
    for sid, eids in schedule.assignments.items():
        shift = config.shifts.get(sid)
        if shift is None:
            out.append(Violation(code="UNKNOWN_SHIFT", message=f"Unknown shift: {sid}", shift_id=sid))
            continue
        for eid in eids:
            emp = config.employees.get(eid)
            if emp is None:
                out.append(Violation(code="UNKNOWN_EMPLOYEE", message=f"Unknown employee: {eid}", shift_id=sid, employee_id=eid))
                continue
            if not any(w.contains(shift.start, shift.end) for w in emp.availability):
                out.append(
                    Violation(
                        code="NOT_AVAILABLE",
                        message=f"{eid} not available for shift {sid}",
                        shift_id=sid,
                        employee_id=eid,
                    )
                )
    return out


def _skills_violation(config: Config, schedule: Schedule) -> List[Violation]:
    out: List[Violation] = []
    for sid, eids in schedule.assignments.items():
        shift = config.shifts.get(sid)
        if shift is None:
            continue
        req = shift.required_skills
        if not req:
            continue
        for eid in eids:
            emp = config.employees.get(eid)
            if emp is None:
                continue
            if not req.issubset(emp.skills):
                out.append(
                    Violation(
                        code="MISSING_SKILL",
                        message=f"{eid} missing skill(s) for {sid}: requires {sorted(req)}",
                        shift_id=sid,
                        employee_id=eid,
                    )
                )
    return out


def _coverage_violation(config: Config, schedule: Schedule) -> List[Violation]:
    out: List[Violation] = []
    for sid, shift in config.shifts.items():
        assigned = schedule.assignments.get(sid, [])
        if len(assigned) < shift.required_headcount:
            out.append(
                Violation(
                    code="UNDER_COVERAGE",
                    message=f"Shift {sid} needs {shift.required_headcount} but has {len(assigned)}",
                    shift_id=sid,
                )
            )
    return out


def _max_shifts_per_week_violation(config: Config, schedule: Schedule) -> List[Violation]:
    out: List[Violation] = []
    emp_to_shifts = schedule.employee_shifts()
    cap = config.policies.max_shifts_per_week
    for eid, sids in emp_to_shifts.items():
        if len(sids) > cap:
            out.append(
                Violation(
                    code="MAX_SHIFTS_WEEK",
                    message=f"{eid} assigned {len(sids)} shifts (cap {cap})",
                    employee_id=eid,
                )
            )
    return out


def _min_rest_violation(config: Config, schedule: Schedule) -> List[Violation]:
    out: List[Violation] = []
    min_rest = timedelta(hours=config.policies.min_rest_hours)

    emp_to_shift_ids = schedule.employee_shifts()
    for eid, sids in emp_to_shift_ids.items():
        shifts = [config.shifts[sid] for sid in sids if sid in config.shifts]
        shifts.sort(key=lambda x: x.start)
        for a, b in zip(shifts, shifts[1:]):
            if b.start - a.end < min_rest:
                out.append(
                    Violation(
                        code="MIN_REST",
                        message=f"{eid} has insufficient rest between {a.id} and {b.id}",
                        employee_id=eid,
                    )
                )
    return out


def _max_consecutive_violation(config: Config, schedule: Schedule) -> List[Violation]:
    out: List[Violation] = []
    cap = config.policies.max_consecutive_shifts
    emp_to_shift_ids = schedule.employee_shifts()

    for eid, sids in emp_to_shift_ids.items():
        shifts = [config.shifts[sid] for sid in sids if sid in config.shifts]
        shifts.sort(key=lambda x: x.start)
        run = 1
        for prev, cur in zip(shifts, shifts[1:]):
            # "Consecutive" heuristic: next shift starts within 18 hours of previous end
            if cur.start - prev.end <= timedelta(hours=18):
                run += 1
            else:
                run = 1
            if run > cap:
                out.append(
                    Violation(
                        code="MAX_CONSECUTIVE",
                        message=f"{eid} exceeds max consecutive shifts ({cap})",
                        employee_id=eid,
                    )
                )
                break
    return out


@dataclass(frozen=True)
class ValidationReport:
    ok: bool
    violations: List[Violation]

    def to_dict(self) -> Dict:
        return {"ok": self.ok, "violations": [v.__dict__ for v in self.violations]}


class ConstraintSuite:
    def __init__(self, constraints: Sequence[Tuple[str, ConstraintFn]]):
        self._constraints = list(constraints)

    @staticmethod
    def default() -> "ConstraintSuite":
        return ConstraintSuite(
            [
                ("coverage", _coverage_violation),
                ("availability", _employee_availability_violation),
                ("skills", _skills_violation),
                ("max_shifts_per_week", _max_shifts_per_week_violation),
                ("min_rest_hours", _min_rest_violation),
                ("max_consecutive_shifts", _max_consecutive_violation),
            ]
        )

    def validate(self, config: Config, schedule: Schedule) -> ValidationReport:
        violations: List[Violation] = []
        for _, fn in self._constraints:
            violations.extend(fn(config, schedule))
        return ValidationReport(ok=(len(violations) == 0), violations=violations)
