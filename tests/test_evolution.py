import copy
import json
from pathlib import Path
import tempfile
import unittest

from core_genesis.budget import RequestBudget
from core_genesis.crusoe import DEFAULT_MODEL
from core_genesis.evolution import EvolutionEngine
from core_genesis.suites import generate, manifest, family
from core_genesis.team import CONTROL, execute, validate_team, validate_program, compare, aggregate, normalize_program, assemble_team
from core_genesis.team import OWNERSHIP
from core_genesis.assembly import assemble_design


RULES = [
    {"target": "timeout_ms", "operation": "increment", "source": "contract.upstream_p99_ms"},
    {"target": "retries", "operation": "copy", "source": "contract.max_retries"},
    {"target": "pool_size", "operation": "copy", "source": "contract.concurrent_queries"},
    {"target": "health_path", "operation": "copy", "source": "contract.registered_health_path"},
    {"target": "port", "operation": "copy", "source": "contract.listening_port"},
]


def reference_team():
    team = copy.deepcopy(CONTROL)
    team["agents"][0]["tools"] = ["read_logs", "inspect_config", "inspect_contract", "recall_memory"]
    team["workflow"] = [{"agent": "executor", "action": action} for action in ("read_logs", "inspect_config", "inspect_contract", "apply_rules", "commit")]
    team["program"] = {"executor": copy.deepcopy(RULES)}
    return validate_team(team)


