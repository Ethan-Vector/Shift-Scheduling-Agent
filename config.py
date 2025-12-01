from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Optional
import datetime as dt
import yaml

# --- Data models -------------------------------------------------------------

@dataclass
class StaffMember:
    id: str
    name: str
    skills: List[str] = field(default_factory=list)
    max_hours_per_week: int = 40

@dataclass
class ShiftDefinition:
    id: str
    label: str
    start: str  # 'HH:MM'
    end: str    # 'HH:MM'
    required_skills: List[str] = field(default_factory=list)
    hours: float = 0.0

    def compute_hours(self) -> float:
        s = dt.datetime.strptime(self.start, "%H:%M")
        e = dt.datetime.strptime(self.end, "%H:%M")
        if e <= s:
            e += dt.timedelta(days=1)
        delta = e - s
        self.hours = delta.total_seconds() / 3600.0
        return self.hours

@dataclass
class RuleSet:
    min_rest_hours: int = 11
    max_hours_per_week: int = 40

# --- Configuration loading ---------------------------------------------------

@dataclass
class ScheduleConfig:
    staff: List[StaffMember]
    shifts: Dict[str, ShiftDefinition]
    rules: RuleSet

    @staticmethod
    def from_files(
        staff_path: str,
        shifts_path: str,
        rules_path: str,
    ) -> "ScheduleConfig":
        with open(staff_path, "r", encoding="utf-8") as f:
            staff_data = yaml.safe_load(f) or []
        with open(shifts_path, "r", encoding="utf-8") as f:
            shifts_data = yaml.safe_load(f) or []
        with open(rules_path, "r", encoding="utf-8") as f:
            rules_data = yaml.safe_load(f) or {}

        staff = [
            StaffMember(
                id=str(item.get("id")),
                name=item.get("name", str(item.get("id"))),
                skills=item.get("skills", []) or [],
                max_hours_per_week=item.get("max_hours_per_week", 40),
            )
            for item in staff_data
        ]

        shifts: Dict[str, ShiftDefinition] = {}
        for item in shifts_data:
            s = ShiftDefinition(
                id=str(item.get("id")),
                label=item.get("label", str(item.get("id"))),
                start=item["start"],
                end=item["end"],
                required_skills=item.get("required_skills", []) or [],
            )
            s.compute_hours()
            shifts[s.id] = s

        rules = RuleSet(
            min_rest_hours=rules_data.get("min_rest_hours", 11),
            max_hours_per_week=rules_data.get("max_hours_per_week", 40),
        )

        return ScheduleConfig(staff=staff, shifts=shifts, rules=rules)
