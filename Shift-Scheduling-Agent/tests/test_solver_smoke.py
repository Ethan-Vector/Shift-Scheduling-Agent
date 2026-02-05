from __future__ import annotations

from shift_scheduling_agent.config_io import load_config
from shift_scheduling_agent.constraints import ConstraintSuite
from shift_scheduling_agent.solver import solve


def test_solver_produces_valid_schedule_for_sample_week():
    config = load_config("configs/sample_week.json")
    result = solve(config)
    report = ConstraintSuite.default().validate(config, result.schedule)
    assert report.ok, f"violations: {[v.code for v in report.violations]}"
