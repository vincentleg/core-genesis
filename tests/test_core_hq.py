"""Safety and provenance checks. Fixtures are not product/browser evidence."""
import copy
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from core_genesis.core_access import inspect_core
from core_genesis.human_testing import validate_human_record
from core_genesis.crusoe import CrusoeClient
from core_genesis.company import Company


class AccessTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.repo = Path(self.temp.name)
        self.run_git('init', '-b', 'v9.2/earth-first')
        (self.repo/'src').mkdir()
        (self.repo/'src/app.js').write_text('const source = true;\n' * 100)
        (self.repo/'world.html').write_text('<h1>CORE fixture</h1>')
        (self.repo/'src/.env.json').write_text('{"sensitive":"not-real"}')
        (self.repo/'src/link.js').symlink_to('/etc/passwd')
        self.run_git('add', '.')
        self.run_git('-c','user.name=Fixture','-c','user.email=fixture@example.invalid','commit','-m','fixture')
        self.sha = self.run_git('rev-parse','HEAD').strip()
    def tearDown(self): self.temp.cleanup()
    def run_git(self,*args):
        return subprocess.check_output(['git','-C',str(self.repo),*args],stderr=subprocess.DEVNULL).decode()
    def test_commit_pinned_full_reads_ignore_dirty_files_and_unsafe_paths(self):
        (self.repo/'src/app.js').write_text('uncommitted change')
        before = self.run_git('status','--porcelain')
        s = inspect_core(self.repo)
        self.assertEqual(s['commit'],self.sha)
        self.assertTrue(s['checkout_dirty'])
        source = next(x for x in s['sources'] if x['path']=='src/app.js')
        self.assertEqual(source['line_end'],100)
        self.assertFalse(source['truncated'])
        self.assertNotIn('uncommitted',source['text'])
        self.assertEqual({x['path'] for x in s['sources']},{'src/app.js','world.html'})
        self.assertFalse(s['external_transmission_allowed'])
        self.assertEqual(self.run_git('status','--porcelain'),before)
    def test_missing_branch_does_not_fall_back_and_explicit_commit_works(self):
        with self.assertRaises(subprocess.CalledProcessError): inspect_core(self.repo,'does-not-exist')
        self.assertEqual(inspect_core(self.repo,self.sha)['commit'],self.sha)
        with self.assertRaises(ValueError): inspect_core(self.repo,'--help')


class SafetyTests(unittest.TestCase):
    def test_paid_client_is_blocked_before_network(self):
        with patch.dict('os.environ', {'CORE_HQ_ALLOW_PAID_INFERENCE':'disabled'}), patch('urllib.request.urlopen') as request:
            client=CrusoeClient(api_key='fixture-key')
            with self.assertRaisesRegex(RuntimeError,'Paid inference disabled'):
                client._request('POST','/chat/completions',{})
            request.assert_not_called()
    def test_local_source_cannot_enter_remote_mission_reasoning(self):
        company=object.__new__(Company)
        company.guard=lambda:None
        company.state={'snapshot':{'external_transmission_allowed':False}}
        with self.assertRaisesRegex(ValueError,'Local CORE source cannot'):
            company.reason('Research','research','analyze',{}, {})


    def test_private_local_snapshot_is_rejected_by_public_export(self):
        from core_genesis.publication import public_company_record
        with self.assertRaisesRegex(ValueError,'Private local CORE'):
            public_company_record({'snapshot':{'external_transmission_allowed':False,'sources':[{'text':'private fixture'}]}},{})


class HumanTests(unittest.TestCase):
    def record(self):
        return {'schema_version':1,'platform':'fixture','study_id':'fixture','target':{'environment':'local','commit':'a'*40},
                'declared_participants':0,'participants':[],'evidence':[],'consent_status':'pending'}
    def person(self):
        return {'participant_id':'P1','consent_evidence':'consent.pdf','tasks':[{'task_id':'explore','completed':True,'evidence':'recording.mp4'}],
                'feedback':[],'issues':[],'evidence':['recording.mp4']}
    def test_empty_template_never_infers_participation(self):
        self.assertEqual(validate_human_record(self.record())['actual_human_participants'],0)
    def test_count_and_consent_fail_closed(self):
        r=self.record();r['declared_participants']=10
        with self.assertRaises(ValueError):validate_human_record(r)
        r['declared_participants']=1;r['participants']=[self.person()]
        with self.assertRaisesRegex(ValueError,'consent'):validate_human_record(r)
    def test_metrics_use_actual_rows_and_duplicates_rejected(self):
        r=self.record();r.update(declared_participants=2,consent_status='documented',evidence=['export.csv'])
        a=self.person();b=copy.deepcopy(a);b['participant_id']='P2';b['tasks'][0]['completed']=False;r['participants']=[a,b]
        result=validate_human_record(r)
        self.assertEqual(result['task_metrics']['explore']['completion_rate'],0.5)
        b['participant_id']='P1'
        with self.assertRaises(ValueError):validate_human_record(r)

if __name__=='__main__':unittest.main()
