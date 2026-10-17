"""Objective citation-preflight evolution. Reuses the existing independent gate."""
import copy
import random
import re
from .team import compare, aggregate

BASE_POLICY = {"known_sources": True, "line_bounds": False, "exact_quotes": False,
               "instructions": "Check source identities before handing findings to Engineering"}
STRICT_POLICY = {"known_sources": True, "line_bounds": True, "exact_quotes": True,
                 "instructions": "Verify exact quoted evidence and line bounds before handoff"}


def check_reference(reference, sources, policy=STRICT_POLICY):
    source = next((s for s in sources if s["id"] == reference.get("source_id")), None)
    if source is None:
        return not policy["known_sources"]
    start, end = reference.get("line_start"), reference.get("line_end")
    bounds = type(start) is int and type(end) is int and source["line_start"] <= start <= end <= source["line_end"]
    if policy["line_bounds"] and not bounds:
        return False
    if policy["exact_quotes"]:
        if not bounds or not isinstance(reference.get("quote"), str) or len(reference["quote"].strip()) < 4:
            return False
        lines = source["text"].splitlines()[start - source["line_start"]:end - source["line_start"] + 1]
        normalize = lambda value: re.sub(r"\s+", " ", value).strip()
        return normalize(reference["quote"]) in normalize("\n".join(lines))
    return True


def verify_report(report, snapshot):
    results = []
    for index, finding in enumerate(report.get("priorities", [])):
        citations = finding.get("citations", [])
        checks = [check_reference(ref, snapshot["sources"]) for ref in citations]
        results.append({"priority": index + 1, "passed": bool(checks) and all(checks),
                        "citation_checks": checks, "reason": "Exact source excerpts and line bounds checked; semantic conclusions remain hypotheses"})
    return {"passed": len(results) == 3 and all(r["passed"] for r in results), "priorities": results,
            "valid_priorities": sum(r["passed"] for r in results), "total_priorities": len(results),
            "note": "Checks citation provenance, not whether the recommended priorities are objectively the best."}


def fixtures(seed, split):
    rng = random.Random(str(seed) + split)
    cases = []
    for index in range(6):
        token = "service_%d" % rng.randrange(100000)
        source = {"id": split + "-source", "line_start": 1, "line_end": 3, "text": "export const " + token + " = true;\nconst budget = 42;\n// reviewed source"}
        ref = {"source_id": source["id"], "line_start": 1, "line_end": 1, "quote": "export const " + token + " = true;"}
        expected = index < 3
        if index == 1:
            ref.update(line_start=2, line_end=2, quote="const budget = 42;")
        if index == 2:
            ref.update(line_start=2, line_end=3, quote="const budget = 42;\n// reviewed source")
        if index == 3:
            ref["quote"] = "invented success metric"
        if index == 4:
            ref.update(line_start=12, line_end=13)
        if index == 5:
            ref["source_id"] = "not-retrieved"
        cases.append({"id": split + "-%d" % index, "sources": [source], "reference": ref, "expected": expected})
    return cases


def evaluate(policy, cases):
    return [{"case_id": case["id"], "passed": check_reference(case["reference"], case["sources"], policy) == case["expected"],
             "accepted": check_reference(case["reference"], case["sources"], policy), "expected": case["expected"],
             "metrics": {"tool_calls": 0, "rule_steps": 1, "work_units": 1, "memory_hits": 0, "latency_s": 0}}
            for case in cases]


def evaluate_mutations(parent, mutations, seed):
    suites = {split: fixtures(seed, split) for split in ("development", "heldout", "regression")}
    parent_results = {split: evaluate(parent, cases) for split, cases in suites.items()}
    candidates = []
    for index, mutation in enumerate(mutations):
        policy = mutation["policy"]
        if set(policy) != set(BASE_POLICY) or any(type(policy[key]) is not bool for key in ("known_sources", "line_bounds", "exact_quotes")) or not isinstance(policy["instructions"], str) or len(policy["instructions"]) > 240:
            raise ValueError("Mutation exceeds the bounded preflight configuration")
        candidates.append({"id": "policy-%d" % (index + 1), "name": mutation["name"], "reason": mutation["reason"],
                           "policy": copy.deepcopy(policy), "development": evaluate(policy, suites["development"])})
    winner = max(candidates, key=lambda candidate: (sum(r["passed"] for r in candidate["development"]), -candidates.index(candidate)))
    heldout = evaluate(winner["policy"], suites["heldout"])
    regression = evaluate(winner["policy"], suites["regression"])
    promoted, reason, kind = compare(parent_results["development"], winner["development"], parent_results["heldout"], heldout,
                                     parent_results["regression"], regression)
    winner.update(heldout=heldout, regression=regression)
    return {"benchmark": "citation-preflight-v1", "seed": seed, "parent_policy": parent, "candidates": candidates,
            "parent_results": parent_results, "selected": winner["id"], "action": "promote" if promoted else "rollback",
            "reason": reason, "kind": kind, "active_policy": winner["policy"] if promoted else parent,
            "comparison": {"development": {"parent": aggregate(parent_results["development"]), "candidate": aggregate(winner["development"])},
                           "heldout": {"parent": aggregate(parent_results["heldout"]), "candidate": aggregate(heldout)}},
            "scope": "Improves early citation-error detection on independent deterministic fixtures. Does not establish real-user satisfaction or semantic recommendation quality."}
