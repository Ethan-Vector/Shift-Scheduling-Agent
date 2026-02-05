# Adding constraints

## Step-by-step
1. Implement a pure function:
   - input: `Config`, `Schedule`
   - output: list of `Violation`

2. Register it:
   - Add to `ConstraintSuite.default()`.

3. Tests:
   - Add a unit test in `tests/test_constraints.py`.

4. Evals:
   - Add a case to `evals/datasets/smoke.jsonl`.

## Example (outline)
- Add `no_night_then_morning(config, schedule)`
- It flags assignments where an employee works a late shift then an early shift.

