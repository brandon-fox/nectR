"""Cross-platform telemetry artifact and test verifier for persona-simulation."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "lib"))
import skill_common


def validate_experiment_outputs(repo_root: Path) -> int:
    """Validate any generated JSON or CSV telemetry artifacts in experiments/."""
    exp_dir = repo_root / "experiments"
    if not exp_dir.is_dir():
        print("[PASS] experiments/ directory not present; skipping artifact validation")
        return 0

    checked = 0
    for json_file in exp_dir.rglob("*.json"):
        json.loads(json_file.read_text(encoding="utf-8"))
        checked += 1

    for csv_file in exp_dir.rglob("*.csv"):
        with csv_file.open("r", encoding="utf-8", newline="") as fh:
            reader = csv.reader(fh)
            rows = list(reader)
            if not rows:
                print(f"[FAIL] Empty telemetry CSV: {csv_file.relative_to(repo_root)}", file=sys.stderr)
                return 1
        checked += 1

    print(f"[PASS] Validated {checked} telemetry artifact(s) in experiments/")
    return 0


def main() -> int:
    repo_root = skill_common.find_repo_root()
    rc = validate_experiment_outputs(repo_root)
    if rc != 0:
        return rc

    persona_tests = [
        p
        for p in ("tests/test_personas.py", "tests/test_invariants.py")
        if (repo_root / p).is_file()
    ]
    return skill_common.run_pytest(persona_tests or None, repo_root)


if __name__ == "__main__":
    raise SystemExit(main())
