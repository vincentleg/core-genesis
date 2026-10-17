"""Capability-limited team execution. Model output is a bounded declarative program.

No eval, exec, generated imports, network access or filesystem actions. Role ownership,
tool grants, workflow order, memory reads, reviews and commits are enforced here.
"""
import copy
import hashlib
import json
import time

from .benchmark import verify
from .suites import family

TOOLS = {"read_logs", "inspect_config", "inspect_contract", "recall_memory"}
ACTIONS = TOOLS | {"apply_rules", "review", "commit"}
FIELDS = {"timeout_ms", "retries", "pool_size", "workers", "health_path", "port"}
OWNERSHIP = {"general": FIELDS, "latency": {"timeout_ms", "retries"}, "capacity": {"pool_size"}, "routing": {"health_path", "port"}, "verifier": set()}
REFERENCES = {"config." + key for key in FIELDS} | {"contract." + key for key in ("upstream_p99_ms", "deadline_ms", "max_retries", "concurrent_queries", "connection_budget", "registered_health_path", "listening_port")}
OPERATIONS = {"copy", "increment", "decrement", "literal"}

CONTROL = {"name": "Log-first control", "instructions": "Infer repairs from symptoms without inspecting deployed configuration or contracts.",
           "agents": [{"id": "executor", "specialty": "general", "tools": ["read_logs"], "instructions": "Propose conservative symptom-based defaults."}],
           "workflow": [{"agent": "executor", "action": action} for action in ("read_logs", "apply_rules", "commit")],
           "review_policy": "schema", "memory_policy": "none", "cache_evidence": False, "program": {"executor": []}}
COORDINATOR = {"id": "controller", "specialty": "verifier", "tools": [],
               "instructions": "Fixed transaction coordinator; review and commit only, no repair writes or evidence capabilities."}