class RuntimeTests(unittest.TestCase):
    def test_typed_assembly_preserves_full_coverage_and_changes_executed_coordination(self):
        workers = [{"specialty": kind, "tools": ["inspect_config", "inspect_contract"], "instructions": "Own " + kind} for kind in ("latency", "capacity", "routing")]
        design = {"workers": workers, "coordination": "specialist_pipeline", "extra_review": True}
        pipeline, _, _ = assemble_design(CONTROL, design, "Pipeline")
        pipeline["program"] = {agent["id"]: [rule for rule in RULES if rule["target"] in OWNERSHIP[agent["specialty"]]] for agent in pipeline["agents"]}
        design["coordination"] = "shared_evidence"
        shared, _, _ = assemble_design(CONTROL, design, "Shared")
        shared["program"] = pipeline["program"]
        for case in generate(1, "test"):
            before, after = execute(pipeline, case), execute(shared, case)
            self.assertTrue(before["passed"] and after["passed"])
            self.assertLess(after["metrics"]["tool_calls"], before["metrics"]["tool_calls"])

    def test_fixed_controller_keeps_specialist_workflows_valid_without_new_authority(self):
        raw = reference_team()
        raw["agents"] = [{"id": "latency", "specialty": "latency", "tools": ["inspect_config", "inspect_contract"], "instructions": "Latency only"}]
        raw["workflow"] = [{"agent": "latency", "action": "inspect_config"}, {"agent": "latency", "action": "inspect_contract"},
                           {"agent": "executor", "action": "apply_rules"}, {"agent": "executor", "action": "commit"}]
        team, notes = assemble_team(raw)
        team["program"] = {"latency": RULES}
        self.assertEqual(len(notes), 2)
        self.assertEqual(team["workflow"][-1]["agent"], "controller")
        self.assertTrue(execute(team, generate(1, "test")[0])["passed"])
        self.assertFalse(execute(team, generate(1, "test")[1])["passed"])
        raw["workflow"] = [{"agent": "controller", "action": "inspect_contract"}, {"agent": "latency", "action": "apply_rules"}, {"agent": "controller", "action": "commit"}]
        with self.assertRaises(ValueError):
            assemble_team(raw)

    def test_unverified_memory_is_never_recalled(self):
        team = reference_team()
        team["program"] = {}
        team["memory_policy"] = "inherit_verified"
        team["workflow"].insert(0, {"agent": "executor", "action": "recall_memory"})
        result = execute(team, generate(1, "test")[0], [{"family": "latency", "rules": RULES, "status": "proposed"}])
        self.assertEqual(result["metrics"]["memory_hits"], 0)
        self.assertFalse(result["passed"])

    def test_unambiguous_json_shapes_normalize_without_new_capabilities(self):
        program, notes = normalize_program({"agent_id": [{"target": "retries", "operation": "literal", "source": "3"}]}, CONTROL)
        self.assertEqual(program, {"executor": [{"target": "retries", "operation": "literal", "value": 3}]})
        self.assertEqual(len(notes), 2)
        with self.assertRaises(ValueError):
            normalize_program({"agent_id": [{"target": "port", "operation": "literal", "source": "contract.listening_port"}]}, CONTROL)

    def test_general_rules_repair_unseen_values_and_do_not_mutate_fixtures(self):
        team = reference_team()
        for seed in range(20):
            for case in generate(seed, "unseen"):
                before = dict(case.config)
                self.assertTrue(execute(team, case)["passed"])
                self.assertEqual(case.config, before)

    def test_missing_evidence_and_late_tool_calls_cannot_read_contract(self):
        team = reference_team()
        team["workflow"] = [{"agent": "executor", "action": action} for action in ("apply_rules", "inspect_config", "inspect_contract", "commit")]
        for case in generate(10, "unseen"):
            record = execute(team, case)
            self.assertFalse(record["passed"])
            self.assertTrue(any(op["status"] == "blocked" for step in record["trace"] for op in step.get("operations", [])))

    def test_specialization_is_enforced_at_runtime(self):
        team = reference_team()
        team["agents"][0]["specialty"] = "latency"
        results = [execute(team, case) for case in generate(10, "unseen")]
        self.assertTrue(all(r["passed"] for r in results if r["family"] == "latency"))
        self.assertFalse(any(r["passed"] for r in results if r["family"] != "latency"))

    def test_unknown_code_and_capabilities_rejected(self):
        for rule in ({"target": "port", "operation": "eval", "source": "contract.listening_port"},
                     {"target": "port", "operation": "copy", "source": "__import__('os')"},
                     {"target": "shell", "operation": "literal", "value": "ls"}):
            with self.assertRaises(ValueError):
                validate_program({"executor": [rule]}, reference_team())
        team = reference_team()
        team["agents"][0]["tools"].append("shell")
        with self.assertRaises(ValueError):
            validate_team(team)

    def test_memory_requires_explicit_recall_and_is_actually_applied(self):
        team = reference_team()
        case = generate(10, "unseen")[0]
        team["program"] = {}
        team["memory_policy"] = "inherit_verified"
        memory = [{"family": "latency", "rules": RULES[:2], "status": "development_verified"}]
        self.assertFalse(execute(team, case, memory)["passed"])
        team["workflow"].insert(0, {"agent": "executor", "action": "recall_memory"})
        result = execute(team, case, memory)
        self.assertTrue(result["passed"])
        self.assertEqual(result["metrics"]["memory_hits"], 1)

    def test_review_is_operational_and_always_enforced_at_commit(self):
        team = reference_team()
        team["review_policy"] = "contract"
        self.assertTrue(all(execute(team, case)["passed"] for case in generate(1, "test")))
        team["program"]["executor"][0] = {"target": "timeout_ms", "operation": "literal", "value": 0}
        result = execute(team, generate(1, "test")[0])
        self.assertFalse(result["passed"])
        self.assertEqual(result["trace"][-1]["status"], "rejected")
        self.assertEqual(result["patch"], {})

    def test_evidence_cache_reduces_real_tool_invocations(self):
        team = reference_team()
        team["workflow"].insert(1, {"agent": "executor", "action": "read_logs"})
        case = generate(1, "test")[0]
        uncached = execute(team, case)
        team["cache_evidence"] = True
        cached = execute(team, case)
        self.assertEqual(cached["passed"], uncached["passed"])
        self.assertEqual(uncached["metrics"]["tool_calls"] - cached["metrics"]["tool_calls"], 1)
        self.assertTrue(any(step["kind"] == "cache_hit" for step in cached["trace"]))


class FreshSuiteTests(unittest.TestCase):
    def test_reproduction_and_disjoint_fresh_shards(self):
        suites, info = manifest(123)
        other, repeated = manifest(123)
        self.assertEqual(info, repeated)
        self.assertEqual(suites, other)
        self.assertNotEqual(info["sha256"], manifest(124)[1]["sha256"])
        ids = [case.id for name, cases in suites.items() for case in cases]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(len(suites), 6)
        self.assertEqual({family(c) for c in suites["sealed"]}, {"latency", "capacity", "routing"})


