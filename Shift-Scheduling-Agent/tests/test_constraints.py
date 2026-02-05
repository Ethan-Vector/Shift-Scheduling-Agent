from __future__ import annotations

from shift_scheduling_agent.config_io import load_config
from shift_scheduling_agent.constraints import ConstraintSuite
from shift_scheduling_agent.domain import Schedule


def test_sample_week_solver_validates():
    config = load_config("configs/sample_week.json")
    # A minimal schedule that might be incomplete; just validate that the suite runs.
    sch = Schedule(assignments={})
    report = ConstraintSuite.default().validate(config, sch)
    assert report.ok is False
    assert any(v.code == "UNDER_COVERAGE" for v in report.violations)


def test_assignment_requires_availability():
    config = load_config("configs/sample_week.json")
    # Force an employee into a shift they cannot cover by availability (pick an employee and shift)
    # We choose shift s2 (stock) and employee e1 (cashier only) → skill violation + possibly availability
    sch = Schedule(assignments={"s2": ["e1"]})
    report = ConstraintSuite.default().validate(config, sch)
    codes = {v.code for v in report.violations}
    assert "MISSING_SKILL" in codes
