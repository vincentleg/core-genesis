"""Isolated transport doubles only; never published as live mission evidence."""
import copy
import json
from pathlib import Path
import tempfile
import unittest

from core_genesis.company import Company, Paused
from core_genesis.budget import RequestBudget, BudgetError
from core_genesis.crusoe import DEFAULT_MODEL
from core_genesis.mission_eval import BASE_POLICY, STRICT_POLICY, evaluate_mutations, verify_report
from core_genesis.repository import safe_path, fetch_snapshot, API


def snapshot(guard=lambda: None):
    guard()
    return {"commit": "a" * 40, "file_count": 2, "structure": ["README.md", "build.js"], "limitations": ["Unit test snapshot"],
        "sources": [{"id": "S1", "path": "README.md", "line_start": 1, "line_end": 2, "text": "CORE is a prototype.\nHumans authorize.", "url": "https://github.com/vincentleg/core/blob/" + "a" * 40 + "/README.md"},
                    {"id": "S2", "path": "build.js", "line_start": 1, "line_end": 1, "text": "const gateway = true;", "url": "https://github.com/vincentleg/core/blob/" + "a" * 40 + "/build.js"}]}


def report():
    return {"summary": "Unit test engineering plan", "priorities": [{"title": "Priority " + str(i), "finding": "Observed source fact",
        "actions": ["Prepare a reviewable change"], "verification": ["Run authorized checks later"], "uncertainty": "No production behavior inspected",
        "citations": [{"source_id": "S1", "line_start": 1, "line_end": 1, "quote": "CORE is a prototype."}]} for i in range(3)], "limitations": ["Unit test"]}


class MissionTransport:
    model = DEFAULT_MODEL
    max_retries = 0
    last_status = 200
    def __init__(self):
        self.prompts = []
    def chat(self, messages, **kwargs):
        role = messages[0]["content"]
        prompt = json.loads(messages[1]["content"])
        self.prompts.append((role, prompt))
        if "Synthetic " in role:
            answer = {"priority": "1", "position": "conditional", "concern": "Synthetic concern", "recommendation": "Validate with real people", "verification_needed": "Real user research"}
        elif "Growth Director" in role:
            answer = {"strategy": "Truthful proposal only", "posts": [{"platform": "X", "text": "We are analyzing proposed CORE improvements, not announcing shipped changes.", "priority_ids": ["1"], "visual_brief": "Source diagram"}]}
        elif "Scientist" in role:
            answer = {"observed_weakness": "Citation preflight misses quote errors", "mutations": [{"name": "Strict", "reason": "Validate exact evidence", "policy": STRICT_POLICY}, {"name": "Permissive", "reason": "Comparison", "policy": BASE_POLICY}]}
        else:
            answer = report()
        return {"model": self.model, "usage": {"prompt_tokens": 5, "completion_tokens": 5, "total_tokens": 10}, "choices": [{"message": {"content": json.dumps(answer)}}]}


