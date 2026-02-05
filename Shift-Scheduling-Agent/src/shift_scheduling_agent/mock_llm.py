from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, Optional


@dataclass(frozen=True)
class ToolCall:
    name: str
    args: Dict


class MockLLM:
    """Deterministic intent router.

    This is *not* a real model. It maps common chat requests into tool calls so you can
    demo an "agent loop" offline and keep CI deterministic.
    """

    def route(self, user_text: str) -> Optional[ToolCall]:
        t = user_text.strip().lower()

        if any(k in t for k in ["generate", "build", "create schedule", "make schedule", "schedula"]):
            return ToolCall(name="schedule_generate", args={})

        if "validate" in t or "check" in t or "violations" in t:
            return ToolCall(name="schedule_validate", args={})

        if "score" in t or "fair" in t or "fairness" in t:
            return ToolCall(name="schedule_score", args={})

        if "explain" in t or "why" in t or "show" in t:
            return ToolCall(name="schedule_explain", args={})

        return None
