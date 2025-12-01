# Roadmap (suggested)

This file gives ideas for how an AI engineer could turn this repo into a
strong, real-world project.

---

## Phase 1 — Learning and prototyping

- Run the CLI on your own example data.
- Add a few staff members and custom shift patterns.
- Experiment with different rules (rest hours, max hours).

Goal: understand the architecture and where to plug improvements.

---

## Phase 2 — Stronger scheduling engine

- Introduce OR-Tools (or similar):
  - model shifts as variables,
  - apply hard constraints (hours, rest, skills),
  - optionally add soft constraints (preferences).
- Keep the `ScheduleResult` interface the same, so the rest of
  the code doesn't need to change.

Goal: robust scheduling that scales to dozens/hundreds of staff.

---

## Phase 3 — Better explanations and feedback

- Improve the `AgentExplainer` prompt.
- Add a way to feed **human corrections** back into:
  - rule updates (e.g. "Rossi no longer does nights"),
  - preference models (e.g. avoid consecutive weekends).

Goal: the system appears to "learn" from the team.

---

## Phase 4 — Web UI and API

- Wrap the agent into a FastAPI (or Flask) service.
- Add endpoints:
  - `POST /schedule/draft`
  - `POST /schedule/explain`
- Build a small front-end with:
  - a calendar,
  - a chat box for questions,
  - buttons to accept/override suggestions.

Goal: make the agent usable by non-technical users.

---

## Phase 5 — Productionization

- Authentication and role-based access.
- Logging, monitoring, and alerting.
- Evaluation:
  - number of violations per schedule,
  - fairness metrics,
  - user satisfaction surveys.

Goal: a maintainable, auditable scheduling assistant
that can be safely deployed in real environments.
