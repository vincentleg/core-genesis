"""Pilot safety boundary tests. Fixture records are not browser evidence."""
import contextlib
import io
import json
import datetime as dt
import hashlib
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
from scripts import test_core

class ProductGateTests(unittest.TestCase):
    def test_successful_room_preflight_cannot_authorize_failed_earth_entry(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            prior=root/'company/core-browser/fixture';prior.mkdir(parents=True)
            (prior/'summary.json').write_text(json.dumps({'suite':'product','entry':'room','passed':True,'commit':'a'*40}))
            argv=['test_core.py','--suite','pilot','--entry','earth','--mode','local-agent','--model','fixture','--sessions','10','--execute-pilot']
            with patch.object(test_core,'ROOT',root),patch.object(test_core,'inspect_core',return_value={'commit':'a'*40}),patch.object(test_core,'ThreadingHTTPServer') as server,patch('sys.argv',argv),contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as stopped:test_core.main()
                self.assertEqual(stopped.exception.code,2)
                server.assert_not_called()

    def test_session_cap_rejects_before_inspection_or_execution(self):
        with patch('sys.argv',['test_core.py','--sessions','11']),patch.object(test_core,'inspect_core') as inspect,contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):test_core.main()
            inspect.assert_not_called()

    def test_resume_cannot_reset_an_expired_pilot_budget(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            run=(dt.datetime.now(dt.timezone.utc)-dt.timedelta(minutes=31)).strftime('%Y%m%dT%H%M%SZ-aaaaaa')
            capture=root/'company/core-browser'/run;capture.mkdir(parents=True)
            config={'suite':'pilot','entry':'room','model':'fixture','commit':'a'*40,'sessions':10,'total_budget_ms':1800000}
            file=capture/'config.json';file.write_text(json.dumps(config))
            (capture/'checksums.json').write_text(json.dumps({'config.json':hashlib.sha256(file.read_bytes()).hexdigest()}))
            # A recent filesystem modification time must not reset the original deadline.
            os.utime(file,None)
            prior=root/'company/core-browser/preflight';prior.mkdir()
            (prior/'summary.json').write_text(json.dumps({'suite':'product','entry':'room','passed':True,'commit':'a'*40}))
            argv=['test_core.py','--suite','pilot','--entry','room','--mode','local-agent','--model','fixture','--sessions','10','--execute-pilot','--resume',run]
            err=io.StringIO()
            with patch.object(test_core,'ROOT',root),patch.object(test_core,'inspect_core',return_value={'commit':'a'*40}),patch.object(test_core,'ThreadingHTTPServer') as server,patch('sys.argv',argv),contextlib.redirect_stderr(err):
                with self.assertRaises(SystemExit):test_core.main()
                self.assertIn('Original pilot budget exhausted',err.getvalue())
                server.assert_not_called()

    def test_failed_or_mismatched_smoke_cannot_authorize_mixed_pilot(self):
        for invalid in ('failed','wrong_model','checksum'):
            with self.subTest(invalid=invalid),tempfile.TemporaryDirectory() as directory:
                root=Path(directory);base=root/'company/core-browser';prior=base/'preflight';prior.mkdir(parents=True)
                (prior/'summary.json').write_text(json.dumps({'suite':'product','entry':'room','passed':True,'commit':'a'*40}))
                smoke=base/'20261018T000000Z-aaaaaa';smoke.mkdir()
                record={'suite':'smoke','passed':invalid!='failed','commit':'a'*40,'model':'different' if invalid=='wrong_model' else 'fixture','browser_task_successes':1,'evaluation_successes':1}
                file=smoke/'summary.json';file.write_text(json.dumps(record))
                (smoke/'checksums.json').write_text(json.dumps({'summary.json':'incorrect' if invalid=='checksum' else hashlib.sha256(file.read_bytes()).hexdigest()}))
                argv=['test_core.py','--suite','pilot','--entry','mixed','--mode','local-agent','--model','fixture','--sessions','10','--execute-pilot','--smoke-run',smoke.name]
                with patch.object(test_core,'ROOT',root),patch.object(test_core,'inspect_core',return_value={'commit':'a'*40}),patch.object(test_core,'ThreadingHTTPServer') as server,patch('sys.argv',argv),contextlib.redirect_stderr(io.StringIO()):
                    with self.assertRaises(SystemExit):test_core.main()
                    server.assert_not_called()

    def test_journey_cannot_launch_multiple_or_unknown_cases(self):
        for args in [['--scenario','my-core','--variant','empty','--sessions','2'],['--scenario','unknown','--variant','empty']]:
            with self.subTest(args=args),patch('sys.argv',['test_core.py','--suite','journey']+args),patch.object(test_core,'inspect_core') as inspect,contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit):test_core.main()
                inspect.assert_not_called()

    def test_product_runner_rejects_production_before_browser_or_inference(self):
        with tempfile.TemporaryDirectory() as directory:
            config=Path(directory)/'fixture.json'
            config.write_text(json.dumps({'base':'https://creationofrebornearth.com','output':str(test_core.ROOT/'company/core-browser/fixture'),'commit':'a'*40,'max_cost_usd':0}))
            result=subprocess.run(['node',str(test_core.ROOT/'scripts/core_product_browser.cjs'),str(config)],capture_output=True,text=True,timeout=10)
            self.assertNotEqual(result.returncode,0)
            self.assertIn('Local immutable CORE only',result.stderr)

if __name__=='__main__':unittest.main()
