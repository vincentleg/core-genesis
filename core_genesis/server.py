"""Local-only Arena server. No dependencies, shell execution, or public mutations."""
import argparse
import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

from .engine import ROOT
from .evolution import EvolutionEngine, DEFAULT_OBJECTIVE
from .budget import BudgetError
from .local_test import run_checks


def serve(host="127.0.0.1", port=8080, fresh=False):
    engine = EvolutionEngine(fresh=fresh)
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
            if path == "/capabilities.json":
                return self.send(200, {"live": True, "mode": "local_budgeted_live", "note": "Inference requires an explicit user action; existing budget limits apply."})
            if path in {"/evidence/story.json", "/evidence/continuation.json", "/evidence/verified.json", "/evidence/manifest.json"}:
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
            assets = {"/": ("world.html", "text/html; charset=utf-8"), "/arena": ("arena.html", "text/html; charset=utf-8"),
                      "/world.js": ("world.js", "text/javascript; charset=utf-8"), "/world.css": ("world.css", "text/css; charset=utf-8"),
                      "/campus.js": ("campus.js", "text/javascript; charset=utf-8"), "/economy.js": ("economy.js", "text/javascript; charset=utf-8"),
                      "/vendor/three.module.js": ("vendor/three.module.js", "text/javascript; charset=utf-8"), "/vendor/three.core.min.js": ("vendor/three.core.min.js", "text/javascript; charset=utf-8"),
                      "/arena.js": ("arena.js", "text/javascript; charset=utf-8"), "/arena.css": ("arena.css", "text/css; charset=utf-8"),
                      "/app.js": ("app.js", "text/javascript; charset=utf-8"), "/style.css": ("style.css", "text/css; charset=utf-8")}
            if path in assets:
                name, mime = assets[path]
                return self.send(200, (ROOT / "web" / name).read_bytes(), mime)
            self.send(404, {"error": "Not found"})

        def do_POST(self):
            # Reject cross-origin forms and DNS rebinding before any credit-spending action.
            expected = {"127.0.0.1:" + str(port), "localhost:" + str(port)}
            if self.headers.get("Host") not in expected:
                return self.send(403, {"error": "Local host required"})
            origin = self.headers.get("Origin")
            if origin and origin not in {"http://" + host for host in expected}:
                return self.send(403, {"error": "Same origin required"})
            if self.headers.get("X-Genesis-Action") not in {"evolve", "local-test"}:
                return self.send(403, {"error": "Explicit action header required"})
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
            except (ValueError, TypeError) as exc:
                return self.send(400, {"error": str(exc)})
            threading.Thread(target=engine.run, daemon=True).start()
            self.send(202, {"id": engine.snapshot()["id"]})

        def log_message(self, *args):
            pass

    server = ThreadingHTTPServer((host, port), Handler)
    print("CORE GENESIS · Living Company → http://%s:%s · Technical Arena /arena" % (host, port), flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CORE GENESIS local Evolution Arena")
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--host", choices=["127.0.0.1", "0.0.0.0"], default="127.0.0.1")
    parser.add_argument("--fresh", action="store_true", help="Run reproducible baseline experiments instead of continuing the last verified team")
    args = parser.parse_args()
    serve(host=args.host, port=args.port, fresh=args.fresh)
