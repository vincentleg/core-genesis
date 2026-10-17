"""Deterministic incident simulators. Model output is data, never executable code."""
from dataclasses import dataclass
from typing import Any

SUITE_VERSION = "incidents-v1"


@dataclass(frozen=True)
class Incident:
    id: str
    split: str
    title: str
    logs: str
    config: dict
    contract: dict

    def context(self, tools):
        result = {"id": self.id, "title": self.title, "logs": self.logs,
                  "config_schema": {key: type(value).__name__ for key, value in self.config.items()}}
        if "inspect_config" in tools:
            result["config"] = dict(self.config)
        if "inspect_contract" in tools:
            result["service_contract"] = dict(self.contract)
        return result


CASES = (
    Incident("dev-timeout", "development", "Gateway drops valid requests",
             "504 upstream timeout; upstream completes normally. Retry storms observed.",
             {"timeout_ms": 80, "retries": 3},
             {"upstream_p99_ms": 240, "deadline_ms": 400, "max_retries": 1}),
    Incident("dev-pool", "development", "Database queue saturation",
             "Pool acquisition timed out under steady traffic. Database is healthy.",
             {"pool_size": 2, "workers": 12},
             {"concurrent_queries": 8, "connection_budget": 10}),
    Incident("dev-route", "development", "Health checks fail after migration",
             "GET /health => 404; service process is running. Load balancer marks backend down.",
             {"health_path": "/health", "port": 8080},
             {"registered_health_path": "/readyz", "listening_port": 8080}),
    Incident("eval-timeout", "held_out", "Report service intermittent 504s",
             "Upstream jobs finish successfully, but gateway abandons responses. Retries amplify load.",
             {"timeout_ms": 150, "retries": 4},
             {"upstream_p99_ms": 650, "deadline_ms": 900, "max_retries": 0}),
    Incident("eval-pool", "held_out", "Worker service cannot acquire connections",
             "Database ping succeeds; connection acquisition exceeds deadline during peak load.",
             {"pool_size": 4, "workers": 20},
             {"concurrent_queries": 15, "connection_budget": 18}),
    Incident("eval-route", "held_out", "New deployment never becomes ready",
             "Readiness requests return 404. Application listener started successfully.",
             {"health_path": "/status", "port": 3000},
             {"registered_health_path": "/live", "listening_port": 9090}),
)


def verify(case: Incident, patch: Any) -> dict:
    """Apply an allowlisted patch to a fresh fixture, then run behavioral assertions."""
    if not isinstance(patch, dict) or not patch or set(patch) - set(case.config):
        return {"passed": False, "checks": {"valid_patch": False}, "error": "Patch must contain only existing configuration keys"}
    if any(type(value) is not type(case.config[key]) for key, value in patch.items()):
        return {"passed": False, "checks": {"valid_patch": False}, "error": "Configuration type mismatch"}
    config = {**case.config, **patch}
    c = case.contract
    if "timeout_ms" in config:
        checks = {"request_completes": c["upstream_p99_ms"] < config["timeout_ms"] <= c["deadline_ms"],
                  "retry_budget": 0 <= config["retries"] <= c["max_retries"]}
    elif "pool_size" in config:
        checks = {"load_served": c["concurrent_queries"] <= config["pool_size"] <= c["connection_budget"],
                  "workers_preserved": config["workers"] == case.config["workers"]}
    else:
        checks = {"probe_reaches_route": config["health_path"] == c["registered_health_path"],
                  "probe_reaches_listener": config["port"] == c["listening_port"]}
    return {"passed": all(checks.values()), "checks": checks, "resulting_config": config}
