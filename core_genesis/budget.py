"""Persistent, process-safe, fail-closed request budgeting around the existing client.

All money is Decimal USD. Unknown/failed requests retain their preflight reserve.
Physical attempts (including retries), not just successful calls, consume the quota.
"""
import contextlib
import datetime as dt
from decimal import Decimal
import fcntl
import json
from pathlib import Path
import time
import urllib.error
import uuid

from .crusoe import CrusoeClient, CrusoeError, DEFAULT_MODEL

ROOT = Path(__file__).resolve().parent.parent
CAP = Decimal("2.00")
MAX_REQUESTS = 6
MAX_CYCLES = 2
MAX_OUTPUT = 1800
MAX_INPUT_BYTES = 24000


class BudgetError(RuntimeError):
    pass


def dollars(value):
    return str(Decimal(value).quantize(Decimal("0.0000000001")))


def price_tokens(pricing, prompt_tokens, completion_tokens):
    return (Decimal(prompt_tokens) * Decimal(pricing["input_usd_per_million"]) +
            Decimal(completion_tokens) * Decimal(pricing["output_usd_per_million"])) / 1000000


class RequestBudget:
    def __init__(self, directory=None, pricing_path=None, history=None):
        self.directory = Path(directory or ROOT / "budget")
        self.directory.mkdir(parents=True, exist_ok=True)
        self.path = self.directory / "ledger.json"
        self.pricing_path = Path(pricing_path or ROOT / "pricing.json")
        self.history = Path(history or ROOT / "experiments")

    def pricing(self):
        try:
            price = json.loads(self.pricing_path.read_text())
            now = dt.datetime.now(dt.timezone.utc)
            verified = dt.datetime.fromisoformat(price["verified_at"])
            expiry = dt.datetime.fromisoformat(price["expires_at"])
            if price["model"] != DEFAULT_MODEL or price["source"] != "https://www.crusoe.ai/cloud/pricing":
                raise ValueError()
            if not verified <= now < expiry or expiry - verified > dt.timedelta(hours=25):
                raise ValueError()
            if any(not Decimal(price[k]).is_finite() or Decimal(price[k]) <= 0 for k in ("input_usd_per_million", "output_usd_per_million")):
                raise ValueError()
            return price
        except (OSError, ValueError, KeyError, TypeError, ArithmeticError):
            raise BudgetError("Live inference locked: verified pricing is missing, invalid, or expired") from None

    def _bootstrap(self, price):
        """Import real pre-budget usage; retain pessimistic reserves for hidden retries.

        Successful legacy attempts may each have retried once with the same prompt.
        Unknown attempts use the model's full 1M (1,048,576) context plus 1200 output.
        The pre-existing smoke invocation reserves six such attempts (old retry cap 5).
        These are allowances, never claimed as measured consumption or billed costs.
        """
        reported = Decimal(0)
        retry_reserve = Decimal(0)
        unknown_attempts = 6  # User-confirmed pre-existing smoke, max 5 retries.
        tokens = calls = 0
        imported = []
        for file in sorted(self.history.glob("*.json")):
            state = json.loads(file.read_text())
            if state.get("budget_policy"):
                # Losing a ledger must not silently reset a project's cap.
                raise BudgetError("Budget ledger missing for previously budgeted runs; restore the ledger")
            events = [e for e in state.get("events", []) if e.get("usage")]
            for event in events:
                usage = event["usage"]
                prompt, output = usage.get("prompt_tokens"), usage.get("completion_tokens")
                if type(prompt) is not int or type(output) is not int or min(prompt, output) < 0 or event.get("model") != DEFAULT_MODEL:
                    raise BudgetError("Historical usage or model cannot be priced; reconcile history before live inference")
                reported += price_tokens(price, prompt, output)
                retry_reserve += price_tokens(price, prompt, 1200)
                tokens += usage.get("total_tokens", prompt + output)
                calls += 1
            missing = max(0, state.get("inference_calls", len(events)) - len(events))
            unknown_attempts += 2 * missing  # Initial attempt and one possible retry.
            if state.get("status") in ("running", "interrupted"):
                unknown_attempts += 2
            imported.append(file.stem)
        unknown_reserve = unknown_attempts * price_tokens(price, 1048576, 1200)
        return {"schema": 1, "cap_usd": str(CAP), "pricing": price,
                "legacy": {"records": imported, "reported_calls": calls, "reported_tokens": tokens,
                           "estimated_reported_cost_usd": dollars(reported), "possible_retry_reserve_usd": dollars(retry_reserve),
                           "unknown_attempts_reserved": unknown_attempts, "unknown_usage_reserve_usd": dollars(unknown_reserve),
                           "total_allowance_usd": dollars(reported + retry_reserve + unknown_reserve),
                           "note": "Conservative allowances, not actual bills. Unknown attempts reserve full 1M model context. Includes existing smoke test and interrupted/failed legacy requests."},
                "entries": []}

    @contextlib.contextmanager
    def ledger(self):
        with (self.directory / "ledger.lock").open("a+") as handle:
            fcntl.flock(handle, fcntl.LOCK_EX)
            try:
                price = self.pricing()
                if self.path.exists():
                    state = json.loads(self.path.read_text())
                    if state.get("schema") != 1 or state.get("cap_usd") != str(CAP) or not isinstance(state.get("entries"), list):
                        raise BudgetError("Budget ledger invalid; restore it before live inference")
                    amounts = [state["legacy"]["total_allowance_usd"]]
                    for entry in state["entries"]:
                        amounts.append(entry["reserved_usd"])
                        if "charge_usd" in entry:
                            amounts.append(entry["charge_usd"])
                    if any(not Decimal(value).is_finite() or Decimal(value) < 0 for value in amounts):
                        raise BudgetError("Budget ledger contains invalid monetary values")
                else:
                    state = self._bootstrap(price)
                yield state
                temporary = self.path.with_suffix(".tmp")
                temporary.write_text(json.dumps(state, indent=2))
                temporary.replace(self.path)
            except (OSError, ValueError, KeyError, ArithmeticError) as exc:
                raise BudgetError("Budget state cannot be determined; live inference blocked") from exc
            finally:
                fcntl.flock(handle, fcntl.LOCK_UN)

    @staticmethod
    def committed(state):
        return Decimal(state["legacy"]["total_allowance_usd"]) + sum((Decimal(e.get("charge_usd", e["reserved_usd"])) for e in state["entries"]), Decimal(0))

    def snapshot(self):
        with self.ledger() as state:
            committed = self.committed(state)
            return {"cap_usd": str(CAP), "committed_estimate_and_reserves_usd": dollars(committed),
                    "remaining_usd": dollars(max(Decimal(0), CAP - committed)), "legacy": state["legacy"],
                    "physical_requests": len(state["entries"]), "reported_tokens": sum(e.get("usage", {}).get("total_tokens", 0) for e in state["entries"]),
                    "pricing": state["pricing"], "status": "ready" if committed < CAP else "exhausted"}

    def run_snapshot(self, run_id):
        with self.ledger() as state:
            entries = [e for e in state["entries"] if e["run_id"] == run_id]
            return {"physical_requests": len(entries), "reported_tokens": sum(e.get("usage", {}).get("total_tokens", 0) for e in entries),
                    "cost_estimate_usd": dollars(sum((Decimal(e.get("charge_usd", e["reserved_usd"])) for e in entries), Decimal(0))),
                    "entries": entries}

    def chat(self, run_id, cycle, role, messages, max_tokens, client=None):
        if type(cycle) is not int or not 0 <= cycle < MAX_CYCLES:
            raise BudgetError("At most two evolution cycles per explicit user run")
        if type(max_tokens) is not int or not 1 <= max_tokens <= MAX_OUTPUT:
            raise BudgetError("Output token limit invalid")
        input_bytes = len(json.dumps(messages, ensure_ascii=False).encode("utf-8"))
        if input_bytes > MAX_INPUT_BYTES:
            raise BudgetError("Input exceeds the strict 24KB request limit")
        # UTF-8 bytes bound byte-level tokenizer tokens; framing is over-reserved.
        input_bound = input_bytes + 1024
        with (self.directory / "request.lock").open("a+") as request_lock:
            try:
                fcntl.flock(request_lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                raise BudgetError("Another project inference request is active") from None
            try:
                client = client or CrusoeClient(max_retries=0, timeout=30)
                if client.model != DEFAULT_MODEL or client.max_retries != 0:
                    raise BudgetError("Budget requires the pinned model and disabled client retries")
                for retry in range(2):
                    price = self.pricing()
                    reserve = price_tokens(price, input_bound, max_tokens)
                    entry_id = uuid.uuid4().hex
                    with self.ledger() as state:
                        attempts = [e for e in state["entries"] if e["run_id"] == run_id and e["cycle"] == cycle]
                        if len(attempts) >= MAX_REQUESTS:
                            raise BudgetError("Six physical model requests per cycle exhausted; retries count")
                        if self.committed(state) + reserve > CAP:
                            raise BudgetError("Project-wide $2 estimated spending cap would be exceeded")
                        state["entries"].append({"id": entry_id, "run_id": run_id, "cycle": cycle, "role": role,
                            "time": time.time(), "model": DEFAULT_MODEL, "retry": retry, "input_token_bound": input_bound,
                            "max_output_tokens": max_tokens, "reserved_usd": dollars(reserve), "status": "reserved"})
                    start = time.perf_counter()
                    response = None
                    failure = None
                    try:
                        response = client.chat(messages, max_tokens=max_tokens, temperature=0, chat_template_kwargs={"enable_thinking": False})
                    except Exception as exc:
                        failure = exc
                    latency = round(time.perf_counter() - start, 3)
                    usage = response.get("usage", {}) if isinstance(response, dict) else {}
                    valid = (response is not None and response.get("model") == DEFAULT_MODEL and
                             all(type(usage.get(k)) is int and usage[k] >= 0 for k in ("prompt_tokens", "completion_tokens", "total_tokens")) and
                             usage["prompt_tokens"] <= input_bound and usage["completion_tokens"] <= max_tokens and
                             usage["total_tokens"] == usage["prompt_tokens"] + usage["completion_tokens"])
                    with self.ledger() as state:
                        entry = next(e for e in state["entries"] if e["id"] == entry_id)
                        entry.update({"latency_s": latency, "status": "complete" if valid else "unknown_usage",
                                      "http_status": client.last_status})
                        if valid:
                            entry["usage"] = usage
                            entry["charge_usd"] = dollars(price_tokens(price, usage["prompt_tokens"], usage["completion_tokens"]))
                        else:
                            entry["error"] = type(failure).__name__ if failure else "InvalidUsageOrModel"
                            # The full reserve remains charged after timeout, partial response or crash.
                    if valid:
                        return response, {"request_id": entry_id, "latency_s": latency, "usage": usage,
                                          "cost_estimate_usd": entry["charge_usd"], "http_status": client.last_status}
                    retryable = isinstance(failure, urllib.error.URLError) or isinstance(failure, CrusoeError) and failure.status in {429, 500, 502, 503, 504}
                    if retry == 0 and retryable:
                        continue
                    if failure:
                        raise failure
                    raise BudgetError("Provider usage/model cannot be priced; reserve retained and live run stopped")
            finally:
                fcntl.flock(request_lock, fcntl.LOCK_UN)
