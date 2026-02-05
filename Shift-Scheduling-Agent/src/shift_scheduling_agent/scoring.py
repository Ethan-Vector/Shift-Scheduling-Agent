from __future__ import annotations

from dataclasses import dataclass
from statistics import pstdev
from typing import Dict, List, Tuple

from .domain import Config, Schedule


@dataclass(frozen=True)
class ScoreReport:
    total: float
    components: Dict[str, float]
    notes: List[str]

    def to_dict(self) -> Dict:
        return {"total": self.total, "components": dict(self.components), "notes": list(self.notes)}


def score_schedule(config: Config, schedule: Schedule) -> ScoreReport:
    # Higher is better.
    comps: Dict[str, float] = {}
    notes: List[str] = []

    # Fairness: minimize standard deviation of shifts per employee
    emp_to = schedule.employee_shifts()
    counts = [len(emp_to.get(eid, [])) for eid in config.employees.keys()]
    fairness = -pstdev(counts) if len(counts) >= 2 else 0.0
    comps["fairness"] = fairness * config.preferences.fairness_weight

    # Preferences: reward when employee gets preferred skill tags
    pref_points = 0.0
    for sid, eids in schedule.assignments.items():
        shift = config.shifts.get(sid)
        if shift is None:
            continue
        for eid in eids:
            prefs = config.preferences.employee_shift_preferences.get(eid, {})
            prefer_skill = set(prefs.get("prefer_skill", []))
            if prefer_skill and shift.required_skills and (shift.required_skills & prefer_skill):
                pref_points += 1.0
    comps["preferences"] = pref_points * config.preferences.preference_weight

    total = sum(comps.values())
    if fairness == 0.0:
        notes.append("Fairness score is flat (small roster).")
    return ScoreReport(total=total, components=comps, notes=notes)
