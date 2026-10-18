"""Serve immutable CORE Git blobs on loopback, run bounded browser sessions, retain evidence."""
import argparse
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import mimetypes
import re
from pathlib import Path, PurePosixPath
import subprocess
import sys
import threading
import time
from urllib.parse import unquote, urlsplit
import uuid
import datetime as dt
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from core_genesis.core_access import inspect_core, git
ROOT = Path(__file__).resolve().parent.parent
STATIC = {'.html','.js','.mjs','.css','.json','.svg','.png','.jpg','.jpeg','.webp','.ico','.woff','.woff2','.ttf','.glb','.bin','.wasm','.geojson'}

def handler(repo, sha, paths):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            name = unquote(urlsplit(self.path).path).lstrip('/') or 'index.html'
            if name not in paths or any(p.startswith('.') or p == '..' for p in PurePosixPath(name).parts) or Path(name).suffix not in STATIC:
                self.send_error(404); return
            body = git(repo, 'show', sha + ':' + name)
            self.send_response(200)
            self.send_header('Content-Type', 'application/javascript' if name.endswith('.mjs') else mimetypes.guess_type(name)[0] or 'application/octet-stream')
            self.send_header('Content-Length', str(len(body)))
            self.send_header('X-CORE-Commit', sha)
            self.send_header('Cache-Control', 'no-store')
            self.end_headers()
            try: self.wfile.write(body)
            except (BrokenPipeError, ConnectionResetError): pass
        def log_message(self, *args): pass
    return Handler

def run_bounded(command, out, budget_seconds):
    """Reserve termination grace inside the deadline; retain finalized and partial reports."""
    process = subprocess.Popen(command, cwd=ROOT)
    watchdog = None
    try:
        process.wait(timeout=max(0.01, budget_seconds-8))
    except subprocess.TimeoutExpired:
        watchdog = {'reason':'Harness deadline', 'termination':'SIGTERM', 'partial_artifacts_retained':True}
        process.terminate()
        try:
            process.wait(timeout=min(7, max(0.01, budget_seconds-0.01)))
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=1)
            watchdog['termination']='SIGKILL_after_grace'
    if watchdog:
        (out/'watchdog.json').write_text(json.dumps(watchdog,indent=2))
    if not (out/'summary.json').exists():
        records, unreadable = [], []
        for file in sorted(out.glob('session-*/report.json')):
            try: records.append(json.loads(file.read_text()))
            except (OSError, ValueError) as error: unreadable.append({'file':str(file.relative_to(out)), 'error':str(error)})
        finished = {'completed','completed_with_failure','completed_evaluation_failure'}
        summary = {'passed':False,'recovered':True,'error':'Runner ended without final summary',
                   'attempted':len(records),'completed':sum(r.get('status') in finished for r in records),
                   'incomplete':sum(r.get('status') not in finished for r in records),
                   'browser_task_successes':sum(r.get('browser_tasks_passed') is True for r in records),
                   'sessions':records,'unreadable_reports':unreadable,'returncode':process.returncode}
        (out/'summary.json').write_text(json.dumps(summary,indent=2))
    return process.returncode if not watchdog else 1

