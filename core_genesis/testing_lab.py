"""Real bounded Product Testing: three browser actors, reproducible evidence and one restoration repair."""
import copy
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import uuid
from .artifact_builder import ROOT, FILES, SCAFFOLD, run_directory, verify


class BrowserLab:
    def __init__(self, company):
        self.company = company
        self.directory = company.directory / 'testing'
        self.directory.mkdir(exist_ok=True)
        self.state = {'status': 'idle'}
        captures = sorted(self.directory.glob('browser-*/summary.json'))
        if captures:
            self.state = json.loads(captures[-1].read_text())
            if self.state.get('status') == 'running':
                self.state['status'] = 'interrupted'

    def snapshot(self):
        return copy.deepcopy(self.state)

    def start(self):
        self.company.guard()
        mission = self.company.snapshot()
        if self.state.get('status') == 'running' or mission.get('status') == 'running':
            raise ValueError('Wait for the current work to finish')
        if not mission.get('artifacts', {}).get('prototype', {}).get('test_report', {}).get('passed'):
            raise ValueError('A completed, tested prototype is required')
        self.state = {'id': 'browser-' + str(int(time.time())) + '-' + uuid.uuid4().hex[:6], 'mission_id': mission['id'], 'status': 'running', 'started_at': time.time(), 'events': [], 'handoffs': [], 'new_model_requests': 0}
        self.state['events'].append({'timestamp': time.time(), 'mission_id': mission['id'], 'department': 'product', 'type': 'browser_testing.started', 'status': 'running', 'evidence': ['scripts/browser_beta.cjs']})
        self.company.event('Product Testing Lead', 'product', 'Three actual local browser testers authorized; no model calls', event_type='product_testing.started', evidence=[self.state['id']])
        self.save()
        return self.snapshot()

    def save(self):
        directory = self.directory / self.state['id']
        directory.mkdir(exist_ok=True)
        self.company.write(directory / 'summary.json', self.state)

    def run(self):
        try:
            directory = run_directory(self.state['mission_id'], self.company.directory.parent / 'artifacts/core-local-solutions')
            for name in FILES:
                if (directory / name).read_bytes() != (SCAFFOLD / name).read_bytes():
                    raise ValueError('Untrusted artifact changes: browser execution refused')
            self.state['source_hashes'] = {name: hashlib.sha256((directory / name).read_bytes()).hexdigest() for name in FILES}
            self.state['regression_before'] = verify(directory, persist=False)
            self.state['before'] = self.execute(directory, 'before')
            if not self.state['before']['passed']:
                self.state['reproduced'] = self.execute(directory, 'reproduce')
                if not self.state['reproduced']['passed']:
                    handoff = {'source_agent': 'Product Browser Testers', 'destination_agent': 'Engineering Lead', 'task': 'One bounded repair: restore audited scaffold only, then repeat identical browser cases and regression tests', 'evidence': ['before/report.json', 'reproduce/report.json'], 'status': 'assigned', 'timestamp': time.time(), 'result': None}
                    self.state['handoffs'].append(handoff)
                    for name in FILES:
                        shutil.copyfile(SCAFFOLD / name, directory / name)
                    self.state['after'] = self.execute(directory, 'after')
                    self.state['regression_after'] = verify(directory, persist=False)
                    handoff.update(status='complete' if self.state['after']['passed'] and self.state['regression_after']['passed'] else 'failed', result={'browser_passed': self.state['after']['passed'], 'regression_passed': self.state['regression_after']['passed']}, completed_at=time.time())
            self.state['repair'] = 'One audited restoration attempted' if self.state.get('after') else 'Not needed or failure not reproduced; no repair claimed'
            self.state['handoffs'].append({'source_agent': 'Product Testing Lead', 'destination_agent': 'Evolution Lab', 'task': 'Review actual functional outcome as workflow evidence; evaluate any proposed change on independent fixtures before promotion', 'evidence': ['before/report.json'], 'status': 'awaiting_independent_evaluation', 'timestamp': time.time(), 'result': None})
            self.state['evolution_evidence'] = {'evidence_type': 'Actual functional workflow outcome; never synthetic satisfaction', 'browser_before': self.state['before'].get('successes', 0), 'browser_after': self.state.get('after', {}).get('successes'), 'automatic_promotion': False, 'requirement': 'Any organizational mutation must separately pass existing development, held-out and regression gate', 'linked_mission_gate': self.company.snapshot().get('evolution', {}).get('action')}
            latest = self.state.get('after', self.state.get('reproduced', self.state['before']))
            self.state['status'] = 'complete' if latest['passed'] else 'failed'
            for agent in latest.get('agents', []):
                self.company.event(agent['role'], 'product', 'Actual browser case ' + ('passed' if agent['passed'] else 'failed'), event_type='product_testing.result', state='idle' if agent['passed'] else 'needs_attention', evidence=[self.state['id'], agent['screenshot']])
            self.company.state['artifacts']['browser_testing'] = {'id': self.state['id'], 'status': self.state['status'], 'successes': latest.get('successes', 0), 'completed': latest.get('completed', 0), 'new_model_requests': 0}
            self.company.save()
        except Exception as exc:
            self.state.update(status='error', error=str(exc))
        finally:
            self.state['finished_at'] = time.time()
            self.save()

    def execute(self, directory, phase):
        self.company.guard()
        output = self.directory / self.state['id'] / phase
        result = subprocess.run(['node', str(ROOT / 'scripts/browser_beta.cjs'), str(directory), str(output), sys.executable], cwd=str(ROOT), capture_output=True, text=True, timeout=100, env=os.environ.copy())
        report_path = output / 'report.json'
        report = json.loads(report_path.read_text()) if report_path.exists() else {'passed': False, 'agents': [], 'completed': 0, 'error': 'Browser tool unavailable: npm install required', 'stderr': result.stderr[-1000:]}
        report['exit_code'] = result.returncode
        self.state['events'].append({'timestamp': time.time(), 'mission_id': self.state['mission_id'], 'department': 'product', 'type': 'browser_testing.' + phase, 'status': 'passed' if report['passed'] else 'failed', 'evidence': [phase + '/report.json']})
        self.save()
        return report
