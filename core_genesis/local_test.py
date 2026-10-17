"""Run deterministic unit checks with network disabled. No demo/model responses."""
import json
from pathlib import Path
import re
import socket
import subprocess
import sys
import time
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent


def run_checks():
    start = time.perf_counter()
    result = subprocess.run([sys.executable, "-m", "core_genesis.local_test", "--worker"], cwd=str(ROOT), capture_output=True, text=True, timeout=30)
    output = result.stdout + result.stderr
    count = re.search(r"Ran (\d+) tests?", output)
    return {"mode": "local", "status": "complete" if result.returncode == 0 else "error", "passed": result.returncode == 0,
            "test_count": int(count.group(1)) if count else None, "external_api_calls": 0,
            "latency_s": round(time.perf_counter() - start, 3), "output": output,
            "note": "Deterministic unit checks; network disabled. Unit-test doubles never serve as live or recorded benchmark evidence."}


def blocked(*args, **kwargs):
    raise RuntimeError("LOCAL TEST forbids all network access")


if __name__ == "__main__":
    if "--worker" in sys.argv:
        with patch.object(socket, "socket", blocked), patch.object(socket, "create_connection", blocked):
            suite = unittest.defaultTestLoader.discover(str(ROOT / "tests"))
            result = unittest.TextTestRunner(verbosity=2).run(suite)
            sys.exit(0 if result.wasSuccessful() else 1)
    else:
        report = run_checks()
        print(json.dumps(report, indent=2))
        sys.exit(0 if report["passed"] else 1)