class CompanyTests(unittest.TestCase):
    def test_failed_citations_get_one_bounded_repair_and_never_reach_growth_unverified(self):
        class RepairTransport(MissionTransport):
            def chat(self, messages, **kwargs):
                response = super().chat(messages, **kwargs)
                prompt = json.loads(messages[1]['content'])
                if 'Engineering Lead' in messages[0]['content'] and 'rejected_plan' not in prompt['data']:
                    bad = report()
                    bad['priorities'][0]['citations'][0]['quote'] = 'invented quotation'
                    response['choices'][0]['message']['content'] = json.dumps(bad)
                if 'Growth Director' in messages[0]['content']:
                    self.allowed = kwargs['response_format']['json_schema']['schema']['properties']['posts']['items']['properties']['priority_ids']['items']['enum']
                return response
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            client = RepairTransport()
            company = Company(root / 'company', RequestBudget(root / 'budget', history=root / 'experiments'), client, snapshot)
            company.start('Analyze CORE using bounded evidence correction.')
            company.run()
            state = company.snapshot()
            self.assertEqual(state['status'], 'complete', state.get('error_detail'))
            self.assertFalse(state['initial_verification']['passed'])
            self.assertTrue(state['verification']['passed'])
            self.assertEqual(state['usage']['physical_requests'], 10)
            self.assertEqual(client.allowed, ['1', '2', '3'])
            self.assertEqual(state['artifacts']['engineering_initial']['priorities'][0]['citations'][0]['quote'], 'invented quotation')

    def test_real_workflow_protocol_has_five_independent_personas_and_objective_promotion(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            transport = MissionTransport()
            company = Company(root / "company", RequestBudget(root / "budget", history=root / "experiments"), transport, snapshot)
            company.start("Analyze CORE and prepare three evidence-backed priorities.")
            company.run()
            state = company.snapshot()
            self.assertEqual(state["status"], "complete", state.get("error_detail"))
            self.assertEqual(state["usage"]["physical_requests"], 9)
            self.assertEqual(len(state["panel"]), 5)
            self.assertEqual(state["panel_summary"]["real_users"], 0)
            self.assertEqual(state["evolution"]["action"], "promote")
            self.assertEqual(state["evolution"]["comparison"]["heldout"]["candidate"]["passed"], 6)
            self.assertTrue(state["verification"]["passed"])
            self.assertTrue(any(h["status"] == "awaiting_ceo" for h in state["handoffs"]))
            persona_prompts = [p for role, p in transport.prompts if "Synthetic " in role]
            self.assertEqual(len(persona_prompts), 5)
            self.assertTrue(all("panel" not in p["data"] for p in persona_prompts))
            scientist_prompt = next(p for role, p in transport.prompts if "Scientist" in role)
            self.assertNotIn("heldout", json.dumps(scientist_prompt))
            self.assertNotIn("regression", json.dumps(scientist_prompt))
            self.assertTrue((company.missions / (state["id"] + ".md")).exists())
            decision = company.governance()["decisions"][0]
            company.control("approve", decision["id"])
            self.assertEqual(company.governance()["decisions"][0]["status"], "approved_for_manual_export")
            self.assertFalse(company.snapshot()["artifacts"]["growth"]["published"])
            self.assertEqual(company.snapshot()["artifacts"]["growth"]["connected_accounts"], [])
            from core_genesis.mission_replay import replay_mission
            self.assertEqual(replay_mission(company.snapshot())["verified_mutation_gates"], 1)
            tampered = company.snapshot()
            tampered["evolution"]["action"] = "rollback"
            with self.assertRaises(ValueError):
                replay_mission(tampered)

    def test_failed_evidence_blocks_growth_but_still_reaches_independent_evolution(self):
        class InvalidTransport(MissionTransport):
            def chat(self, messages, **kwargs):
                response = super().chat(messages, **kwargs)
                if 'Engineering Lead' in messages[0]['content']:
                    bad = report()
                    for priority in bad['priorities']:
                        priority['citations'][0]['quote'] = 'not in the source'
                    response['choices'][0]['message']['content'] = json.dumps(bad)
                return response
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            client = InvalidTransport()
            company = Company(root / 'company', RequestBudget(root / 'budget', history=root / 'history'), client, snapshot)
            company.start('Analyze CORE with intentionally invalid unit-test evidence.')
            company.run()
            state = company.snapshot()
            self.assertEqual(state['status'], 'needs_review', state.get('error_detail'))
            self.assertEqual(state['verification']['valid_priorities'], 0)
            self.assertNotIn('growth', state['artifacts'])
            self.assertEqual(company.governance()['decisions'], [])
            self.assertTrue(state.get('evolution'))
            self.assertFalse(any('Growth Director' in role for role, _ in client.prompts))

    def test_public_export_withholds_unapproved_draft_text_and_raw_model_output(self):
        from core_genesis.publication import public_company_record
        private = {"artifacts": {"growth": {"strategy": "Private draft strategy", "posts": [{"text": "Private draft text", "visual_brief": "Private brief"}]}},
                   "events": [{"agent": "Growth Director", "output": '{"draft":"Private draft text"}'}]}
        public = public_company_record(private, {"decisions": []})
        self.assertNotIn("Private draft", json.dumps(public))
        self.assertTrue(public["mission"]["artifacts"]["growth"]["public_content_withheld"])
        self.assertIn("output_sha256", public["mission"]["events"][0])
        self.assertEqual(private["artifacts"]["growth"]["posts"][0]["text"], "Private draft text")

    def test_promoted_configuration_requires_replayable_provenance_before_reuse(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            client = MissionTransport()
            company = Company(root / 'company', RequestBudget(root / 'budget', history=root / 'history'), client, snapshot)
            company.start('Analyze CORE and preserve a verified policy.')
            company.run()
            original = company.snapshot()
            following = company.start('Analyze CORE using the independently verified policy.')
            self.assertEqual(following['configuration']['version'], 1)
            self.assertEqual(following['configuration']['source_mission'], original['id'])
            self.assertEqual(following['configuration']['policy'], STRICT_POLICY)
            self.assertEqual(len(client.prompts), 9)  # Starting never calls inference.
            company.state['status'] = 'interrupted'
            changed = json.loads(company.policy_path.read_text())
            changed['policy']['exact_quotes'] = False
            company.write(company.policy_path, changed)
            with self.assertRaisesRegex(ValueError, 'differs'):
                company.start('Analyze CORE with a tampered active policy.')

    def test_ceo_pause_blocks_missions_and_centralized_inference_without_a_call(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            client = MissionTransport()
            budget = RequestBudget(root / "budget", history=root / "history")
            company = Company(root / "company", budget, client, snapshot)
            company.control("pause")
            with self.assertRaises(Paused):
                company.start("Analyze CORE read-only")
            with self.assertRaises(BudgetError):
                budget.chat("test", 0, "Research", [{"role": "user", "content": "No call"}], 10, client)
            self.assertEqual(client.prompts, [])
            company.control("resume")
            self.assertEqual(company.snapshot()["status"], "idle")

    def test_citation_gate_rejects_fabricated_quotes_and_line_ranges(self):
        for field, value in (("quote", "invented result"), ("line_end", 99), ("source_id", "unknown")):
            bad = report()
            bad["priorities"][0]["citations"][0][field] = value
            self.assertFalse(verify_report(bad, snapshot())["passed"])

    def test_independent_gate_rolls_back_weakened_policy(self):
        mutation = {"name": "Weaken", "reason": "Unit test", "policy": BASE_POLICY}
        result = evaluate_mutations(STRICT_POLICY, [mutation, mutation], 123)
        self.assertEqual(result["action"], "rollback")
        self.assertEqual(result["kind"], "regression")

    def test_sensitive_and_unbounded_paths_are_excluded(self):
        for path in [".env", ".env.example", "secrets.json", "src/credentials.js", "../README.md", "/README.md", "node_modules/app.js", "key.pem"]:
            self.assertFalse(safe_path(path), path)
        self.assertTrue(safe_path("scripts/gateway.mjs"))

    def test_cached_immutable_sources_require_rechecking_compact_branch_metadata(self):
        calls = []
        old = snapshot()
        old.update(repository="vincentleg/core", requests=[])
        def read(url, limit, guard):
            calls.append(url)
            if url == API:
                return json.dumps({"private": False, "full_name": "vincentleg/core", "default_branch": "main"}).encode()
            if url.endswith("/branches/main"):
                return json.dumps({"commit": {"sha": "a" * 40}}).encode()
            raise AssertionError("Unnecessary source download")
        result = fetch_snapshot(read=read, previous=old)
        self.assertTrue(result["cache_reused"])
        self.assertEqual(len(calls), 2)
        self.assertTrue(calls[-1].endswith("/branches/main"))
