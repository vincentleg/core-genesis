"""Typed team-assembly operators selected by the Scientist, expanded by the runtime."""
from .team import validate_team, OWNERSHIP, TOOLS

STYLES = {"shared_evidence", "specialist_pipeline", "memory_first"}


def assemble_design(parent, design, name, memory=()):
    if not isinstance(design, dict) or set(design) - {"instructions", "workers", "coordination", "review_policy", "memory_policy", "cache_evidence", "extra_review", "procedure_source"}:
        raise ValueError("Unknown team design field")
    workers = design.get("workers")
    if not isinstance(workers, list) or not 1 <= len(workers) <= 4:
        raise ValueError("Design requires 1–4 workers")
    style = design.get("coordination", "shared_evidence")
    if style not in STYLES:
        raise ValueError("Unknown coordination operator")
    procedure_source = design.get("procedure_source", "compile")
    if procedure_source not in {"compile", "reuse_memory"}:
        raise ValueError("Unknown procedure source")
    if procedure_source == "reuse_memory" and {entry.get("family") for entry in memory if entry.get("status") == "development_verified" and entry.get("rules")} != {"latency", "capacity", "routing"}:
        raise ValueError("Compiler-free reuse requires verified rule coverage for all three incident families")
    if type(design.get("extra_review", False)) is not bool:
        raise ValueError("extra_review must be boolean")
    agents = []
    specialties = set()
    for worker in workers:
        if not isinstance(worker, dict) or worker.get("specialty") not in OWNERSHIP:
            raise ValueError("Unknown worker specialization")
        specialty = worker["specialty"]
        if specialty in specialties:
            raise ValueError("Duplicate worker specialty")
        specialties.add(specialty)
        tools = worker.get("tools", [])
        if not isinstance(tools, list) or any(tool not in TOOLS for tool in tools):
            raise ValueError("Unknown worker capability")
        agents.append({"id": "executor" if specialty == "general" else specialty, "specialty": specialty,
                       "tools": list(dict.fromkeys(tools)), "instructions": worker.get("instructions", "")})
    if specialties == {"verifier"}:
        raise ValueError("A team needs a repair worker")
    memory_policy = design.get("memory_policy", parent.get("memory_policy", "none"))
    if style == "memory_first" or procedure_source == "reuse_memory":
        memory_policy = "inherit_verified"
        if "recall_memory" not in agents[0]["tools"]:
            agents[0]["tools"].append("recall_memory")
    workflow = []
    if style in {"shared_evidence", "memory_first"}:
        gathered = set()
        if style == "memory_first":
            workflow.append({"agent": agents[0]["id"], "action": "recall_memory"})
            gathered.add("recall_memory")
        for agent in agents:
            for tool in agent["tools"]:
                if tool not in gathered:
                    workflow.append({"agent": agent["id"], "action": tool})
                    gathered.add(tool)
        workflow.extend({"agent": agent["id"], "action": "apply_rules"} for agent in agents if agent["specialty"] != "verifier")
    else:
        for agent in agents:
            workflow.extend({"agent": agent["id"], "action": tool} for tool in agent["tools"])
            if agent["specialty"] != "verifier":
                workflow.append({"agent": agent["id"], "action": "apply_rules"})
    if design.get("extra_review", False):
        workflow.append({"agent": "controller", "action": "review"})
    workflow.append({"agent": "controller", "action": "commit"})
    team = {"name": name, "instructions": design.get("instructions", parent["instructions"]), "agents": agents, "workflow": workflow,
            "review_policy": design.get("review_policy", parent["review_policy"]), "memory_policy": memory_policy,
            "cache_evidence": design.get("cache_evidence", False), "program": {}}
    return validate_team(team, program_required=False), ["Assembled explicit workflow from Scientist-selected " + style + " operator"], procedure_source
