# Contributing

## Setup
```bash
pip install -e ".[dev]"
```

## Quality gates
- `ruff check .`
- `pytest`
- `python -m shift_scheduling_agent.evals.harness`

## Style
- Prefer small functions with explicit types
- Keep constraints pure (no IO)
- Add tests for each new constraint

