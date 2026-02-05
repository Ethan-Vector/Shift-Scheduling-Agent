from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Sequence, Set, Tuple


@dataclass(frozen=True)
class TimeWindow:
    start: datetime
    end: datetime

    def contains(self, start: datetime, end: datetime) -> bool:
        return self.start <= start and end <= self.end


@dataclass(frozen=True)
class Employee:
    id: str
    name: str
    skills: Set[str]
    availability: List[TimeWindow] = field(default_factory=list)


@dataclass(frozen=True)
class Shift:
    id: str
    start: datetime
    end: datetime
    required_headcount: int
    required_skills: Set[str] = field(default_factory=set)

    @property
    def duration_hours(self) -> float:
        return (self.end - self.start).total_seconds() / 3600.0


@dataclass(frozen=True)
class Policies:
    max_shifts_per_week: int = 5
    max_consecutive_shifts: int = 3
    min_rest_hours: int = 10


@dataclass(frozen=True)
class Preferences:
    fairness_weight: float = 1.0
    preference_weight: float = 0.3
    employee_shift_preferences: Dict[str, Dict[str, List[str]]] = field(default_factory=dict)


@dataclass(frozen=True)
class SolverConfig:
    max_seconds: float = 2.0
    max_iterations: int = 800
    random_seed: int = 7
    backtracking_limit: int = 3000


@dataclass(frozen=True)
class Config:
    employees: Dict[str, Employee]
    shifts: Dict[str, Shift]
    policies: Policies
    preferences: Preferences
    solver: SolverConfig
    meta: Dict[str, str] = field(default_factory=dict)


@dataclass
class Schedule:
    # shift_id -> list of employee_ids assigned
    assignments: Dict[str, List[str]] = field(default_factory=dict)

    def copy(self) -> "Schedule":
        return Schedule(assignments={k: list(v) for k, v in self.assignments.items()})

    def assigned_employees(self, shift_id: str) -> List[str]:
        return self.assignments.get(shift_id, [])

    def employee_shifts(self) -> Dict[str, List[str]]:
        emp_to_shifts: Dict[str, List[str]] = {}
        for sid, eids in self.assignments.items():
            for eid in eids:
                emp_to_shifts.setdefault(eid, []).append(sid)
        return emp_to_shifts
