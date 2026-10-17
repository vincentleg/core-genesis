"""Re-run deterministic verification from a real experiment without inference."""
import argparse
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from core_genesis.benchmark import CASES
from core_genesis.engine import ROOT, promotion_gate
from core_genesis.benchmark import verify

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("record", type=Path)
    args = parser.parse_args()
    state = json.loads(args.record.read_text())
    fingerprint = hashlib.sha256((ROOT / "core_genesis/benchmark.py").read_bytes()).hexdigest()
    if state.get("suite_sha256") != fingerprint:
        sys.exit("Suite fingerprint differs; use the benchmark revision that produced this record.")
    cases = {c.id: c for c in CASES}
    checked = 0
    for run in state["runs"]:
        last_passed = False
        for attempt in run["attempts"]:
            actual = verify(cases[run["case_id"]], attempt["patch"])
            if actual != attempt["verification"]:
                sys.exit("Verification mismatch: " + run["case_id"])
            checked += 1
            last_passed = actual["passed"]
        if run["passed"] != last_passed:
            sys.exit("Recorded success does not match repair verification: " + run["case_id"])
    for decision in state.get("decisions", []):
        candidates = [strategy for strategy in state["strategies"] if strategy["version"] != state.get("baseline_version", 0)]
        def score(strategy):
            runs = [r for r in state["runs"] if r["version"] == strategy["version"] and r["split"] == "development"]
            return sum(r["passed"] for r in runs), -sum(len(r["attempts"]) for r in runs), -strategy["version"]
        if max(candidates, key=score)["version"] != decision["version"]:
            sys.exit("Development candidate selection mismatch")
        before = [r for r in state["runs"] if r["version"] == state.get("baseline_version", 0)]
        after = [r for r in state["runs"] if r["version"] == decision["version"]]
        promoted, reason = promotion_gate(before, after)
        if promoted != (decision["action"] == "promote") or reason != decision["reason"]:
            sys.exit("Promotion gate mismatch")
    print("Verified %d repair attempts and %d decisions. No inference used." % (checked, len(state.get("decisions", []))))
