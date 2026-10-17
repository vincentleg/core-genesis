import copy
import json
import tempfile
import unittest

from core_genesis.benchmark import CASES, verify
from core_genesis.engine import BASELINE, Engine, parse_json, promotion_gate, validate_strategy
from core_genesis.budget import RequestBudget


def test_engine(directory, client, fresh=False):
    return Engine(directory, client, fresh=fresh, budget=RequestBudget(directory=directory + "/.budget", history=directory))


def repair(case):
    c = case.contract
    if "timeout_ms" in case.config:
        return {"timeout_ms": c["deadline_ms"], "retries": c["max_retries"]}
    if "pool_size" in case.config:
        return {"pool_size": c["concurrent_queries"]}
    return {"health_path": c["registered_health_path"], "port": c["listening_port"]}


class VerifierTests(unittest.TestCase):
    def test_valid_repairs_and_fixture_isolation(self):
        for case in CASES:
            original = dict(case.config)
            self.assertTrue(verify(case, repair(case))["passed"])
            self.assertEqual(case.config, original)
            self.assertFalse(verify(case, dict(case.config))["passed"])

    def test_rejects_untrusted_shapes_and_types(self):
        for patch in (None, [], {}, {"shell": "echo exploit"}, {"timeout_ms": True}, {"timeout_ms": "400"}):
            self.assertFalse(verify(CASES[0], patch)["passed"])

    def test_partial_and_out_of_budget_repairs_fail(self):
        self.assertFalse(verify(CASES[0], {"timeout_ms": 300})["passed"])
        self.assertFalse(verify(CASES[1], {"pool_size": 100})["passed"])
        self.assertFalse(verify(CASES[-1], {"port": 9090})["passed"])

    def test_tool_access_controls_evidence(self):
        context = CASES[0].context(["read_logs"])
        self.assertNotIn("config", context)
        self.assertNotIn("service_contract", context)
        self.assertIn("config_schema", context)


class GateTests(unittest.TestCase):
    def setUp(self):
        self.baseline = [{"case_id": c.id, "split": c.split, "passed": False} for c in CASES]
        self.candidate = [{**r, "passed": True} for r in self.baseline]

    def test_promotes_strict_improvement(self):
        self.assertTrue(promotion_gate(self.baseline, self.candidate)[0])

    def test_rejects_tie_regression_missing_duplicate_error_and_split_tampering(self):
        self.assertFalse(promotion_gate(self.baseline, self.baseline)[0])
        before = copy.deepcopy(self.baseline)
        before[0]["passed"] = True
        after = copy.deepcopy(self.candidate)
        after[0]["passed"] = False
        self.assertFalse(promotion_gate(before, after)[0])
        self.assertFalse(promotion_gate(self.baseline, self.candidate[:-1])[0])
        self.assertFalse(promotion_gate(self.baseline, self.candidate + [self.candidate[0]])[0])
        after = copy.deepcopy(self.candidate)
        after[0]["error"] = "NetworkFailure"
        self.assertFalse(promotion_gate(self.baseline, after)[0])
        after = copy.deepcopy(self.candidate)
        after[0]["split"] = "held_out"
        self.assertFalse(promotion_gate(self.baseline, after)[0])

    def test_development_only_improvement_rejected(self):
        after = [{**r, "passed": r["split"] == "development"} for r in self.baseline]
        self.assertFalse(promotion_gate(self.baseline, after)[0])


class StrategyTests(unittest.TestCase):
    def test_contract_first_without_logs_is_a_valid_tool_mutation(self):
        strategy = validate_strategy({**BASELINE, "tools": ["inspect_contract", "inspect_config"], "sequence": ["inspect_contract", "inspect_config", "repair"]}, 1)
        self.assertNotIn("read_logs", strategy["tools"])

    def test_safe_singleton_verification_normalization(self):
        strategy = validate_strategy({**BASELINE, "verification": "final_check"}, 1)
        self.assertEqual(strategy["verification"], ["final_check"])
        with self.assertRaises(ValueError):
            validate_strategy({**BASELINE, "verification": "invented_tool"}, 1)

    def test_rejects_new_capabilities_and_unbounded_attempts(self):
        for changes in ({"tools": ["shell"]}, {"max_attempts": 999}, {"sequence": ["read_logs"]}, {"max_attempts": True}, {"verification": ["magic"]}):
            with self.assertRaises(ValueError):
                validate_strategy({**BASELINE, **changes}, 1)

    def test_json_parser(self):
        self.assertEqual(parse_json('```json\n{"a":1}\n```'), {"a": 1})
        with self.assertRaises(ValueError):
            parse_json('[]')


