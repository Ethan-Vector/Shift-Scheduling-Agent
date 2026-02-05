# Shift-Scheduling-Agent

A **production-friendly** reference repo for building a *shift scheduling agent*: given staff, shifts, availability, skills, and policies, it generates a schedule, validates it, scores it, and explains trade-offs.

This repo is intentionally **offline-first**:
- Works with **standard Python** (no hosted LLM required).
- Includes a deterministic **MockLLM** for "agent-like" chat + tool calls.
- Provides a solver with **hard constraints** + **soft preferences** (scoring).

## Quickstart

### 1) Setup
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

### 2) Generate a schedule (JSON config)
```bash
shift-agent generate --config configs/sample_week.json --out outputs/schedule.json
```

### 3) Validate and score
```bash
shift-agent validate --config configs/sample_week.json --schedule outputs/schedule.json
shift-agent score --config configs/sample_week.json --schedule outputs/schedule.json
```

### 4) Chat mode (offline "agent")
```bash
shift-agent chat --config configs/sample_week.json
```

## What you get

- **Agent loop**: interprets an intent → calls tools → checks constraints → iterates within budgets
- **Solver**: greedy construction + local improvements (swap-based) + backtracking fallback for tiny instances
- **Guardrails**: time/budget caps, deterministic mode, file sandbox (`workspace/`)
- **Evals**: smoke dataset + harness
- **CI**: ruff + pytest + smoke evals
- **Docker**: reproducible runs

## Project layout

- `src/shift_scheduling_agent/` — library code
- `configs/` — example inputs
- `outputs/` — generated artifacts (gitignored)
- `evals/` — smoke datasets + harness
- `tests/` — unit + smoke
- `.github/workflows/ci.yml` — CI pipeline
- `docs/` — architecture + constraints

## Notes on realism

Shift scheduling is a full optimization domain (CP-SAT/ILP/Metaheuristics). This repo gives you:
- a clean *engineering* baseline,
- correctness-first validation,
- extendable constraints,
- a pragmatic solver that works well for small/medium rosters.

If you need optimal schedules at scale, swap the solver with OR-Tools CP-SAT and keep the rest.

## License
MIT — see `LICENSE`.
