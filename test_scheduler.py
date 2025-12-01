import datetime as dt

from shift_agent.config import ScheduleConfig
from shift_agent.scheduler import SimpleGreedyScheduler


def test_basic_schedule_runs():
    cfg = ScheduleConfig.from_files(
        staff_path="data/example_staff.yaml",
        shifts_path="data/example_shifts.yaml",
        rules_path="data/example_rules.yaml",
    )
    scheduler = SimpleGreedyScheduler(cfg)
    start = dt.date.today()
    result = scheduler.generate_week(start_date=start, days=3)
    assert result.assignments  # at least some assignments
