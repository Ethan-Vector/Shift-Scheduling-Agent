# Agentic Shift Scheduling Agent

This repository contains a **hybrid agent + constraint solver** that helps
design, test, and iteratively improve staff shift schedules (e.g. for clinics,
departments, or teams) while keeping a human in the loop.

The goal is to give an AI engineer a **solid starting point** for a serious
project:

- A clear architecture (LLM orchestrator + constraint-based scheduler).
- Configurable rules and staff data (YAML).
- A CLI agent that you can talk to from the terminal.
- Extension points for plugging in OR-Tools or other solvers.

> ⚠️ This is a reference implementation and learning project.
> Before using it in production or in sensitive domains (e.g. hospitals),
> you **must** review, extend, and validate the behavior carefully.

---

## Features

- Define **staff**, **shifts**, and **rules** in simple YAML files.
- Generate **draft schedules** while respecting:
  - Max hours per week per person
  - Min rest time between shifts
  - Simple skill requirements per shift
- Use an **LLM orchestrator** to:
  - Turn natural language requests into configuration changes.
  - Explain why a schedule looks the way it does.
  - Propose alternatives when constraints are impossible.
- Keep a **feedback loop**:
  - Apply human corrections to the schedule.
  - Capture them as new or updated rules.

The out-of-the-box solver is intentionally simple (pure Python) so you can run
it everywhere. For real-world loads, you’ll probably want to plug in a
stronger constraint solver (e.g. OR-Tools). The repository is structured to
make that easy.

---

## Repository structure

```text
.
├── README.md
├── requirements.txt
├── src
│   ├── cli.py
│   └── shift_agent
│       ├── __init__.py
│       ├── agent.py
│       ├── config.py
│       ├── llm_interface.py
│       └── scheduler.py
├── data
│   ├── example_staff.yaml
│   ├── example_shifts.yaml
│   └── example_rules.yaml
├── docs
│   ├── ARCHITECTURE.md
│   ├── ROADMAP.md
│   └── SCENARIOS.md
└── tests
    └── test_scheduler.py
```

---

## Quickstart

### 1. Install

Python 3.10+ is recommended.

```bash
git clone YOUR_REPO_URL_HERE
cd shift_scheduling_agent

python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

### 2. Run a sample schedule

```bash
python -m src.cli \
  --staff data/example_staff.yaml \
  --shifts data/example_shifts.yaml \
  --rules data/example_rules.yaml \
  draft
```

This will print a simple draft schedule to the console.

### 3. Enable the LLM agent (optional)

Set your environment variables:

```bash
export OPENAI_API_KEY="sk-..."        # or other provider
export OPENAI_MODEL="gpt-4.1-mini"    # or equivalent model name
```

Then you can ask the agent for an explanation:

```bash
python -m src.cli explain \
  --staff data/example_staff.yaml \
  --shifts data/example_shifts.yaml \
  --rules data/example_rules.yaml
```

The CLI will:

1. Run the scheduler.
2. Send the schedule + rules to the LLM.
3. Print back a human-readable explanation.

> Note: `llm_interface.py` is written to be provider-agnostic.
> You can integrate OpenAI, Anthropic, or any other provider you prefer
> by implementing the `LLMClient` interface.

---

## How to extend this project

Some ideas:

- Replace the simple greedy solver with:
  - OR-Tools CP-SAT
  - A MILP solver (e.g. PuLP)
- Add richer constraints:
  - Fair distribution of nights/weekends
  - Seniority rules
  - Multi-site coverage
- Build a small web UI:
  - Visual calendar
  - Drag & drop adjustments
  - Agent chat side panel

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) and
[`docs/ROADMAP.md`](docs/ROADMAP.md) for more details.

---

## Disclaimer

This repository is for **educational and prototyping purposes**.
For critical environments (like hospitals), you must:

- Validate schedules with domain experts.
- Add proper testing, monitoring, and auditing.
- Ensure compliance with local laws and contracts.

Use at your own risk.
