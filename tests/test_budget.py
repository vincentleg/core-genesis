import datetime as dt
from decimal import Decimal
import fcntl
import json
from pathlib import Path
import tempfile
import unittest

from core_genesis.budget import BudgetError, RequestBudget, ROOT
from core_genesis.crusoe import DEFAULT_MODEL, CrusoeError


class IsolatedTransport:
    """Unit-test transport; never imported by production code or served as evidence."""
    model = DEFAULT_MODEL
    max_retries = 0
    last_status = 200

    def __init__(self, fail_once=False, missing_usage=False):
        self.calls = 0
        self.fail_once = fail_once
        self.missing_usage = missing_usage

    def chat(self, messages, **kwargs):
        self.calls += 1
        if self.fail_once and self.calls == 1:
            self.last_status = 503
            raise CrusoeError(503, "unit test only")
        self.last_status = 200
        return {"model": self.model, "usage": {} if self.missing_usage else {"prompt_tokens": 5, "completion_tokens": 5, "total_tokens": 10},
                "choices": [{"message": {"content": "{}"}}]}


class BudgetTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.price = self.root / "pricing.json"
        pricing = json.loads((ROOT / "pricing.json").read_text())
        now = dt.datetime.now(dt.timezone.utc)
        pricing.update(verified_at=(now - dt.timedelta(minutes=1)).isoformat(), expires_at=(now + dt.timedelta(hours=1)).isoformat())
        self.price.write_text(json.dumps(pricing))
        self.budget = RequestBudget(self.root / "budget", self.price, self.root / "history")
        self.client = IsolatedTransport()

    def tearDown(self):
        self.temp.cleanup()

    def ask(self, client=None, run="unit-test", cycle=0):
        return self.budget.chat(run, cycle, "UnitTest", [{"role": "user", "content": "unit test"}], 20, client or self.client)

    def test_six_physical_attempts_then_no_transport(self):
        for _ in range(6):
            self.ask()
        with self.assertRaises(BudgetError):
            self.ask()
        self.assertEqual(self.client.calls, 6)
        self.assertEqual(self.budget.run_snapshot("unit-test")["physical_requests"], 6)

    def test_retries_consume_quota_and_keep_unknown_cost_reserve(self):
        client = IsolatedTransport(fail_once=True)
        self.ask(client)
        entries = self.budget.run_snapshot("unit-test")["entries"]
        self.assertEqual(len(entries), 2)
        self.assertEqual(entries[0]["status"], "unknown_usage")
        self.assertNotIn("charge_usd", entries[0])
        self.assertGreater(Decimal(entries[0]["reserved_usd"]), Decimal(entries[1]["charge_usd"]))
        for _ in range(4):
            self.ask(client)
        with self.assertRaises(BudgetError):
            self.ask(client)
        self.assertEqual(client.calls, 6)

    def test_maximum_two_cycles(self):
        self.ask(cycle=0)
        self.ask(cycle=1)
        with self.assertRaises(BudgetError):
            self.ask(cycle=2)
        self.assertEqual(self.client.calls, 2)

    def test_missing_expired_and_unknown_pricing_fail_before_transport(self):
        good = self.price.read_text()
        for mutation in ("missing", "expired", "model", "negative", "nan"):
            self.price.write_text(good)
            if mutation == "missing":
                self.price.unlink()
            else:
                data = json.loads(good)
                if mutation == "expired":
                    data["expires_at"] = "2020-01-01T00:00:00+00:00"
                if mutation == "model":
                    data["model"] = "unknown-model"
                if mutation in ("negative", "nan"):
                    data["input_usd_per_million"] = "-1" if mutation == "negative" else "NaN"
                self.price.write_text(json.dumps(data))
            with self.assertRaises(BudgetError):
                self.ask()
        self.assertEqual(self.client.calls, 0)

    def test_cap_reserves_before_transport_and_persists(self):
        self.budget.snapshot()
        with self.budget.ledger() as state:
            state["legacy"]["total_allowance_usd"] = "1.9999999999"
        with self.assertRaises(BudgetError):
            self.ask()
        self.assertEqual(self.client.calls, 0)
        restored = RequestBudget(self.root / "budget", self.price, self.root / "history")
        self.assertEqual(restored.snapshot()["committed_estimate_and_reserves_usd"], "1.9999999999")

    def test_unknown_usage_retains_reserve_and_stops(self):
        client = IsolatedTransport(missing_usage=True)
        with self.assertRaises(BudgetError):
            self.ask(client)
        self.assertEqual(client.calls, 1)
        entry = self.budget.run_snapshot("unit-test")["entries"][0]
        self.assertEqual(entry["status"], "unknown_usage")
        self.assertNotIn("charge_usd", entry)

    def test_process_wide_single_request_lock(self):
        with (self.budget.directory / "request.lock").open("a+") as handle:
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
            with self.assertRaises(BudgetError):
                self.ask()
            fcntl.flock(handle, fcntl.LOCK_UN)
        self.assertEqual(self.client.calls, 0)

    def test_corrupt_ledger_and_oversized_input_fail_closed(self):
        self.budget.path.write_text("invalid json")
        with self.assertRaises(BudgetError):
            self.ask()
        with self.assertRaises(BudgetError):
            self.budget.chat("unit-test", 0, "UnitTest", [{"role": "user", "content": "x" * 25000}], 20, self.client)
        self.assertEqual(self.client.calls, 0)

    def test_reading_budget_never_calls_transport(self):
        for _ in range(5):
            self.budget.snapshot()
        self.assertEqual(self.client.calls, 0)

    def test_negative_ledger_amounts_fail_closed(self):
        self.budget.snapshot()
        state = json.loads(self.budget.path.read_text())
        state["legacy"]["total_allowance_usd"] = "-1"
        self.budget.path.write_text(json.dumps(state))
        with self.assertRaises(BudgetError):
            self.ask()
        self.assertEqual(self.client.calls, 0)
