# Constraints

Hard constraints (must hold):
- Coverage: each shift meets required headcount
- Availability: assigned employees are available
- Skills: assigned employees meet shift skill requirements
- Max shifts/week: per employee cap
- Max consecutive shifts: per employee cap
- Minimum rest hours: between any two shifts for same employee

Soft preferences (scored, not enforced):
- Fairness: distribute total shifts evenly
- Shift preferences: employees prefer certain shift tags or times (optional)
- Stability: minimize last-minute changes (optional; via baseline schedule)

See `src/shift_scheduling_agent/constraints.py` and `scoring.py`.
