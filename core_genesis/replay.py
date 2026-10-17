"""Independent replay of V2 programs, traces, development selection and every gate."""
import hashlib
import json
import re
from pathlib import Path

from .suites import manifest, family
from .team import validate_team, validate_program, execute, fingerprint, compare, aggregate
from .assembly import assemble_design

ROOT = Path(__file__).resolve().parent.parent


def replay_v2(state):
    for name, expected in state["source_hashes"].items():
        if name not in {"team.py", "suites.py", "benchmark.py", "assembly.py"} or hashlib.sha256((ROOT / "core_genesis" / name).read_bytes()).hexdigest() != expected:
            raise ValueError("Evaluator source fingerprint differs: use the source revision that produced this record")
    suites, suite_manifest = manifest(int(state["suite_manifest"]["seed"]), state["requested_generations"])
    if suite_manifest != state["suite_manifest"]:
        raise ValueError("Suite manifest mismatch")
    nodes = {node["id"]: node for node in state["nodes"]}
    if len(nodes) != len(state["nodes"]):
        raise ValueError("Duplicate lineage node")
    sources = {state["id"]: state}
    checked_lessons = set()

    def verify_lesson(lesson):
        identity = json.dumps(lesson, sort_keys=True)
        if identity in checked_lessons:
            return
        source_id = lesson.get("source_experiment_id", "")
        if not re.fullmatch(r"[0-9a-f-]+", source_id):
            raise ValueError("Invalid memory provenance experiment")
        if source_id not in sources:
            sources[source_id] = json.loads((ROOT / "experiments" / (source_id + ".json")).read_text())
        source = sources[source_id]
        origin = next((n for n in source["nodes"] if n["id"] == lesson.get("source_node_id")), None)
        if not origin or origin["status"] != "promoted":
            raise ValueError("Memory source was never promoted")
        source_suites, _ = manifest(int(source["suite_manifest"]["seed"]), source["requested_generations"])
        cases = [case for case in source_suites["development"] if family(case) == lesson.get("family")]
        if not cases or lesson.get("source_case_ids") != [case.id for case in cases]:
            raise ValueError("Memory source cases do not match the development family")
        rules = []
        for case in cases:
            record = execute(origin["team"], case, origin["memory_snapshot"])
            evidence = [r for r in source["runs"] if r["node_id"] == origin["id"] and r["suite"] == "development" and r["case_id"] == case.id]
            if not record["passed"] or not evidence or any(not r["passed"] or r["patch"] != record["patch"] for r in evidence):
                raise ValueError("Memory source lacks reproducible passing development evidence")
            for step in record["trace"]:
                for operation in step.get("operations", []):
                    rule = operation.get("rule")
                    if operation["status"] == "applied" and rule and rule["operation"] != "literal" and rule not in rules:
                        rules.append(rule)
        if not rules or rules != lesson.get("rules") or lesson.get("status") != "development_verified":
            raise ValueError("Memory rules differ from applied development evidence")
        checked_lessons.add(identity)

    for lesson in state.get("memory", []):
        verify_lesson(lesson)
    for node in nodes.values():
        if node["status"] == "invalid":
            if any(record["node_id"] == node["id"] for record in state["runs"]):
                raise ValueError("Invalid candidate was executed")
            try:
                if node["invalid_phase"] == "design":
                    assemble_design(nodes[node["parent_id"]]["team"], node["design"], node["team"]["name"], node["memory_snapshot"])
                elif node["invalid_phase"] == "configuration":
                    validate_team(node["team"], program_required=False)
                else:
                    program = validate_program(node["rejected_program"], node["team"])
                    if node["generation"] > 0 and any(rule["operation"] == "literal" for rules in program.values() for rule in rules):
                        raise ValueError("Literal fixture answer rejected by mutation policy")
            except ValueError:
                continue
            raise ValueError("Recorded invalid candidate is actually valid")
        team = validate_team(node["team"])
        if node.get("design"):
            assembled, _, _ = assemble_design(nodes[node["parent_id"]]["team"], node["design"], node["team"]["name"], node["memory_snapshot"])
            if {k: v for k, v in assembled.items() if k != "program"} != {k: v for k, v in team.items() if k != "program"}:
                raise ValueError("Typed team assembly differs from the recorded configuration")
        if fingerprint(team) != node["team_sha256"]:
            raise ValueError("Team fingerprint mismatch")
        if node["parent_id"] is not None and (node["parent_id"] not in nodes or nodes[node["parent_id"]]["generation"] >= node["generation"]):
            raise ValueError("Invalid parent lineage")
        for lesson in node["memory_snapshot"]:
            if lesson.get("status") != "development_verified" or any(not case_id.startswith("development-") for case_id in lesson.get("source_case_ids", [])):
                raise ValueError("Memory contains unverified or non-development evidence")
            verify_lesson(lesson)
    seen = set()
    for record in state["runs"]:
        if record["id"] in seen:
            raise ValueError("Duplicate execution record")
        seen.add(record["id"])
        node = nodes[record["node_id"]]
        case = next(case for case in suites[record["suite"]] if case.id == record["case_id"])
        actual = execute(node["team"], case, node["memory_snapshot"])
        for key in ("passed", "patch", "verification", "trace"):
            if actual[key] != record[key]:
                raise ValueError("Execution replay mismatch: " + record["id"] + "/" + key)
        for key in ("tool_calls", "rule_steps", "workflow_steps", "work_units", "memory_hits"):
            if actual["metrics"][key] != record["metrics"][key]:
                raise ValueError("Work accounting mismatch")
    active_id = "g0"
    for round_info, decision in zip(state["rounds"], state["decisions"]):
        generation, evaluation_id = round_info["generation"], round_info["evaluation_id"]
        if decision["parent_id"] != active_id:
            raise ValueError("Decision does not descend from the verified active team")
        if decision["action"] == "promote":
            active_id = decision["candidate_id"]
        if round_info["active_after"] != active_id:
            raise ValueError("Recorded active lineage differs from the gate decision")
        if decision["kind"] == "inference_unavailable":
            attempt = next((entry for entry in state.get("budget_audit", {}).get("entries", []) if entry["id"] == decision.get("failure_request_id")), None)
            if not attempt or attempt["status"] != "unknown_usage" or attempt.get("http_status") != decision.get("error_http_status") or not 400 <= attempt["http_status"] < 600:
                raise ValueError("Provider-stop rollback lacks budgeted HTTP failure evidence")
            if decision["action"] != "rollback" or round_info["selected"] is not None or any(r["node_id"] in round_info["candidates"] and r["evaluation_id"] == evaluation_id for r in state["runs"]):
                raise ValueError("Provider-stop candidate was promoted or executed")
            continue
        if decision["kind"] == "invalid_model_output":
            failure = next((event for event in state["events"] if event.get("request_id") == decision.get("failure_request_id") and event.get("message") == "Inference completed"), None)
            if not failure or decision["action"] != "rollback" or round_info["selected"] is not None:
                raise ValueError("Malformed-output rollback lacks actual inference evidence")
            try:
                json.loads(failure["output"])
            except json.JSONDecodeError:
                if any(r["node_id"] in round_info["candidates"] and r["evaluation_id"] == evaluation_id for r in state["runs"]):
                    raise ValueError("Uncompiled candidate was executed")
                continue
            raise ValueError("Recorded malformed model JSON is actually valid")
        def records(node_id, suite):
            return [r for r in state["runs"] if r["node_id"] == node_id and r["suite"] == suite and r["evaluation_id"] == evaluation_id]
        def score(node_id):
            results = records(node_id, "development")
            return sum(r["passed"] for r in results), -sum(r["metrics"]["work_units"] for r in results), -round_info["candidates"].index(node_id)
        valid_candidates = [node_id for node_id in round_info["candidates"] if nodes[node_id]["status"] != "invalid"]
        if not valid_candidates:
            if decision["kind"] != "invalid_mutations" or decision["action"] != "rollback" or round_info["selected"] is not None:
                raise ValueError("Invalid-mutation rollback mismatch")
            continue
        if max(valid_candidates, key=score) != round_info["selected"]:
            raise ValueError("Development selection mismatch")
        parent, candidate = decision["parent_id"], decision["candidate_id"]
        suite = "validation-g%d" % generation
        promoted, reason, kind = compare(records(parent, "development"), records(candidate, "development"),
                                        records(parent, suite), records(candidate, suite),
                                        records(parent, "regression"), records(candidate, "regression"))
        if (promoted, reason, kind) != (decision["action"] == "promote", decision["reason"], decision["kind"]):
            raise ValueError("Promotion/rollback replay mismatch")
    if len(state["rounds"]) != len(state["decisions"]):
        raise ValueError("Incomplete decision history")
    if state["active_node_id"] != active_id or state.get("active_strategy") != nodes[active_id]["team"]:
        raise ValueError("Restored active configuration differs from verified lineage")
    active_memory = nodes[active_id].get("memory_earned", nodes[active_id]["memory_snapshot"])
    if state.get("memory") != active_memory:
        raise ValueError("Restored active memory differs from verified lineage")
    return {"verified_executions": len(state["runs"]), "verified_decisions": len(state["decisions"]), "verified_nodes": len(nodes),
            "external_api_calls": 0, "note": "Programs, tool traces, work counts, development selection and independent gates reproduced. Wall-clock latency is a historical measurement, not replayed."}