class GenerationTransport:
    """Scripted unit-test transport only, never used in the production Arena."""
    model = DEFAULT_MODEL
    max_retries = 0
    last_status = 200

    def __init__(self):
        self.prompts = []
        self.generation = 0

    def chat(self, messages, **kwargs):
        system, prompt = messages[0]["content"], json.loads(messages[1]["content"])
        self.prompts.append((system, prompt))
        if "Architect" in system:
            answer = {"approach": "Unit-test objective plan", "success_criteria": ["No regressions"]}
        elif "Scientist" in system:
            self.generation += 1
            team = reference_team()
            if self.generation == 3:
                team["workflow"] = [step for step in team["workflow"] if step["action"] != "read_logs"]
            changes = {key: value for key, value in team.items() if key not in {"program", "name"}}
            answer = {"observation": {"weakness": "Unit-test observation", "lesson": "Use generic service references"},
                      "mutations": [{"name": "Unit candidate A", "reason": "Test lineage", "changes": changes},
                                    {"name": "Unit candidate B", "reason": "Test competition", "changes": changes}]}
        else:
            programs = []
            for item in prompt["teams"]:
                node = item["node_id"]
                rules = [] if node == "g0" else copy.deepcopy(RULES[-2:] if node.startswith("g1") else RULES)
                programs.append({"node_id": node, "program": {"executor": rules}})
            answer = {"programs": programs}
        return {"model": self.model, "usage": {"prompt_tokens": 5, "completion_tokens": 5, "total_tokens": 10},
                "choices": [{"message": {"content": json.dumps(answer)}}]}