def fingerprint(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def validate_team(raw, program_required=True):
    if not isinstance(raw, dict):
        raise ValueError("Team must be an object")
    result = {}
    for key in ("name", "instructions"):
        value = raw.get(key)
        if not isinstance(value, str) or not 1 <= len(value) <= 1200:
            raise ValueError("Invalid team " + key)
        result[key] = value
    agents = raw.get("agents")
    if not isinstance(agents, list) or not 1 <= len(agents) <= 4:
        raise ValueError("Team requires 1–4 agents")
    result["agents"] = []
    ids = set()
    for agent in agents:
        if not isinstance(agent, dict):
            raise ValueError("Invalid agent")
        agent_id = agent.get("id", "")
        specialty = agent.get("specialty")
        tools = agent.get("tools", [])
        instructions = agent.get("instructions", "")
        if not isinstance(agent_id, str) or not agent_id or len(agent_id) > 32 or not all(c.isalnum() or c == "_" for c in agent_id) or agent_id in ids or agent_id == "controller":
            raise ValueError("Agent IDs must be unique short identifiers")
        if specialty not in OWNERSHIP or not isinstance(tools, list) or len(tools) > 4 or any(t not in TOOLS for t in tools):
            raise ValueError("Unknown specialization or tool")
        if not isinstance(instructions, str) or len(instructions) > 600:
            raise ValueError("Invalid agent instructions")
        ids.add(agent_id)
        result["agents"].append({"id": agent_id, "specialty": specialty, "tools": list(dict.fromkeys(tools)), "instructions": instructions})
    workflow = raw.get("workflow")
    if not isinstance(workflow, list) or not 1 <= len(workflow) <= 24:
        raise ValueError("Workflow requires 1–24 explicit steps")
    result["workflow"] = []
    for step in workflow:
        if not isinstance(step, dict) or step.get("agent") not in ids | {"controller"} or step.get("action") not in ACTIONS:
            raise ValueError("Unknown workflow agent/action")
        owner = COORDINATOR if step["agent"] == "controller" else next(a for a in result["agents"] if a["id"] == step["agent"])
        if step["agent"] == "controller" and step["action"] not in {"review", "commit"}:
            raise ValueError("Fixed controller may only review or commit")
        if step["action"] in TOOLS and step["action"] not in owner["tools"]:
            raise ValueError("Workflow tool exceeds agent capabilities")
        result["workflow"].append({"agent": step["agent"], "action": step["action"]})
    if not any(s["action"] == "commit" for s in workflow) or not any(s["action"] == "apply_rules" for s in workflow):
        raise ValueError("Workflow must apply rules and commit")
    for key, options, default in (("review_policy", {"schema", "contract", "protected_fields"}, "schema"),
                                   ("memory_policy", {"none", "inherit_verified"}, "none")):
        result[key] = raw.get(key, default)
        if result[key] not in options:
            raise ValueError("Invalid " + key)
    result["cache_evidence"] = raw.get("cache_evidence", False)
    if type(result["cache_evidence"]) is not bool:
        raise ValueError("cache_evidence must be boolean")
    result["program"] = validate_program(raw.get("program", {}), result) if program_required else {}
    return result


def assemble_team(raw):
    """Bind safe orchestration shorthand while preserving the capability boundary.

    The immutable controller can transact but cannot write repairs or retrieve evidence.
    A removed generic executor's apply_rules step dispatches the declared specialists;
    it never grants a tool, writes a rule or invents a specialist.
    """
    team = copy.deepcopy(raw)
    notes = []
    agents = team.get("agents", [])
    if not isinstance(agents, list) or any(not isinstance(agent, dict) for agent in agents):
        return validate_team(team, program_required=False), notes
    ids = {agent.get("id") for agent in agents}
    steps = []
    workflow = team.get("workflow", [])
    if not isinstance(workflow, list):
        return validate_team(team, program_required=False), notes
    for step in workflow:
        if isinstance(step, dict) and step.get("agent") == "executor" and "executor" not in ids:
            if step.get("action") in {"review", "commit"}:
                steps.append({"agent": "controller", "action": step["action"]})
                notes.append("Bound removed generic executor's " + step["action"] + " to the fixed transaction controller")
                continue
            if step.get("action") == "apply_rules":
                steps.extend({"agent": agent["id"], "action": "apply_rules"} for agent in agents if agent.get("specialty") != "verifier")
                notes.append("Expanded generic apply_rules into declared specialist dispatch; field ownership remains enforced")
                continue
        steps.append(step)
    team["workflow"] = steps
    return validate_team(team, program_required=False), notes


def validate_program(program, team):
    ids = {agent["id"] for agent in team["agents"]}
    if not isinstance(program, dict) or set(program) - ids:
        raise ValueError("Program refers to unknown agents")
    result = {}
    total = 0
    for agent_id, rules in program.items():
        if not isinstance(rules, list):
            raise ValueError("Agent program must be a list")
        total += len(rules)
        if total > 12:
            raise ValueError("At most 12 repair rules per team")
        result[agent_id] = []
        for rule in rules:
            if not isinstance(rule, dict) or rule.get("target") not in FIELDS or rule.get("operation") not in OPERATIONS:
                raise ValueError("Unknown rule target/operation")
            canonical = {"target": rule["target"], "operation": rule["operation"]}
            if rule["operation"] == "literal":
                value = rule.get("value")
                if type(value) not in (int, str) or isinstance(value, str) and len(value) > 100 or isinstance(value, int) and not 0 <= value <= 100000:
                    raise ValueError("Literal out of bounds")
                canonical["value"] = value
            else:
                if rule.get("source") not in REFERENCES:
                    raise ValueError("Only explicit config/contract references are permitted")
                canonical["source"] = rule["source"]
            result[agent_id].append(canonical)
    return result


def normalize_program(program, team):
    """Normalize two unambiguous JSON representation errors, never invent logic."""
    raw = copy.deepcopy(program)
    notes = []
    if isinstance(raw, dict) and set(raw) == {"agent_id"} and len(team["agents"]) == 1:
        agent_id = team["agents"][0]["id"]
        raw = {agent_id: raw["agent_id"]}
        notes.append("Bound placeholder agent_id to the only declared agent: " + agent_id)
    if isinstance(raw, dict):
        for rules in raw.values():
            if not isinstance(rules, list):
                continue
            for rule in rules:
                if isinstance(rule, dict) and rule.get("operation") == "literal" and "value" not in rule:
                    source = rule.get("source")
                    if isinstance(source, str) and source.isascii() and source.isdigit() and len(source) <= 6:
                        rule["value"] = int(source)
                        rule.pop("source")
                        notes.append("Canonicalized numeric literal source to integer value")
    return validate_program(raw, team), notes


def mutation_diff(parent, candidate):
    changes = []
    labels = {"instructions": "Agent instructions", "agents": "Team composition and specialization", "workflow": "Execution workflow",
              "review_policy": "Verification policy", "memory_policy": "Lessons and memory", "cache_evidence": "Evidence reuse", "program": "Repair procedure"}
    for key, label in labels.items():
        if parent.get(key) != candidate.get(key):
            changes.append({"field": key, "label": label, "before": parent.get(key), "after": candidate.get(key)})
    return changes


def _review(case, board, patch, policy):
    config = board.get("config", {})
    if set(patch) - set(case.config) or any(type(value) is not type(case.config[key]) for key, value in patch.items()):
        return False, "Schema/type violation"
    if policy == "protected_fields" and "workers" in patch and ("workers" not in config or patch["workers"] != config["workers"]):
        return False, "Worker configuration is protected"
    if policy == "contract":
        # This review may use only retrieved evidence, never the evaluator's hidden fixture.
        contract = board.get("contract")
        if not contract or not config:
            return False, "Review blocked: config/contract evidence missing"
        proposed = {**config, **patch}
        if "timeout_ms" in proposed:
            good = contract["upstream_p99_ms"] < proposed["timeout_ms"] <= contract["deadline_ms"] and 0 <= proposed["retries"] <= contract["max_retries"]
        elif "pool_size" in proposed:
            good = contract["concurrent_queries"] <= proposed["pool_size"] <= contract["connection_budget"] and proposed["workers"] == config["workers"]
        else:
            good = proposed["health_path"] == contract["registered_health_path"] and proposed["port"] == contract["listening_port"]
        return good, "Contract review passed" if good else "Contract review rejected the proposed transaction"
    return True, "Schema review passed"


def execute(team, case, memory=()):
    start = time.perf_counter()
    board, staged, committed, trace = {}, {}, {}, []
    agents = {a["id"]: a for a in team["agents"]}
    agents["controller"] = COORDINATOR
    executed_tools = rule_steps = memory_hits = 0
    rejected = False
    for index, step in enumerate(team["workflow"]):
        agent, action = agents[step["agent"]], step["action"]
        entry = {"step": index, "agent": agent["id"], "specialty": agent["specialty"], "action": action, "kind": "local_tool", "status": "complete"}
        if action in TOOLS:
            board_key = {"read_logs": "logs", "inspect_config": "config", "inspect_contract": "contract", "recall_memory": "memory"}[action]
            if team["cache_evidence"] and board_key in board:
                entry.update(kind="cache_hit", detail="Previously gathered evidence reused")
            else:
                executed_tools += 1
                if action == "read_logs":
                    board[board_key] = case.logs
                elif action == "inspect_config":
                    board[board_key] = dict(case.config)
                elif action == "inspect_contract":
                    board[board_key] = dict(case.contract)
                else:
                    board[board_key] = [copy.deepcopy(m) for m in memory if m.get("family") == family(case) and m.get("status") == "development_verified"] if team["memory_policy"] == "inherit_verified" else []
                    memory_hits += len(board[board_key])
                entry["evidence"] = copy.deepcopy(board[board_key])
        elif action == "apply_rules":
            rules = list(team["program"].get(agent["id"], []))
            if team["memory_policy"] == "inherit_verified":
                for lesson in board.get("memory", []):
                    rules.extend(lesson.get("rules", []))
            applied = []
            for rule in rules[:24]:
                target = rule["target"]
                if target not in case.config:
                    continue
                rule_steps += 1
                if target not in OWNERSHIP[agent["specialty"]]:
                    applied.append({"target": target, "status": "denied", "reason": "Specialization does not own this field"})
                    continue
                if rule["operation"] == "literal":
                    value = rule["value"]
                else:
                    namespace, key = rule["source"].split(".", 1)
                    if key not in board.get(namespace, {}):
                        applied.append({"target": target, "status": "blocked", "reason": "Required evidence has not been retrieved"})
                        continue
                    value = board[namespace][key]
                    if rule["operation"] in ("increment", "decrement"):
                        if type(value) is not int:
                            applied.append({"target": target, "status": "denied", "reason": "Arithmetic requires an integer"})
                            continue
                        value += 1 if rule["operation"] == "increment" else -1
                if type(value) is not type(case.config[target]):
                    applied.append({"target": target, "status": "denied", "reason": "Result type mismatch"})
                    continue
                staged[target] = value
                applied.append({"target": target, "status": "applied", "value": value, "rule": rule})
            entry["operations"] = applied
        elif action == "review":
            good, detail = _review(case, board, staged, team["review_policy"])
            entry.update(status="passed" if good else "rejected", detail=detail)
            rejected = not good
        elif action == "commit":
            # Every commit receives a real review, even if the workflow omitted one.
            good, detail = _review(case, board, staged, team["review_policy"])
            if not rejected and good:
                committed.update(staged)
                entry["patch"] = dict(staged)
            else:
                entry.update(status="rejected", detail=detail)
        trace.append(entry)
    outcome = verify(case, committed)
    return {"case_id": case.id, "title": case.title, "family": family(case), "split": case.split, "passed": outcome["passed"],
            "patch": committed, "verification": outcome, "trace": trace,
            "metrics": {"tool_calls": executed_tools, "rule_steps": rule_steps, "workflow_steps": len(trace),
                        "work_units": executed_tools + rule_steps + sum(t["action"] in {"apply_rules", "review", "commit"} for t in trace),
                        "memory_hits": memory_hits, "latency_s": round(time.perf_counter() - start, 6)},
            "provenance": "Executed by the bounded local team interpreter; model-generated program, no per-incident inference or simulated API response"}


def aggregate(records):
    total = len(records)
    return {"passed": sum(r["passed"] for r in records), "total": total, "pass_rate": sum(r["passed"] for r in records) / total if total else None,
            **{key: sum(r["metrics"][key] for r in records) for key in ("tool_calls", "rule_steps", "work_units", "memory_hits", "latency_s")}}


def compare(parent_dev, candidate_dev, parent_validation, candidate_validation, parent_regression, candidate_regression):
    pairs = ((parent_dev, candidate_dev), (parent_validation, candidate_validation), (parent_regression, candidate_regression))
    for before, after in pairs:
        if not before or len(before) != len(after) or len({r["case_id"] for r in before}) != len(before) or {r["case_id"] for r in before} != {r["case_id"] for r in after}:
            return False, "Incomplete or mismatched independent evaluation", "incomplete"
        old = {r["case_id"]: r for r in before}
        if any(old[r["case_id"]]["passed"] and not r["passed"] for r in after):
            return False, "Previously passing case regressed; automatic rollback", "regression"
    pd, cd, pv, cv = map(aggregate, (parent_dev, candidate_dev, parent_validation, candidate_validation))
    if cd["passed"] > pd["passed"] and cv["passed"] > pv["passed"]:
        return True, "Strict success gains on development and fresh held-out cases; no regressions", "success_gain"
    if cd["passed"] == pd["passed"] and cv["passed"] == pv["passed"] and cv["passed"] == cv["total"] and cd["passed"] == cd["total"]:
        if cd["work_units"] < pd["work_units"] and cv["work_units"] < pv["work_units"]:
            return True, "All development and held-out cases pass with strictly less executed work; no regressions", "efficiency_gain"
    return False, "No independent success gain or fully correct efficiency gain; baseline retained", "no_gain"
