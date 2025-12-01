from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
import datetime as dt

from .config import ScheduleConfig, StaffMember, ShiftDefinition, RuleSet


@dataclass
class Assignment:
    staff_id: str
    day: dt.date
    shift_id: str


@dataclass
class ScheduleResult:
    assignments: List[Assignment]
    violations: List[str]


class SimpleGreedyScheduler:
    """Very simple scheduler for demonstration purposes.

    This is intentionally basic so it is easy to read and modify.
    For real-world loads, replace this with a proper constraint solver.
    """

    def __init__(self, config: ScheduleConfig):
        self.config = config

    def generate_week(
        self,
        start_date: dt.date,
        days: int = 7,
    ) -> ScheduleResult:
        assignments: List[Assignment] = []
        violations: List[str] = []

        staff_hours: Dict[str, float] = {m.id: 0.0 for m in self.config.staff}
        last_shift_end: Dict[str, Optional[dt.datetime]] = {
            m.id: None for m in self.config.staff
        }

        shifts = list(self.config.shifts.values())
        shifts_sorted = sorted(shifts, key=lambda s: s.hours, reverse=True)

        for offset in range(days):
            day = start_date + dt.timedelta(days=offset)
            for shift in shifts_sorted:
                candidate = self._pick_staff_for_shift(
                    day=day,
                    shift=shift,
                    staff_hours=staff_hours,
                    last_shift_end=last_shift_end,
                )
                if candidate is None:
                    violations.append(
                        f"No staff available for shift {shift.id} on {day.isoformat()}"
                    )
                    continue

                assignments.append(
                    Assignment(staff_id=candidate.id, day=day, shift_id=shift.id)
                )
                staff_hours[candidate.id] += shift.hours
                last_shift_end[candidate.id] = self._shift_end_datetime(day, shift)

        return ScheduleResult(assignments=assignments, violations=violations)

    # --- Helpers -------------------------------------------------------------

    def _shift_start_datetime(self, day: dt.date, shift: ShiftDefinition) -> dt.datetime:
        h, m = map(int, shift.start.split(":"))
        return dt.datetime.combine(day, dt.time(hour=h, minute=m))

    def _shift_end_datetime(self, day: dt.date, shift: ShiftDefinition) -> dt.datetime:
        h, m = map(int, shift.end.split(":"))
        end = dt.datetime.combine(day, dt.time(hour=h, minute=m))
        if end <= self._shift_start_datetime(day, shift):
            end += dt.timedelta(days=1)
        return end

    def _has_required_skills(self, member: StaffMember, shift: ShiftDefinition) -> bool:
        if not shift.required_skills:
            return True
        return all(skill in member.skills for skill in shift.required_skills)

    def _pick_staff_for_shift(
        self,
        day: dt.date,
        shift: ShiftDefinition,
        staff_hours: Dict[str, float],
        last_shift_end: Dict[str, Optional[dt.datetime]],
    ) -> Optional[StaffMember]:
        candidates: List[Tuple[StaffMember, float]] = []

        for member in self.config.staff:
            if not self._has_required_skills(member, shift):
                continue

            projected_hours = staff_hours[member.id] + shift.hours
            max_hours = min(member.max_hours_per_week, self.config.rules.max_hours_per_week)
            if projected_hours > max_hours:
                continue

            start_dt = self._shift_start_datetime(day, shift)
            last_end = last_shift_end[member.id]
            if last_end is not None:
                rest = (start_dt - last_end).total_seconds() / 3600.0
                if rest < self.config.rules.min_rest_hours:
                    continue

            candidates.append((member, staff_hours[member.id]))

        if not candidates:
            return None

        candidates.sort(key=lambda x: x[1])
        return candidates[0][0]