class EvolutionTests(unittest.TestCase):
    def test_operator_search_and_memory_reuse_avoid_a_compiler_request(self):
        class OperatorTransport(GenerationTransport):
            def chat(self, messages, **kwargs):
                system, prompt = messages[0]["content"], json.loads(messages[1]["content"])
                self.prompts.append((system, prompt))
                if "Architect" in system:
                    answer = {"approach": "Use development evidence", "success_criteria": ["No regressions"]}
                elif "Scientist" in system:
                    self.generation += 1
                    kinds = ["latency", "capacity", "routing"]
                    def design(specialties, style, extra, source="compile"):
                        return {"instructions": "Respect every contract", "workers": [{"specialty": kind, "tools": ["inspect_contract"] if source == "reuse_memory" else ["read_logs", "inspect_config", "inspect_contract"], "instructions": "Own " + kind} for kind in specialties],
                                "coordination": style, "review_policy": "schema", "memory_policy": "inherit_verified" if source == "reuse_memory" else "none",
                                "cache_evidence": False, "extra_review": extra, "procedure_source": source}
                    if self.generation == 1:
                        designs = [design(kinds, "specialist_pipeline", True), design(kinds, "shared_evidence", True)]
                    elif self.generation == 2:
                        designs = [design(kinds, "shared_evidence", False), design(["general"], "shared_evidence", False)]
                    else:
                        designs = [design(["general"], "memory_first", False, "reuse_memory")] * 2
                    answer = {"observation": {"weakness": "Unit-test coverage/efficiency", "lesson": "Reference contracts and reuse verified rules"},
                              "mutations": [{"name": "Operator candidate " + str(i), "reason": "Unit-test operator selection", "design": d} for i, d in enumerate(designs)]}
                else:
                    answer = {"programs": [{"node_id": item["node_id"], "program": {agent["id"]: ([] if item["node_id"] == "g0" else [r for r in RULES if r["target"] in OWNERSHIP[agent["specialty"]]]) for agent in item["team"]["agents"]}} for item in prompt["teams"]]}
                return {"model": self.model, "usage": {"prompt_tokens": 5, "completion_tokens": 5, "total_tokens": 10}, "choices": [{"message": {"content": json.dumps(answer)}}]}
        with tempfile.TemporaryDirectory() as directory:
            engine = EvolutionEngine(directory, OperatorTransport(), fresh=True, budget=RequestBudget(Path(directory) / ".budget", history=directory))
            engine.start(seed=123)
            engine.run()
            self.assertEqual(engine.state["status"], "complete", engine.state.get("error_detail"))
            self.assertEqual(engine.state["inference_calls"], 7)
            self.assertEqual([d["action"] for d in engine.state["decisions"]], ["promote"] * 3)
            self.assertEqual(engine.node("g3a")["procedure_origin"], "development_verified_memory")
            self.assertGreater(engine.node("g3a")["metrics"]["sealed"]["memory_hits"], 0)
            from core_genesis.replay import replay_v2
            self.assertEqual(replay_v2(engine.snapshot())["verified_decisions"], 3)

    def test_three_real_rounds_lineage_memory_and_eight_request_schedule(self):
        with tempfile.TemporaryDirectory() as directory:
            budget = RequestBudget(Path(directory) / ".budget", history=directory)
            client = GenerationTransport()
            engine = EvolutionEngine(directory, client, fresh=True, budget=budget)
            engine.start(seed=123)
            engine.run()
            state = engine.snapshot()
            self.assertEqual(state["status"], "complete", state.get("error_detail"))
            self.assertEqual(len(state["nodes"]), 7)
            self.assertEqual(len(state["rounds"]), 3)
            self.assertEqual(state["inference_calls"], 8)
            self.assertEqual(state["cycles"], 2)
            self.assertEqual([d["action"] for d in state["decisions"]], ["promote"] * 3)
            self.assertEqual([d["kind"] for d in state["decisions"]], ["success_gain", "success_gain", "efficiency_gain"])
            self.assertEqual(state["active_node_id"], "g3a")
            self.assertEqual(engine.node("g0")["team"]["instructions"], "Unit-test objective plan")
            self.assertEqual(engine.node("g2a")["parent_id"], "g1a")
            self.assertEqual(engine.node("g3a")["parent_id"], "g2a")
            self.assertTrue(engine.node("g2a")["memory_snapshot"])
            self.assertTrue(state["objective_achieved"])
            self.assertEqual(state["sealed_comparison"]["active"]["passed"], 6)
            for role, prompt in client.prompts:
                encoded = json.dumps(prompt)
                self.assertNotIn("validation-g", encoded)
                self.assertNotIn("sealed-", encoded)
                self.assertNotIn("eval-timeout", encoded)
            self.assertTrue(all("development-" in case for lesson in state["memory"] for case in lesson["source_case_ids"]))
            entries = state["budget_audit"]["entries"]
            self.assertLessEqual(max(sum(e["cycle"] == cycle for e in entries) for cycle in (0, 1)), 6)
            from core_genesis.replay import replay_v2
            self.assertEqual(replay_v2(state)["verified_decisions"], 3)
            tampered = copy.deepcopy(state)
            tampered["runs"][0]["passed"] = not tampered["runs"][0]["passed"]
            with self.assertRaises(ValueError):
                replay_v2(tampered)

    def test_invalid_objectives_and_generation_counts_rejected_without_requests(self):
        with tempfile.TemporaryDirectory() as directory:
            client = GenerationTransport()
            engine = EvolutionEngine(directory, client, budget=RequestBudget(Path(directory) / ".budget", history=directory))
            for parameters in ({"objective": "x"}, {"generations": 4}, {"seed": -1}):
                with self.assertRaises(ValueError):
                    engine.start(**parameters)
            self.assertFalse(client.prompts)

    def test_invalid_sibling_does_not_abort_valid_competition(self):
        class FaultTransport(GenerationTransport):
            def chat(self, messages, **kwargs):
                response = super().chat(messages, **kwargs)
                if "Scientist" in messages[0]["content"]:
                    content = json.loads(response["choices"][0]["message"]["content"])
                    content["mutations"][1]["changes"]["workflow"].append({"agent": "nonexistent", "action": "commit"})
                    response["choices"][0]["message"]["content"] = json.dumps(content)
                return response
        with tempfile.TemporaryDirectory() as directory:
            engine = EvolutionEngine(directory, FaultTransport(), fresh=True, budget=RequestBudget(Path(directory) / ".budget", history=directory))
            engine.start(generations=1, seed=123)
            engine.run()
            self.assertEqual(engine.state["status"], "complete")
            self.assertEqual(engine.node("g1b")["status"], "invalid")
            self.assertFalse(any(r["node_id"] == "g1b" for r in engine.state["runs"]))
            self.assertEqual(engine.state["decisions"][0]["action"], "promote")
            from core_genesis.replay import replay_v2
            self.assertEqual(replay_v2(engine.snapshot())["verified_decisions"], 1)

    def test_all_invalid_candidates_roll_back_without_paid_compilation(self):
        class FaultTransport(GenerationTransport):
            def chat(self, messages, **kwargs):
                response = super().chat(messages, **kwargs)
                if "Scientist" in messages[0]["content"]:
                    content = json.loads(response["choices"][0]["message"]["content"])
                    for mutation in content["mutations"]:
                        mutation["changes"]["workflow"].append({"agent": "nonexistent", "action": "commit"})
                    response["choices"][0]["message"]["content"] = json.dumps(content)
                return response
        with tempfile.TemporaryDirectory() as directory:
            engine = EvolutionEngine(directory, FaultTransport(), fresh=True, budget=RequestBudget(Path(directory) / ".budget", history=directory))
            engine.start(generations=1, seed=123)
            engine.run()
            self.assertEqual(engine.state["status"], "complete")
            self.assertEqual(engine.state["active_node_id"], "g0")
            self.assertEqual(engine.state["inference_calls"], 3)
            self.assertEqual(engine.state["decisions"][0]["kind"], "invalid_mutations")
            from core_genesis.replay import replay_v2
            self.assertEqual(replay_v2(engine.snapshot())["verified_decisions"], 1)


if __name__ == "__main__":
    unittest.main()