def main():
    launched = time.monotonic()
    p = argparse.ArgumentParser()
    p.add_argument('--resume', help='Continue only unrun personas of an existing pilot within its original deadline')
    p.add_argument('--entry', choices=['earth','room'], default='earth', help='Explicit product entry; no silent fallback')
    p.add_argument('--suite', choices=['navigation','product','pilot','earth-diagnostic'], default='navigation')
    p.add_argument('--repo')
    p.add_argument('--ref')
    p.add_argument('--mode', choices=['scripted','local-agent'], default='scripted')
    p.add_argument('--model', help='An already installed Ollama model; no downloads or paid providers')
    p.add_argument('--sessions', type=int, default=1)
    p.add_argument('--execute-pilot', action='store_true', help='Run up to ten sessions after a successful single-session gate')
    p.add_argument('--check-models', action='store_true', help='Probe local Ollama only; no inference or downloads')
    a = p.parse_args()
    if a.check_models:
        import urllib.request
        try:
            with urllib.request.urlopen('http://127.0.0.1:11434/api/tags', timeout=3) as response:
                data = json.load(response)
            check = {'status':'available','models':[m['name'] for m in data.get('models',[])], 'inference_calls':0}
        except Exception as error:
            check = {'status':'unavailable','reason':str(error),'inference_calls':0}
        target = ROOT/'company/core-browser/model-preflight.json'
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(check,indent=2))
        print(json.dumps(check))
        return 0 if check['status']=='available' else 1
    if a.suite == 'navigation' and a.entry != 'earth': p.error('Explicit room entry requires the product or pilot suite')
    if not 1 <= a.sessions <= 10: p.error('One to ten sessions only')
    if a.mode == 'local-agent' and not a.model: p.error('--model required; no automatic model selection or download')
    snapshot = inspect_core(a.repo, a.ref)
    if a.suite == 'pilot' and (a.mode != 'local-agent' or not a.execute_pilot): p.error('Pilot requires local-agent mode and --execute-pilot')
    if a.suite in {'product','earth-diagnostic'} and a.sessions != 1: p.error('Product preflight is one session')
    if a.sessions > 1 or a.suite == 'pilot':
        if not a.execute_pilot: p.error('Multi-session runs require --execute-pilot')
        prior = []
        for file in (ROOT/'company/core-browser').glob('*/summary.json'):
            record = json.loads(file.read_text())
            if a.suite == 'pilot':
                if record.get('suite') == 'product' and record.get('entry','earth') == a.entry and record.get('passed') and record.get('commit') == snapshot['commit']: prior.append(record)
                continue
            if record.get('mode') == a.mode and record.get('completed') == 1 and record.get('passed') and record.get('commit') == snapshot['commit'] and record.get('model') == a.model:
                prior.append(record)
        if not prior: p.error('A successful single session in this mode is required before the pilot')
    resume_root = None
    start_index = 0
    total_budget_ms = max(1000,1800000-int((time.monotonic()-launched)*1000))
    if a.resume:
        if a.suite != 'pilot' or not re.fullmatch(r'[0-9]{8}T[0-9]{6}Z-[a-f0-9]{6}', a.resume): p.error('Resume requires an existing pilot run ID')
        original = ROOT/'company/core-browser'/a.resume/'config.json'
        prior_config = json.loads(original.read_text())
        if any(prior_config.get(k) != v for k,v in [('suite','pilot'),('entry',a.entry),('model',a.model),('commit',snapshot['commit']),('sessions',a.sessions)]): p.error('Resume must retain target, entry, model and ten-session plan')
        hashes = json.loads((original.parent/'checksums.json').read_text())
        if hashes.get('config.json') != hashlib.sha256(original.read_bytes()).hexdigest(): p.error('Original pilot config checksum mismatch')
        captured = dt.datetime.strptime(a.resume.split('-')[0], '%Y%m%dT%H%M%SZ').replace(tzinfo=dt.timezone.utc).timestamp()
        deadline = captured + prior_config['total_budget_ms']/1000
        total_budget_ms = int((deadline-time.time())*1000)
        if total_budget_ms < 15000: p.error('Original pilot budget exhausted')
        ids=[]
        for config_file in (ROOT/'company/core-browser').glob('*/config.json'):
            capture_config=json.loads(config_file.read_text())
            if config_file.parent.name==a.resume or capture_config.get('resume_root')==a.resume:
                ids.extend(json.loads(f.read_text())['id'] for f in config_file.parent.glob('session-*/report.json'))
        if sorted(ids)!=list(range(1,len(ids)+1)) or len(ids)>=a.sessions: p.error('Prior persona IDs must be unique and contiguous; never rerun a persona')
        resume_root=a.resume
        start_index=len(ids)
    run = dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ-') + uuid.uuid4().hex[:6]
    out = ROOT/'company/core-browser'/run
    out.mkdir(parents=True)
    # Evidence contains paths/hashes only; source bodies never go to browser models or public output.
    provenance = {k:v for k,v in snapshot.items() if k != 'sources'}
    provenance['source_manifest'] = [{k:v for k,v in s.items() if k != 'text'} for s in snapshot['sources']]
    (out/'provenance.json').write_text(json.dumps(provenance, indent=2))
    server = ThreadingHTTPServer(('127.0.0.1',0), handler(snapshot['local_path'], snapshot['commit'], set(snapshot['structure'])))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    config = {'base': 'http://127.0.0.1:'+str(server.server_port), 'commit': snapshot['commit'], 'output': str(out),
              'suite':a.suite,'entry':a.entry,'resume_root':resume_root,'start_index':start_index,'total_budget_ms':total_budget_ms,'mode':a.mode,'model':a.model,'sessions':a.sessions,'max_steps':12,'max_model_calls':12,
              'external_network':'blocked','environment':'local_immutable_commit','max_cost_usd':0}
    (out/'config.json').write_text(json.dumps(config, indent=2))
    try:
        runner = {'navigation':'core_browser.cjs','earth-diagnostic':'diagnose_core_earth.cjs'}.get(a.suite,'core_product_browser.cjs')
        returncode = run_bounded(['node',str(ROOT/'scripts'/runner),str(out/'config.json')], out, min(1800,config['total_budget_ms']/1000) if a.suite == 'pilot' else 240*a.sessions)
        if a.suite == 'earth-diagnostic':
            (out/'summary.json').write_text(json.dumps({'suite':'earth-diagnostic','commit':snapshot['commit'],'completed':0,'pilot_sessions':0,'model_calls':0,'note':'See diagnostic.json; this is not a product pass or an AI session'}))
    finally:
        server.shutdown(); server.server_close()
    manifest = {str(f.relative_to(out)):hashlib.sha256(f.read_bytes()).hexdigest() for f in out.rglob('*') if f.is_file()}
    (out/'checksums.json').write_text(json.dumps(manifest,indent=2))
    print('Evidence:',out)
    return returncode
if __name__ == '__main__': sys.exit(main())
