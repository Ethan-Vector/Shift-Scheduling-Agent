# INSTRUCTIONS (How to use and extend)

## 1) Inputs

The primary input format is JSON (no external dependencies). See:
- `configs/sample_week.json`

Key parts:
- `employees`: id, name, skills, availability windows
- `shifts`: id, start/end ISO timestamps, required skills, required headcount
- `policies`: max shifts/week, max consecutive shifts, min rest hours, etc.
- `preferences`: optional soft rules for scoring (fairness, preferred shifts)

## 2) Tools (the "agent" uses these)

- `schedule_generate(config) -> schedule`
- `schedule_validate(config, schedule) -> validation_report`
- `schedule_score(config, schedule) -> score_report`
- `schedule_explain(config, schedule, report) -> markdown`

You can call them from Python or via CLI.

## 3) Extending constraints

Constraints live in `src/shift_scheduling_agent/constraints.py`.

Pattern:
1. Add a function that returns violations for a schedule.
2. Register it inside `ConstraintSuite.default()`.
3. Add unit tests in `tests/test_constraints.py`.
4. Add at least one smoke eval case in `evals/datasets/`.

See `docs/adding_constraints.md`.

## 4) Solver tuning knobs

- `solver.max_seconds`: total runtime budget
- `solver.max_iterations`: number of improvement rounds
- `solver.random_seed`: deterministic reproducibility
- `solver.backtracking_limit`: for tiny instances only

Configured in `configs/*.json` under `"solver"`.

## 5) Typical workflow

1. Generate schedule
2. Validate (hard constraints)
3. Score (soft preferences)
4. Iterate: adjust config/policies/preferences
5. Lock config + add evals to prevent regressions

## 6) Safety/guardrails

This repo includes:
- file sandbox: writes only to `workspace/`
- time budget: solver stops when budget is consumed
- deterministic mode for CI + evals

