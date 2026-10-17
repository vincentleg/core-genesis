"""Real API tests. Every store is temporary; no synthetic records enter the usable app."""
import json
from pathlib import Path
import tempfile
import threading
import unittest
import urllib.request
import urllib.error
from app import Application, make_server

ROOT = Path(__file__).resolve().parent


class LocalSolutionsTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(dir=ROOT / '.test-work')
        self.app = Application(ROOT, Path(self.temporary.name) / 'records.json')
        self.problem = {'title': 'Unsafe library crossing', 'description': 'People have difficulty crossing near the local library during busy hours.', 'location': 'Library plaza', 'evidence': 'https://example.org/observation'}

    def tearDown(self):
        self.temporary.cleanup()

    def test_problem_and_pending_solution_persist(self):
        problem = self.app.change('/api/problems', self.problem)
        solution = self.app.change('/api/solutions', {'problem_id': problem['id'], 'description': 'Study a pedestrian crossing with residents and municipal reviewers.'})
        state = Application(ROOT, self.app.store).state()
        self.assertEqual(state['problems'][0]['title'], self.problem['title'])
        self.assertEqual(state['solutions'][0]['problem_id'], problem['id'])
        self.assertEqual(solution['status'], 'pending_human_review')
        self.assertFalse(solution['authorized_for_real_world'])

    def test_human_review_never_authorizes_real_world_action(self):
        p = self.app.change('/api/problems', self.problem)
        s = self.app.change('/api/solutions', {'problem_id': p['id'], 'description': 'Investigate a safer crossing with local experts.'})
        body = {'solution_id': s['id'], 'decision': 'approve'}
        with self.assertRaises(ValueError):
            self.app.change('/api/review', body)
        reviewed = self.app.change('/api/review', body, True)
        self.assertEqual(reviewed['status'], 'human_approved')
        self.assertFalse(reviewed['authorized_for_real_world'])

    def test_invalid_problem_and_unsafe_evidence_rejected(self):
        for key, value in [('title', ''), ('description', 'short'), ('evidence', 'javascript:alert(1)'), ('evidence', 'https://user:pass@example.org/'), ('location', {'bad': 'type'})]:
            with self.subTest(key=key, value=value), self.assertRaises(ValueError):
                self.app.change('/api/problems', {**self.problem, key: value})
        self.assertEqual(self.app.state()['problems'], [])

    def test_unknown_problem_and_permission_fields_rejected(self):
        with self.assertRaises(ValueError):
            self.app.change('/api/solutions', {'problem_id': 'missing', 'description': 'Investigate the problem safely.'})
        with self.assertRaises(ValueError):
            self.app.change('/api/problems', {**self.problem, 'approved': True})

    def test_model_configuration_is_enforced(self):
        with self.assertRaises(ValueError):
            self.app.change('/api/problems', {**self.problem, 'description': 'a' * (self.app.spec['maximum_description_chars'] + 1)})
        if self.app.spec['require_location']:
            with self.assertRaises(ValueError):
                self.app.change('/api/problems', {**self.problem, 'location': ''})

    def test_user_text_is_data_not_executable_markup(self):
        p = self.app.change('/api/problems', {**self.problem, 'title': '<img src=x onerror=alert(1)>'})
        self.assertIn('<img', p['title'])
        client = (ROOT / 'app.js').read_text()
        self.assertNotIn('innerHTML', client)
        self.assertIn('textContent', client)

    def test_real_http_start_create_propose_read_and_reject_cross_origin(self):
        server = make_server(ROOT, 0, self.app.store)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        base = 'http://127.0.0.1:%d' % server.server_address[1]
        def request(path, data=None, headers=None):
            req = urllib.request.Request(base + path, data=json.dumps(data).encode() if data is not None else None, headers={'Content-Type': 'application/json', 'X-Local-Solutions': 'explicit-action', **(headers or {})})
            return urllib.request.urlopen(req, timeout=5)
        try:
            with request('/') as response:
                self.assertEqual(response.status, 200)
                self.assertIn(b'CORE LOCAL SOLUTIONS', response.read())
            with request('/api/problems', self.problem) as response:
                p = json.load(response)
            with request('/api/solutions', {'problem_id': p['id'], 'description': 'Prepare a reviewed crossing study with accessible alternatives.'}) as response:
                self.assertEqual(json.load(response)['status'], 'pending_human_review')
            with request('/api/state') as response:
                state = json.load(response)
                self.assertEqual(len(state['problems']), 1)
                self.assertEqual(len(state['solutions']), 1)
            with self.assertRaises(urllib.error.HTTPError) as caught:
                request('/api/problems', self.problem, {'Origin': 'https://untrusted.example'})
            self.assertEqual(caught.exception.code, 403)
            with self.assertRaises(urllib.error.HTTPError):
                request('/../../.env')
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=3)


if __name__ == '__main__':
    (ROOT / '.test-work').mkdir(exist_ok=True)
    unittest.main(verbosity=2)
