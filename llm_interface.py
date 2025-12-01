from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional
import os
import textwrap

from .scheduler import ScheduleResult
from .config import ScheduleConfig


@dataclass
class LLMClient:
    """Thin wrapper around an LLM provider.

    This is intentionally abstract. To actually call a provider (OpenAI,
    Anthropic, etc.) you should implement the `complete` method using
    the SDK of your choice.

    Example sketch for OpenAI:

        from openai import OpenAI
        client = OpenAI()

        def complete(self, prompt: str) -> str:
            resp = client.chat.completions.create(
                model=os.environ.get("OPENAI_MODEL", "gpt-4.1-mini"),
                messages=[{"role": "user", "content": prompt}],
            )
            return resp.choices[0].message.content

    For this repo, we default to a dummy implementation if no API key is set.
    """

    def complete(self, prompt: str) -> str:
        if not os.environ.get("OPENAI_API_KEY"):
            return self._dummy_response(prompt)
        # Placeholder: implement your provider-specific call here.
        return self._dummy_response(prompt)

    def _dummy_response(self, prompt: str) -> str:
        return (
            "LLM integration is not configured.

"
            "Prompt preview (truncated):
"
            + textwrap.shorten(prompt, width=400, placeholder=" ...")
        )


@dataclass
class AgentExplainer:
    config: ScheduleConfig
    llm: LLMClient

    def build_explanation_prompt(self, result: ScheduleResult) -> str:
        lines: List[str] = []

        lines.append("You are an expert in workforce shift scheduling.")
        lines.append("Explain the following weekly schedule in clear, concise terms.")
        lines.append("")
        lines.append("Rules:")
        lines.append(f"- Min rest hours: {self.config.rules.min_rest_hours}")
        lines.append(f"- Max hours per week (global): {self.config.rules.max_hours_per_week}")
        lines.append("")
        lines.append("Staff:")
        for m in self.config.staff:
            skills = ", ".join(m.skills) if m.skills else "none"
            lines.append(f"- {m.id} ({m.name}), skills: {skills}, max_hours/week: {m.max_hours_per_week}")
        lines.append("")
        lines.append("Assignments:")
        for a in result.assignments:
            shift = self.config.shifts[a.shift_id]
            lines.append(
                f"- {a.day.isoformat()} | {shift.label} ({shift.start}-{shift.end}) -> {a.staff_id}"
            )
        if result.violations:
            lines.append("")
            lines.append("Violations or warnings detected:")
            for v in result.violations:
                lines.append(f"- {v}")

        lines.append("")
        lines.append(
            "Explain:
"
            "1) How the rules are being respected.
"
            "2) Where there might be fairness or workload concerns.
"
            "3) Suggestions for improving this schedule while still respecting constraints."
        )

        return "\n".join(lines)

    def explain(self, result: ScheduleResult) -> str:
        prompt = self.build_explanation_prompt(result)
        return self.llm.complete(prompt)
