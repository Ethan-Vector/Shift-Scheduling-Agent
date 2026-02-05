from __future__ import annotations

import random
import time
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

from .constraints import ConstraintSuite
from .domain import Config, Schedule
from .scoring import score_schedule


@dataclass
class SolveResult:
    schedule: Schedule
    ok: bool
    iterations: int
    seconds: float
    notes: List[str]


def _eligible_employees(config: Config, shift_id: str) -> List[str]:
    shift = config.shifts[shift_id]
    out: List[str] = []
    for eid, emp in config.employees.items():
        if shift.required_skills and not shift.required_skills.issubset(emp.skills):
            continue
        if not any(w.contains(shift.start, shift.end) for w in emp.availability):
            continue
        out.append(eid)
    return out


def _greedy_construct(config: Config, rnd: random.Random) -> Schedule:
    schedule = Schedule(assignments={})
    # Sort shifts by "hardness": fewer eligible employees first
    shift_ids = list(config.shifts.keys())
    shift_ids.sort(key=lambda sid: len(_eligible_employees(config, sid)))

    emp_load: Dict[str, int] = {eid: 0 for eid in config.employees.keys()}

    for sid in shift_ids:
        req = config.shifts[sid].required_headcount
        candidates = _eligible_employees(config, sid)

        # Pick employees with smallest load first (fairness-ish), then random tie-break
        rnd.shuffle(candidates)
        candidates.sort(key=lambda eid: emp_load[eid])

        chosen: List[str] = []
        for eid in candidates:
            if len(chosen) >= req:
                break
            if emp_load[eid] >= config.policies.max_shifts_per_week:
                continue
            chosen.append(eid)
            emp_load[eid] += 1

        schedule.assignments[sid] = chosen

    return schedule


def _try_swap_improvements(config: Config, schedule: Schedule, rnd: random.Random, max_steps: int) -> Tuple[Schedule, int]:
    # Local improvement: attempt swaps to increase score while staying valid.
    suite = ConstraintSuite.default()
    best = schedule.copy()
    best_score = score_schedule(config, best).total
    steps = 0

    shift_ids = list(config.shifts.keys())
    employees = list(config.employees.keys())

    while steps < max_steps:
        steps += 1

        s1 = rnd.choice(shift_ids)
        s2 = rnd.choice(shift_ids)
        if s1 == s2:
            continue

        a1 = best.assignments.get(s1, [])
        a2 = best.assignments.get(s2, [])
        if not a1 or not a2:
            continue

        e1 = rnd.choice(a1)
        e2 = rnd.choice(a2)
        if e1 == e2:
            continue

        # propose swap
        cand = best.copy()
        cand.assignments[s1] = [e2 if x == e1 else x for x in a1]
        cand.assignments[s2] = [e1 if x == e2 else x for x in a2]

        report = suite.validate(config, cand)
        if not report.ok:
            continue

        cand_score = score_schedule(config, cand).total
        if cand_score >= best_score:
            best = cand
            best_score = cand_score

    return best, steps


def solve(config: Config) -> SolveResult:
    rnd = random.Random(config.solver.random_seed)
    start = time.time()

    notes: List[str] = []
    suite = ConstraintSuite.default()

    schedule = _greedy_construct(config, rnd)
    report = suite.validate(config, schedule)

    # If already OK, still try minor improvements for better fairness/preferences
    iterations = 0
    max_iter = max(1, int(config.solver.max_iterations))
    time_budget = max(0.1, float(config.solver.max_seconds))

    while (time.time() - start) < time_budget and iterations < max_iter:
        iterations += 1
        improved, _ = _try_swap_improvements(config, schedule, rnd, max_steps=20)
        if improved.assignments != schedule.assignments:
            schedule = improved
        # stop early if valid and improvements plateau-ish (lightweight condition)
        if iterations % 50 == 0:
            report = suite.validate(config, schedule)
            if report.ok:
                notes.append("Valid schedule found; continuing small improvements within budget.")

    final_report = suite.validate(config, schedule)
    ok = final_report.ok
    seconds = time.time() - start
    if not ok:
        notes.append(f"Schedule not fully valid ({len(final_report.violations)} violation(s)). Consider relaxing policies or adding staff.")
    return SolveResult(schedule=schedule, ok=ok, iterations=iterations, seconds=seconds, notes=notes)
