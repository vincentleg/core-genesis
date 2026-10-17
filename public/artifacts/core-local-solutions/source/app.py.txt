"""Audited standard-library scaffold. Model choices are data in spec.json, never code."""
import argparse
import datetime as dt
import json
from pathlib import Path
import threading
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent
NOTICE = 'Local prototype only. Human review records a local decision, not authorization for real-world implementation.'


class Application:
    def __init__(self, directory=ROOT, store=None):
        self.directory = Path(directory)
        self.spec = json.loads((self.directory / 'spec.json').read_text())
        self.store = Path(store or self.directory / 'data' / 'records.json')
        self.lock = threading.RLock()

    def state(self):
        with self.lock:
            state = json.loads(self.store.read_text()) if self.store.exists() else {'problems': [], 'solutions': []}
            return {**state, 'spec': self.spec, 'notice': NOTICE}

    def text(self, data, key, minimum, maximum):
        value = data.get(key)
        if not isinstance(value, str) or not minimum <= len(value.strip()) <= maximum or any(ord(c) < 32 and c not in '\n\t' for c in value):
            raise ValueError('%s must contain %d–%d characters' % (key, minimum, maximum))
        return value.strip()

    def change(self, path, data, human_review=False):
        if not isinstance(data, dict):
            raise ValueError('Expected a JSON object')
        with self.lock:
            state = self.state()
            record = {'id': uuid.uuid4().hex, 'created_at': dt.datetime.now(dt.timezone.utc).isoformat()}
            if len(state['problems']) + len(state['solutions']) >= 500:
                raise ValueError('Local prototype capacity reached; export and review records')
            if path == '/api/problems':
                if set(data) - {'title', 'description', 'location', 'evidence'}:
                    raise ValueError('Unknown problem fields')
                record.update(title=self.text(data, 'title', 3, 120), description=self.text(data, 'description', self.spec['minimum_description_chars'], self.spec['maximum_description_chars']), location=self.text(data, 'location', 1 if self.spec['require_location'] else 0, 160), status='unreviewed')
                evidence = data.get('evidence', '')
                if not isinstance(evidence, str) or len(evidence) > 500 or evidence and (urlparse(evidence).scheme != 'https' or not urlparse(evidence).netloc or urlparse(evidence).username):
                    raise ValueError('Optional evidence must be a public HTTPS URL; it is never fetched')
                record['evidence'] = evidence
                state['problems'].append(record)
            elif path == '/api/solutions':
                if set(data) - {'problem_id', 'description'}:
                    raise ValueError('Unknown solution fields')
                if not any(p['id'] == data.get('problem_id') for p in state['problems']):
                    raise ValueError('Problem does not exist')
                record.update(problem_id=data['problem_id'], description=self.text(data, 'description', 10, self.spec['maximum_description_chars']), status='pending_human_review', authorized_for_real_world=False)
                state['solutions'].append(record)
            elif path == '/api/review':
                if not human_review or set(data) != {'solution_id', 'decision'} or data['decision'] not in {'approve', 'reject'}:
                    raise ValueError('Explicit local human review action required')
                record = next((s for s in state['solutions'] if s['id'] == data['solution_id']), None)
                if not record:
                    raise ValueError('Solution does not exist')
                record.update(status='human_approved' if data['decision'] == 'approve' else 'human_rejected', reviewed_at=dt.datetime.now(dt.timezone.utc).isoformat(), reviewer='Local human reviewer (identity not authenticated)', authorized_for_real_world=False)
            else:
                raise ValueError('Unsupported action')
            self.store.parent.mkdir(parents=True, exist_ok=True)
            temporary = self.store.with_suffix('.tmp')
            temporary.write_text(json.dumps({key: state[key] for key in ('problems', 'solutions')}, indent=2))
            temporary.replace(self.store)
            return record


def dispatch(handler, application, prefix=''):
    path = urlparse(handler.path).path[len(prefix):] or '/'
    if handler.command == 'GET':
        if path == '/api/state':
            return handler.send(200, application.state())
        assets = {'/': ('index.html', 'text/html; charset=utf-8'), '/index.html': ('index.html', 'text/html; charset=utf-8'), '/app.js': ('app.js', 'text/javascript; charset=utf-8'), '/style.css': ('style.css', 'text/css; charset=utf-8')}
        if path in assets:
            name, mime = assets[path]
            return handler.send(200, (application.directory / name).read_bytes(), mime)
        return handler.send(404, {'error': 'Not found'})
    port = handler.server.server_address[1]
    hosts = {'127.0.0.1:' + str(port), 'localhost:' + str(port)}
    origin = handler.headers.get('Origin')
    if handler.headers.get('Host') not in hosts or origin and origin not in {'http://' + h for h in hosts}:
        return handler.send(403, {'error': 'Loopback same-origin access required'})
    if handler.headers.get('X-Local-Solutions') != 'explicit-action':
        return handler.send(403, {'error': 'Explicit action required'})
    try:
        size = int(handler.headers.get('Content-Length', '0'))
        if not 1 <= size <= 16000:
            raise ValueError('Bounded JSON body required')
        data = json.loads(handler.rfile.read(size))
        record = application.change(path, data, handler.headers.get('X-Human-Review') == 'approve-local-review')
        return handler.send(201, record)
    except (ValueError, TypeError, KeyError) as exc:
        return handler.send(400, {'error': str(exc)})


def make_server(directory=ROOT, port=8091, store=None):
    application = Application(directory, store)
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass
        def send(self, status, data, kind='application/json'):
            body = json.dumps(data).encode() if kind == 'application/json' else data
            self.send_response(status)
            self.send_header('Content-Type', kind)
            self.send_header('Content-Length', str(len(body)))
            self.send_header('Cache-Control', 'no-store')
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'")
            self.end_headers()
            self.wfile.write(body)
        def do_GET(self):
            dispatch(self, application)
        def do_POST(self):
            dispatch(self, application)
    return ThreadingHTTPServer(('127.0.0.1', port), Handler)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=8091)
    args = parser.parse_args()
    server = make_server(port=args.port)
    print('CORE Local Solutions → http://127.0.0.1:%d (local human review only)' % args.port, flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()
