# Example scenarios

Some concrete ways this agent can be used.

---

## 1. Hospital department weekly planning

- Input:
  - staff list with roles (doctors, nurses),
  - three standard shifts (day, evening, night),
  - rules for max hours and rest.
- Process:
  - run `draft` to propose a weekly schedule,
  - run `explain` to get a textual explanation,
  - manually adjust any assignments that are suboptimal.
- Benefit:
  - start with a good baseline instead of building from scratch.

---

## 2. Emergency change at short notice

- A staff member calls in sick.
- You remove them temporarily from the staff list or reduce
  their max hours to 0 for the week.
- Re-run the scheduler for the affected days.
- Use the LLM explanation to understand how coverage is maintained.

---

## 3. "What if" experiments

- Increase or decrease `max_hours_per_week`.
- Try different `min_rest_hours`.
- Add or remove skills from staff.
- Re-run the schedule and compare outcomes.

This is useful for management discussions about policy changes.

---

## 4. Teaching / internal workshop

Use this repo to:

- Show non-technical stakeholders how AI + optimization can help.
- Demonstrate the difference between:
  - a naive, greedy approach,
  - and a more advanced solver.
- Discuss fairness, work-life balance, and policy design.

Because the code is relatively small and documented, it is ideal for
live coding or interactive sessions.
