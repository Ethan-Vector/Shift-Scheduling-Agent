# Architecture

## Core pipeline
1. Parse config → domain objects
2. Generate schedule (solver)
3. Validate hard constraints
4. Score soft preferences
5. Explain trade-offs

## Modules
- `config_io.py`: read/validate JSON configs and schedules
- `domain.py`: dataclasses for employees/shifts/schedule
- `constraints.py`: hard constraints + validation report
- `scoring.py`: soft constraints & fairness scoring
- `solver.py`: constructive + improvement heuristics
- `agent.py`: offline "agent loop" that calls tools
- `tools.py`: tool registry used by the agent and the CLI

## Design goals
- Determinism in CI (fixed random seed)
- Explicit budgets (seconds / iterations)
- Pure constraint checks (no side effects)

