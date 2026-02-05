from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

from ..config_io import load_config
from ..constraints import ConstraintSuite
from ..domain import Schedule
from ..solver import solve


DATASET = Path("evals/datasets/smoke.jsonl")


def run_case(case: Dict) -> Dict:
    config_path = case["config_path"]
    expect_ok = bool(case.get("expect_ok", True))

    config = load_config(config_path)
    result = solve(config)
    report = ConstraintSuite.default().validate(config, result.schedule)

    return {
        "case_id": case.get("id", config_path),
        "solver_ok": result.ok,
        "valid_ok": report.ok,
        "expect_ok": expect_ok,
        "violations": [v.__dict__ for v in report.violations[:20]],
    }


def main() -> None:
    if not DATASET.exists():
        raise SystemExit(f"Missing dataset: {DATASET}")

    cases = [json.loads(line) for line in DATASET.read_text(encoding="utf-8").splitlines() if line.strip()]
    results = [run_case(c) for c in cases]

    failed: List[Dict] = []
    for r in results:
        if r["expect_ok"] and not r["valid_ok"]:
            failed.append(r)
        if (not r["expect_ok"]) and r["valid_ok"]:
            failed.append(r)

    if failed:
        print("FAILED cases:")
        print(json.dumps(failed, indent=2))
        raise SystemExit(1)

    print(f"OK — {len(results)} smoke case(s).")


if __name__ == "__main__":
    main()
