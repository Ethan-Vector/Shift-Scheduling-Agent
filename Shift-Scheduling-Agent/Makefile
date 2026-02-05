.PHONY: install lint test evals

install:
	pip install -e ".[dev]"

lint:
	ruff check .

test:
	pytest

evals:
	python -m shift_scheduling_agent.evals.harness
