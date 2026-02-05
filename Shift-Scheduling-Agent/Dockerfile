FROM python:3.11-slim

WORKDIR /app
COPY pyproject.toml README.md INSTRUCTIONS.md /app/
COPY src /app/src
COPY configs /app/configs
COPY evals /app/evals
COPY tests /app/tests

RUN pip install -U pip && pip install -e ".[dev]"

CMD ["shift-agent", "--help"]
