"""Watchdog fixtures, not browser sessions."""
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import Mock, patch
from scripts.test_core import run_bounded

class RecoveryTests(unittest.TestCase):
    def test_timeout_preserves_finished_summary_and_grace(self):
        with tempfile.TemporaryDirectory() as d:
            out=Path(d);original='{"completed":9,"passed":false}'
            (out/'summary.json').write_text(original)
            process=Mock(returncode=0);process.wait.side_effect=[subprocess.TimeoutExpired('fixture',1),0]
            with patch('scripts.test_core.subprocess.Popen',return_value=process):
                self.assertEqual(run_bounded(['fixture'],out,30),1)
            process.terminate.assert_called_once();process.kill.assert_not_called()
            self.assertEqual((out/'summary.json').read_text(),original)
            self.assertEqual(json.loads((out/'watchdog.json').read_text())['termination'],'SIGTERM')

    def test_force_kill_recovers_partial_stage_results(self):
        with tempfile.TemporaryDirectory() as d:
            out=Path(d);session=out/'session-01';session.mkdir()
            (session/'report.json').write_text(json.dumps({'status':'running','browser_tasks_passed':True,'stages':{'evaluation':'running'}}))
            process=Mock(returncode=-9);process.wait.side_effect=[subprocess.TimeoutExpired('fixture',1),subprocess.TimeoutExpired('fixture',1),0]
            with patch('scripts.test_core.subprocess.Popen',return_value=process):run_bounded(['fixture'],out,30)
            process.kill.assert_called_once();r=json.loads((out/'summary.json').read_text())
            self.assertEqual(r['completed'],0);self.assertEqual(r['incomplete'],1);self.assertEqual(r['browser_task_successes'],1)
