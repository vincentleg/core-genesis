"""Reproducible, disjoint incident suites for multi-generation experiments."""
import hashlib
import json
import random

from .benchmark import Incident, CASES

VERSION = "incidents-v2-fresh-shards"
FAMILIES = ("latency", "capacity", "routing")


def family(case):
    return "latency" if "timeout_ms" in case.config else "capacity" if "pool_size" in case.config else "routing"


def generate(seed, shard, count=6):
    """Each shard has independent parameters; the saved seed exactly reproduces it."""
    digest = hashlib.sha256((str(seed) + ":" + shard).encode()).hexdigest()
    rng = random.Random(int(digest, 16))
    cases = []
    for i in range(count):
        kind = FAMILIES[i % len(FAMILIES)]
        case_id = "%s-%s-%02d" % (shard, kind, i)
        if kind == "latency":
            p99 = rng.randint(140, 1600)
            config = {"timeout_ms": rng.randint(10, p99 - 1), "retries": rng.randint(2, 6)}
            contract = {"upstream_p99_ms": p99, "deadline_ms": p99 + rng.randint(40, 500), "max_retries": rng.randint(0, 1)}
            logs = "Gateway 504; upstream completes normally; retry amplification observed."
        elif kind == "capacity":
            demand = rng.randint(5, 36)
            config = {"pool_size": rng.randint(1, demand - 1), "workers": demand + rng.randint(2, 12)}
            contract = {"concurrent_queries": demand, "connection_budget": demand + rng.randint(1, 7)}
            logs = "Connection acquisition deadline exceeded under load; database remains healthy."
        else:
            token = "%08x" % rng.getrandbits(32)
            config = {"health_path": "/old/" + token, "port": rng.choice([3000, 8080, 8000])}
            contract = {"registered_health_path": "/ready/" + token, "listening_port": rng.choice([9090, 9001, 5000])}
            logs = "Readiness returns 404; application listener is running after migration."
        split = "development" if shard == "development" else "held_out"
        cases.append(Incident(case_id, split, kind.capitalize() + " contract incident", logs, config, contract))
    return tuple(cases)


def manifest(seed, generations=3):
    suites = {"development": generate(1729, "development"), "regression": tuple(CASES)}
    for generation in range(1, generations + 1):
        suites["validation-g%d" % generation] = generate(seed, "validation-g%d" % generation)
    suites["sealed"] = generate(seed, "sealed")
    identity = {key: [case.__dict__ for case in value] for key, value in suites.items()}
    return suites, {"version": VERSION, "seed": str(seed), "sha256": hashlib.sha256(json.dumps(identity, sort_keys=True).encode()).hexdigest(),
                    "suites": {key: [case.id for case in value] for key, value in suites.items()},
                    "note": "Fresh validation shard per generation; sealed challenge never enters synthesis prompts. Development is fixed for fair iteration."}
