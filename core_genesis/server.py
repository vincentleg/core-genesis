"""Local-only Arena server. No dependencies, shell execution, or public mutations."""
import argparse
import json
import os
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

from .engine import ROOT
from .evolution import EvolutionEngine, DEFAULT_OBJECTIVE
from .budget import BudgetError
from .local_test import run_checks
from .company import Company, Paused
from .testing_lab import BrowserLab
from .audience import AudiencePanel


def serve(host="127.0.0.1", port=8080, fresh=False):
    engine = EvolutionEngine(fresh=fresh)
    company = Company(budget=engine.budget)
    browser_lab = BrowserLab(company)
    audience = AudiencePanel(company)
    prototype_apps = {}
    prototype_lock = threading.Lock()
    def prototype(identity):
        from .artifact_builder import run_directory
        from .scaffolds.local_solutions.app import Application
        directory = run_directory(identity)
        if not json.loads((directory / 'build-report.json').read_text()).get('passed'):
            raise ValueError('Prototype has not passed Operations verification')
        with prototype_lock:
            if identity not in prototype_apps:
                prototype_apps[identity] = Application(directory)
            return prototype_apps[identity]
    local_report = {"mode": "local", "status": "idle", "external_api_calls": 0}
    local_lock = threading.Lock()
    histories = sorted(engine.directory.glob("*.json"))
    if histories:
        try:
            engine.state = json.loads(histories[-1].read_text())
            if engine.state.get("status") == "running":
                engine.state["status"] = "interrupted"
        except (ValueError, OSError):
            pass

    class Handler(BaseHTTPRequestHandler):
        def send(self, status, data, kind="application/json"):
            body = json.dumps(data).encode() if kind == "application/json" else data
            self.send_response(status)
            self.send_header("Content-Type", kind)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Content-Security-Policy", "default-src 'self'; style-src 'self' 'unsafe-inline'; script-src 'self'; connect-src 'self'; img-src 'self' data:; frame-ancestors 'none'")
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            path = urlparse(self.path).path
            if path == '/api/company/testing':
                return self.send(200, {'browser': browser_lab.snapshot(), 'audience': audience.snapshot()})
            if path.startswith('/testing-evidence/'):
                parts = path.split('/')
                if len(parts) != 5 or not parts[2].startswith('browser-') or any(c not in 'browser-0123456789abcdef' for c in parts[2]) or parts[3] not in {'before', 'reproduce', 'after'} or parts[4] not in {'report.json', 'resident.png', 'mobile.png', 'safety.png'}:
                    return self.send(404, {'error': 'Unknown testing evidence'})
                file = browser_lab.directory / parts[2] / parts[3] / parts[4]
                if file.is_file():
                    return self.send(200, json.loads(file.read_text())) if file.suffix == '.json' else self.send(200, file.read_bytes(), 'image/png')
                return self.send(404, {'error': 'Evidence not captured'})
            if path.startswith('/prototype/'):
                from .artifact_builder import run_directory
                from .scaffolds.local_solutions.app import Application, dispatch
                parts = path.split('/')
                try:
                    directory = run_directory(parts[2])
                    if not (directory / 'build-report.json').is_file() or not json.loads((directory / 'build-report.json').read_text()).get('passed'):
                        raise ValueError('Prototype has not passed Operations verification')
                    return dispatch(self, prototype(parts[2]), '/prototype/' + parts[2])
                except (ValueError, OSError, IndexError) as exc:
                    return self.send(404, {'error': str(exc)})
            if path.startswith('/artifact/'):
                from .artifact_builder import run_directory, FILES
                parts = path.split('/')
                try:
                    if len(parts) != 4 or parts[3] not in {*FILES, 'spec.json', 'research-brief.json', 'manifest.json', 'build-report.json', 'failed-build-report.json'}:
                        raise ValueError('Unknown artifact file')
                    file = run_directory(parts[2]) / parts[3]
                    return self.send(200, json.loads(file.read_text())) if file.suffix == '.json' else self.send(200, file.read_bytes(), 'text/plain; charset=utf-8')
                except (ValueError, OSError) as exc:
                    return self.send(404, {'error': str(exc)})
            if path in {"/hq-status.json", "/api/hq/status"}:
                from .hq_status import hq_status
                return self.send(200, hq_status())
            if path == "/api/company":
                return self.send(200, {"mission": company.snapshot(), "governance": company.governance()})
            if path == "/api/company/history":
                return self.send(200, [{"id": p.stem} for p in sorted(company.missions.glob("*.json"), reverse=True)])
            if path.startswith("/api/company/mission/"):
                name = path.rsplit("/", 1)[-1]
                suffix = ".md" if name.endswith(".md") else ".json"
                identity = name[:-3] if suffix == ".md" else name
                if not identity.startswith("mission-") or any(c not in "mission-0123456789abcdef" for c in identity):
                    return self.send(400, {"error": "Invalid mission identity"})
                file = company.missions / (identity + suffix)
                if file.is_file():
                    return self.send(200, file.read_bytes(), "text/markdown; charset=utf-8") if suffix == ".md" else self.send(200, json.loads(file.read_text()))
                return self.send(404, {"error": "Mission not found"})
            if path == "/capabilities.json":
                return self.send(200, {"live": True, "company": True, "paid_inference_enabled": os.environ.get("CORE_HQ_ALLOW_PAID_INFERENCE") == "approved", "mode": "local_read_only", "note": "Paid inference disabled by default. Use CORE HQ status and the local CORE browser harness."})
            if path in {"/evidence/story.json", "/evidence/continuation.json", "/evidence/verified.json", "/evidence/manifest.json", "/evidence/company-mission.json"}:
                file = ROOT / "public" / path.lstrip("/")
                if file.is_file():
                    return self.send(200, json.loads(file.read_text()))
                return self.send(404, {"error": "Build the static evidence with python3 scripts/build_world.py"})
            if path == "/api/state":
                return self.send(200, engine.snapshot())
            if path == "/api/recorded":
                for file in sorted(engine.directory.glob("*.json"), reverse=True):
                    record = json.loads(file.read_text())
                    if record.get("status") == "complete":
                        return self.send(200, record)
                return self.send(200, {"status": "idle", "events": [], "runs": [], "strategies": [], "mode": "recorded"})
            if path == "/api/budget":
                try:
                    return self.send(200, engine.budget.snapshot())
                except BudgetError as exc:
                    return self.send(200, {"status": "locked", "reason": str(exc), "cap_usd": "2.00"})
            if path == "/api/local-test":
                with local_lock:
                    return self.send(200, dict(local_report))
            if path == "/api/history":
                return self.send(200, [{"id": p.stem} for p in sorted(engine.directory.glob("*.json"), reverse=True)])
            if path.startswith("/api/experiments/"):
                name = path.rsplit("/", 1)[-1]
                if not name or any(c not in "0123456789-abcdef" for c in name):
                    return self.send(400, {"error": "Invalid experiment ID"})
                file = engine.directory / (name + ".json")
                if file.is_file():
                    return self.send(200, json.loads(file.read_text()))
                return self.send(404, {"error": "Unknown experiment"})
            assets = {"/hq.html": ("hq.html", "text/html; charset=utf-8"),
                      "/hq.js": ("hq.js", "text/javascript; charset=utf-8"), "/hq.css": ("hq.css", "text/css; charset=utf-8"),
                      "/genesis-run.js": ("genesis-run.js", "text/javascript; charset=utf-8"), "/genesis.css": ("genesis.css", "text/css; charset=utf-8"),
                      "/": ("world.html", "text/html; charset=utf-8"), "/arena": ("arena.html", "text/html; charset=utf-8"),
                      "/world.js": ("world.js", "text/javascript; charset=utf-8"), "/world.css": ("world.css", "text/css; charset=utf-8"),
                      "/campus.js": ("campus.js", "text/javascript; charset=utf-8"), "/economy.js": ("economy.js", "text/javascript; charset=utf-8"),
                      "/company-ui.js": ("company-ui.js", "text/javascript; charset=utf-8"),
                      "/testing-ui.js": ("testing-ui.js", "text/javascript; charset=utf-8"),
                      "/company.css": ("company.css", "text/css; charset=utf-8"),
                      "/vendor/three.module.js": ("vendor/three.module.js", "text/javascript; charset=utf-8"), "/vendor/three.core.min.js": ("vendor/three.core.min.js", "text/javascript; charset=utf-8"),
                      "/arena.js": ("arena.js", "text/javascript; charset=utf-8"), "/arena.css": ("arena.css", "text/css; charset=utf-8"),
                      "/app.js": ("app.js", "text/javascript; charset=utf-8"), "/style.css": ("style.css", "text/css; charset=utf-8")}
            if path in assets:
                name, mime = assets[path]
                return self.send(200, (ROOT / "web" / name).read_bytes(), mime)
            self.send(404, {"error": "Not found"})

        def do_POST(self):
            if urlparse(self.path).path.startswith('/prototype/'):
                from .artifact_builder import run_directory
                from .scaffolds.local_solutions.app import Application, dispatch
                parts = urlparse(self.path).path.split('/')
                try:
                    directory = run_directory(parts[2])
                    if not json.loads((directory / 'build-report.json').read_text()).get('passed'):
                        raise ValueError('Unverified prototype')
                    return dispatch(self, prototype(parts[2]), '/prototype/' + parts[2])
                except (ValueError, OSError, IndexError) as exc:
                    return self.send(404, {'error': str(exc)})
            # Reject cross-origin forms and DNS rebinding before any credit-spending action.
            expected = {"127.0.0.1:" + str(port), "localhost:" + str(port)}
            if self.headers.get("Host") not in expected:
                return self.send(403, {"error": "Local host required"})
            origin = self.headers.get("Origin")
            if origin and origin not in {"http://" + host for host in expected}:
                return self.send(403, {"error": "Same origin required"})
            if self.headers.get("X-Genesis-Action") not in {"evolve", "local-test", "mission", "ceo", "testing"}:
                return self.send(403, {"error": "Explicit action header required"})
            if self.path in {'/api/evolve', '/api/company/mission', '/api/company/testing/batch'} and os.environ.get('CORE_HQ_ALLOW_PAID_INFERENCE') != 'approved':
                return self.send(403, {'error': 'Paid inference disabled; explicit founder approval required. The CORE HQ local browser harness uses no paid APIs.'})
            if self.path in {'/api/company/testing/browser', '/api/company/testing/audience', '/api/company/testing/batch'}:
                if self.headers.get('X-Genesis-Action') != 'testing':
                    return self.send(403, {'error': 'Explicit testing action required'})
                try:
                    if engine.snapshot().get('status') == 'running' or browser_lab.snapshot().get('status') == 'running' or audience.snapshot().get('status') == 'running':
                        raise ValueError('Wait for active work to finish')
                    length = int(self.headers.get('Content-Length', '0'))
                    if not 1 <= length <= 1024:
                        raise ValueError('Bounded request required')
                    data = json.loads(self.rfile.read(length))
                    if not isinstance(data, dict) or set(data) - {'target'}:
                        raise ValueError('Unknown testing fields')
                    if self.path.endswith('/browser'):
                        result = browser_lab.start()
                        threading.Thread(target=browser_lab.run, daemon=True).start()
                    elif self.path.endswith('/audience'):
                        result = audience.create(data.get('target', 100))
                    else:
                        result = audience.prepare_batch()
                        threading.Thread(target=audience.run_batch, daemon=True).start()
                    return self.send(202, result)
                except (ValueError, TypeError, BudgetError, Paused) as exc:
                    return self.send(400, {'error': str(exc)})
            if self.path in {"/api/company/mission", "/api/company/control"}:
                expected_action = "mission" if self.path.endswith("/mission") else "ceo"
                if self.headers.get("X-Genesis-Action") != expected_action:
                    return self.send(403, {"error": "Explicit CEO or mission action required"})
                try:
                    length = int(self.headers.get("Content-Length", "0"))
                    if not 1 <= length <= 4096:
                        raise ValueError("Invalid request size")
                    data = json.loads(self.rfile.read(length))
                    if not isinstance(data, dict):
                        raise ValueError("Request must be an object")
                    allowed = {"objective"} if self.path.endswith("/mission") else {"action", "decision_id"}
                    if set(data) - allowed:
                        raise ValueError("Unknown company request fields")
                    if self.path.endswith("/control"):
                        return self.send(200, company.control(data.get("action"), data.get("decision_id")))
                    if engine.snapshot().get("status") == "running":
                        raise ValueError("An evolution experiment is already active")
                    if browser_lab.snapshot().get('status') == 'running' or audience.snapshot().get('status') == 'running':
                        raise ValueError('Product Testing work is active')
                    result = company.start(data.get("objective"))
                    threading.Thread(target=company.run, daemon=True).start()
                    return self.send(202, {"id": result["id"]})
                except (ValueError, TypeError, Paused, BudgetError) as exc:
                    return self.send(400, {"error": str(exc)})
            if self.path == "/api/local-test":
                if self.headers.get("X-Genesis-Action") != "local-test":
                    return self.send(403, {"error": "Local test action required"})
                with local_lock:
                    if local_report["status"] == "running":
                        return self.send(409, {"error": "Local checks already running"})
                    local_report.clear()
                    local_report.update({"mode": "local", "status": "running", "external_api_calls": 0})
                def worker():
                    try:
                        report = run_checks()
                    except Exception as exc:
                        report = {"mode": "local", "status": "error", "external_api_calls": 0, "error": type(exc).__name__}
                    with local_lock:
                        local_report.clear()
                        local_report.update(report)
                threading.Thread(target=worker, daemon=True).start()
                return self.send(202, {"mode": "local", "status": "running"})
            if self.path != "/api/evolve":
                return self.send(404, {"error": "Not found"})
            if self.headers.get("X-Genesis-Action") != "evolve":
                return self.send(403, {"error": "Live evolution action required"})
            try:
                company.guard()
                if company.snapshot().get("status") == "running":
                    raise ValueError("A company mission is already active")
                length = int(self.headers.get("Content-Length", "0"))
                if not 0 <= length <= 4096:
                    return self.send(413, {"error": "Objective request too large"})
                options = json.loads(self.rfile.read(length)) if length else {}
                if not isinstance(options, dict) or set(options) - {"objective", "generations", "seed"}:
                    return self.send(400, {"error": "Only objective, generations and seed may be provided"})
                if not engine.start(objective=options.get("objective", DEFAULT_OBJECTIVE), generations=options.get("generations", 3), seed=options.get("seed")):
                    return self.send(409, {"error": "Experiment already running"})
            except BudgetError as exc:
                return self.send(503, {"error": str(exc)})
            except (ValueError, TypeError, Paused) as exc:
                return self.send(400, {"error": str(exc)})
            threading.Thread(target=engine.run, daemon=True).start()
            self.send(202, {"id": engine.snapshot()["id"]})

        def log_message(self, *args):
            pass

    server = ThreadingHTTPServer((host, port), Handler)
    print("CORE HQ · Living Company → http://%s:%s · Technical Arena /arena" % (host, port), flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CORE HQ local Evolution Arena")
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--host", choices=["127.0.0.1", "0.0.0.0"], default="127.0.0.1")
    parser.add_argument("--fresh", action="store_true", help="Run reproducible baseline experiments instead of continuing the last verified team")
    args = parser.parse_args()
    serve(host=args.host, port=args.port, fresh=args.fresh)