class ScriptedClient:
    """Unit-test adapter only. Never used by CLI, server, or demo."""
    def __init__(self):
        self.prompts = []
        from core_genesis.crusoe import DEFAULT_MODEL
        self.model = DEFAULT_MODEL
        self.max_retries = 0
        self.last_status = 200

    def chat(self, messages, **kwargs):
        system, prompt = messages[0]["content"], messages[1]["content"]
        self.prompts.append((system, prompt))
        if "Architect" in system:
            answer = {"approach": "Diagnose from logs", "hypothesis": "Missing evidence"}
        elif "Observer" in system:
            strategy = {**BASELINE, "name": "Inspect before repair", "tools": ["read_logs", "inspect_config", "inspect_contract"], "sequence": ["read_logs", "inspect_config", "inspect_contract", "repair", "verify"]}
            answer = {"observation": {"weakness": "No inspection", "recommendation": "Inspect configuration and contracts"}, "candidates": [strategy, {**strategy, "name": "Alternative inspection"}]}
        else:
            payload = json.loads(prompt)
            repairs = []
            for job in payload["jobs"]:
                case = next(c for c in CASES if c.id == job["incident"]["id"])
                patch = repair(case) if "service_contract" in job["incident"] else dict(case.config)
                repairs.append({"version": job["version"], "case_id": case.id, "diagnosis": "Unit test only", "patch": patch})
            answer = {"repairs": repairs}
        return {"choices": [{"message": {"content": json.dumps(answer)}}], "usage": {"prompt_tokens": 5, "completion_tokens": 5, "total_tokens": 10}, "model": self.model}


class LifecycleTests(unittest.TestCase):
    def test_full_loop_and_heldout_isolation(self):
        with tempfile.TemporaryDirectory() as directory:
            client = ScriptedClient()
            engine = test_engine(directory, client)
            self.assertTrue(engine.start())
            self.assertFalse(engine.start())
            engine.run()
            state = engine.snapshot()
            self.assertEqual(state["status"], "complete")
            self.assertEqual(state["decisions"][0]["action"], "promote")
            self.assertEqual(len(state["runs"]), 15)
            self.assertEqual(json.loads(engine.path.read_text())["id"], state["id"])
            for role, prompt in client.prompts:
                if "Observer" in role or "Scientist" in role:
                    self.assertNotIn("eval-timeout", prompt)
                    self.assertNotIn("eval-pool", prompt)
                    self.assertNotIn("eval-route", prompt)
            self.assertEqual(state["inference_calls"], 6)

    def test_promoted_strategy_survives_restart_and_ties_roll_back(self):
        with tempfile.TemporaryDirectory() as directory:
            engine = test_engine(directory, ScriptedClient())
            engine.start()
            engine.run()
            restored = test_engine(directory, ScriptedClient())
            self.assertEqual(restored.champion["version"], 1)
            restored.start()
            self.assertEqual(restored.state["baseline_version"], 1)
            restored.run()
            self.assertEqual(restored.state["decisions"][0]["action"], "rollback")
            self.assertEqual(restored.state["current_generation"], 1)
            fresh = test_engine(directory, ScriptedClient(), fresh=True)
            fresh.start()
            self.assertEqual(fresh.state["baseline_version"], 0)

    def test_tools_after_repair_do_not_leak_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            client = ScriptedClient()
            engine = test_engine(directory, client)
            engine.start()
            strategy = {**BASELINE, "tools": ["read_logs", "inspect_contract", "inspect_config"], "sequence": ["read_logs", "repair", "inspect_contract", "inspect_config"]}
            results = engine.evaluate(strategy, "development")
            self.assertFalse(any(r["passed"] for r in results))
            for _, prompt in client.prompts:
                for job in json.loads(prompt)["jobs"]:
                    self.assertNotIn("config", job["incident"])
                    self.assertNotIn("service_contract", job["incident"])

    def test_budget_stops_safely_without_promotion(self):
        with tempfile.TemporaryDirectory() as directory:
            engine = test_engine(directory, ScriptedClient())
            engine.max_calls = 1
            engine.start()
            engine.run()
            self.assertEqual(engine.state["status"], "error")
            self.assertEqual(engine.state["decisions"], [])
            self.assertEqual(engine.state["current_generation"], 0)


if __name__ == "__main__":
    unittest.main()
