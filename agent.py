from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
import datetime as dt

from .config import ScheduleConfig
from .scheduler import SimpleGreedyScheduler, ScheduleResult
from .llm_interface import LLMClient, AgentExplainer


@dataclass
class ShiftSchedulingAgent:
    config: ScheduleConfig

    def __post_init__(self):
        self.scheduler = SimpleGreedyScheduler(self.config)
        self.llm_client = LLMClient()
        self.explainer = AgentExplainer(self.config, self.llm_client)

    def draft_schedule(
        self,
        start_date: Optional[dt.date] = None,
        days: int = 7,
    ) -> ScheduleResult:
        if start_date is None:
            today = dt.date.today()
            start_date = today - dt.timedelta(days=today.weekday())
        return self.scheduler.generate_week(start_date=start_date, days=days)

    def explain_schedule(
        self,
        start_date: Optional[dt.date] = None,
        days: int = 7,
    ) -> str:
        result = self.draft_schedule(start_date=start_date, days=days)
        return self.explainer.explain(result)
