"""Reproduce mission citation and evolution checks without any network access."""
import json
from .mission_eval import verify_report, evaluate_mutations, check_reference


def replay_mission(state):
    if "mission" in state:
        state = state["mission"]
    checked = 0
    if state.get("verification"):
        actual = verify_report(state["artifacts"]["engineering"], state["snapshot"])
        if actual != state["verification"]:
            raise ValueError("Mission citation verification differs from source evidence")
        checked = actual["total_priorities"]
    if state.get('preflight'):
        expected = [{'priority': i + 1, 'accepted': bool(p.get('citations')) and all(check_reference(ref, state['snapshot']['sources'], state['configuration']['policy']) for ref in p.get('citations', []))} for i, p in enumerate(state['artifacts']['research']['priorities'])]
        if expected != state['preflight']:
            raise ValueError('Active preflight policy was not applied as recorded')
    evolution = state.get("evolution")
    if evolution:
        mutations = [{"name": c["name"], "reason": c["reason"], "policy": c["policy"]} for c in evolution["candidates"]]
        actual = evaluate_mutations(evolution["parent_policy"], mutations, evolution["seed"])
        for key in actual:
            if actual[key] != evolution[key]:
                raise ValueError("Independent mission evolution replay mismatch: " + key)
        inference = next((event for event in state["events"] if event["agent"] == "Scientist" and event["message"] == "Nemotron result recorded"), None)
        if not inference or json.loads(inference["output"])["mutations"] != mutations:
            raise ValueError("Mutations do not match actual recorded Scientist output")
    entries = {entry["id"]: entry for entry in state.get("usage", {}).get("entries", [])}
    model_events = [event for event in state["events"] if event["message"] == "Nemotron result recorded"]
    for event in model_events:
        entry = entries.get(event["request_id"])
        if not entry or entry.get("usage") != event["usage"] or entry["role"] != event["agent"]:
            raise ValueError("Reasoning event differs from the request ledger")
    for artifact, agent in (("research", "Research Lead"), ("engineering", "Engineering Lead")):
        if artifact in state.get("artifacts", {}):
            recorded = [e for e in model_events if e["agent"] == agent]
            if not recorded or json.loads(recorded[-1]["output"]) != state["artifacts"][artifact]:
                raise ValueError("Deliverable differs from actual recorded " + agent + " output")
    prototype = state.get('artifacts', {}).get('prototype')
    if prototype:
        from .artifact_builder import validate_spec
        design = next((e for e in model_events if e['agent'] == 'Implementation Designer'), None)
        if not design or json.loads(design['output']) != state['artifacts']['implementation_spec'] or validate_spec(state['artifacts']['implementation_spec'], [s['id'] for s in state['snapshot']['sources']]) != prototype['spec']:
            raise ValueError('Artifact specification differs from actual Nemotron design')
        report = prototype['test_report']
        if json.loads(report['stdout']) != report['outcome'] or report['passed'] != (report['exit_code'] == 0 and report['outcome']['passed']):
            raise ValueError('Artifact outcome differs from captured test process')
    if "engineering_initial" in state.get("artifacts", {}):
        first = next(e for e in model_events if e["agent"] == "Engineering Lead")
        if json.loads(first["output"]) != state["artifacts"]["engineering_initial"] or verify_report(state["artifacts"]["engineering_initial"], state["snapshot"]) != state["initial_verification"]:
            raise ValueError("Initial rejected plan or its verification differs from recorded evidence")
    if len({p["persona"]["id"] for p in state.get("panel", [])}) != len(state.get("panel", [])):
        raise ValueError("Duplicate synthetic persona")
    for review in state.get("panel", []):
        event = next((event for event in model_events if event["agent"] == "Synthetic " + review["persona"]["name"]), None)
        if not event or json.loads(event["output"]) != review["response"]:
            raise ValueError("Synthetic response differs from actual recorded independent call")
        if "panel" in event["input_context"]["data"]:
            raise ValueError("Persona context contains other persona responses")
    return {"verified_priority_citation_sets": checked, "verified_independent_persona_calls": len(state.get("panel", [])),
            "verified_reasoning_records": len(model_events), "verified_mutation_gates": int(bool(evolution)), "verified_artifact_reports": int(bool(prototype)), "external_api_calls": 0,
            "scope": "Citation provenance, independent synthetic contexts, request accounting and deterministic promotion are reproduced. Semantic recommendation quality and real-user outcomes are not proven."}
