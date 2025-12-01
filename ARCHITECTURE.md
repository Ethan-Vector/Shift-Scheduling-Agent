# Architecture

This project is intentionally simple but structured in a way that makes it easy
to extend into a serious, production-ready system.

At a high level:

- **Configuration layer** (`config.py`)
- **Scheduling core** (`scheduler.py`)
- **LLM orchestration** (`llm_interface.py`)
- **Agent facade** (`agent.py`)
- **CLI interface** (`cli.py`)

---

## Configuration layer

- Defines `StaffMember`, `ShiftDefinition`, and `RuleSet`.
- Loads data from YAML files into a `ScheduleConfig` object.
- Computes shift durations in hours.

You can extend this layer with:

- Additional fields (e.g. departments, seniority, union group).
- Derived properties (e.g. week numbers, weekend flags).
- Validation of input data.

---

## Scheduling core

`SimpleGreedyScheduler` takes a `ScheduleConfig` and generates a weekly
schedule:

- Assigns staff to each shift for each day.
- Tries to respect:
  - maximum hours per week (per person + global cap),
  - minimum rest hours between shifts,
  - required skills per shift.
- Chooses the candidate with **lowest current hours** to promote fairness.

The output is a `ScheduleResult`:

- `assignments`: list of (staff, day, shift).
- `violations`: any "we couldn't fill this" messages.

This is the place where you would:

- Swap the greedy logic with a constraint solver.
- Add more constraints (weekends, fairness, seniority).
- Optimise for specific objectives (e.g. minimize variance of hours).

---

## LLM orchestration

`LLMClient` is a simple abstraction with a `complete(prompt: str) -> str`
method.

- Out-of-the-box, it returns a **dummy explanation** if no API key is set.
- In real usage, you plug in your favorite provider.

`AgentExplainer`:

- Builds a structured prompt describing:
  - rules,
  - staff,
  - assignments,
  - violations.
- Asks the LLM to:
  - explain how the schedule respects rules,
  - highlight fairness/duty load issues,
  - suggest improvements.

This makes the schedule **auditable** and easier to discuss with humans.

---

## Agent facade

`ShiftSchedulingAgent` is a convenience wrapper:

- Owns:
  - `SimpleGreedyScheduler`
  - `LLMClient`
  - `AgentExplainer`
- Provides:
  - `draft_schedule(start_date, days)` -> `ScheduleResult`
  - `explain_schedule(start_date, days)` -> `str`

This is what you would import from an API server, web UI, or notebook.

---

## CLI interface

`src/cli.py` exposes a minimal command line:

- `draft` → prints a weekly schedule.
- `explain` → prints an LLM-generated explanation.

Because it uses the same agent class, the CLI is a thin layer on top
of the architecture you would use in a web app or internal tool.

---

## Next steps

If you want to evolve this into a real product:

1. Replace the greedy scheduler with OR-Tools or another solver.
2. Add persistent storage (database) for:
   - historical schedules,
   - user feedback,
   - rule versions.
3. Build a web UI (e.g. FastAPI + React / Streamlit) and expose:
   - a calendar view,
   - a chat with the agent,
   - audit logs.
4. Introduce role-based access:
   - admins (change rules),
   - supervisors (approve schedules),
   - staff (view & request changes).
