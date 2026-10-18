"""Scheduler state/process fixtures only. These are not browser or AI participation evidence."""
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
from core_genesis.browser_campaign import prepare
from core_genesis.campaign_scheduler import Scheduler,atomic,command_for,collect

class SchedulerTests(unittest.TestCase):
    def plan(self):return prepare('a'*40)
    def test_sequential_bounded_subset_and_accounting(self):
        with tempfile.TemporaryDirectory() as d:
            seen=[];plan=self.plan()
            def fixture(spec,capture,deadline):
                seen.append(spec['session_id'])
                return {'status':'completed','calls_attempted':2,'calls_returned':2,'prompt_tokens':11,'completion_tokens':3,'unknown_usage_attempts':0,'paid_api_cost_usd':0}
            scheduler=Scheduler.create(plan,['campaign-01','campaign-10','campaign-17'],{},total_ms=90000,session_ms=30000,directory=Path(d)/'run',clock=lambda:1000,runner=fixture)
            result=scheduler.run(2)
            self.assertEqual(seen,['campaign-01','campaign-10']);self.assertEqual(result['totals']['completed'],2)
            self.assertEqual(result['totals']['unstarted'],1);self.assertEqual(result['totals']['prompt_tokens'],22)
            self.assertFalse((scheduler.directory/'runner.lock').exists())
            self.assertEqual(len(list((scheduler.directory/'checkpoints').glob('*.json'))),6)

    def test_resume_keeps_deadline_and_does_not_replay_interrupted(self):
        with tempfile.TemporaryDirectory() as d:
            scheduler=Scheduler.create(self.plan(),['campaign-01','campaign-02'],{},total_ms=90000,session_ms=30000,directory=Path(d)/'run',clock=lambda:1000,runner=lambda *_:{'status':'incomplete','unknown_usage_attempts':1})
            scheduler.run(1)
            resumed=Scheduler.resume(scheduler.directory,clock=lambda:91001,runner=lambda *_:self.fail('Deadline must prevent launch'))
            self.assertEqual(resumed.state['deadline_ms'],91000)
            result=resumed.run(2);self.assertEqual(result['totals']['incomplete'],1);self.assertEqual(result['totals']['attempted'],1)
            self.assertEqual(result['status'],'budget_reached')

    def test_mutated_deadline_and_clock_rollback_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            scheduler=Scheduler.create(self.plan(),['campaign-01'],{},total_ms=90000,session_ms=30000,directory=Path(d)/'run',clock=lambda:1000)
            with self.assertRaisesRegex(ValueError,'Clock'):Scheduler.resume(scheduler.directory,clock=lambda:999)
            state=json.loads((scheduler.directory/'state.json').read_text());state['deadline_ms']+=1000;atomic(scheduler.directory/'state.json',state)
            with self.assertRaisesRegex(ValueError,'policy'):Scheduler.resume(scheduler.directory,clock=lambda:2000)

    def test_running_crash_recovers_partial_and_never_replays(self):
        with tempfile.TemporaryDirectory() as d:
            scheduler=Scheduler.create(self.plan(),['campaign-01','campaign-02'],{},total_ms=90000,session_ms=30000,directory=Path(d)/'run',clock=lambda:1000)
            scheduler.state['records']=[{'session_id':'campaign-01','status':'running','capture':'20261018T000000Z-aaaaaa','core_commit':'a'*40}];scheduler.persist('fixture_crash')
            with patch('core_genesis.campaign_scheduler.collect',return_value={'status':'incomplete','unknown_usage_attempts':1}):resumed=Scheduler.resume(scheduler.directory,clock=lambda:2000)
            visited=[];resumed.runner=lambda spec,*_:(visited.append(spec['session_id']) or {'status':'failed'})
            result=resumed.run(2);self.assertEqual(visited,['campaign-02']);self.assertEqual(result['totals']['incomplete'],1);self.assertEqual(result['totals']['failed'],1)

    def test_interrupt_stops_new_work_and_keeps_unstarted(self):
        with tempfile.TemporaryDirectory() as d:
            scheduler=Scheduler.create(self.plan(),['campaign-01','campaign-02'],{},total_ms=90000,session_ms=30000,directory=Path(d)/'run',clock=lambda:1000)
            def fixture(*_):scheduler.interrupt();return {'status':'incomplete','unknown_usage_attempts':1}
            scheduler.runner=fixture;state=scheduler.run(2)
            self.assertEqual(state['status'],'interrupted');self.assertEqual(state['totals']['attempted'],1);self.assertEqual(state['totals']['unstarted'],1)

    def test_commands_ignore_untrusted_plan_shell_text(self):
        plan=self.plan();spec=plan['sessions'][0];spec['single_session_command']=['sh','-c','do not execute'];cmd=command_for(plan,spec,'20261018T000000Z-aaaaaa',120)
        self.assertNotIn('sh',cmd);self.assertIn('qwen3:8b',cmd);self.assertIn('120',cmd);self.assertIn('1440x1000',cmd)

    def test_wrong_commit_is_a_failed_provenance_check(self):
        with tempfile.TemporaryDirectory() as d:
            out=Path(d);(out/'session-01').mkdir()
            atomic(out/'session-01/report.json',{'commit':'b'*40,'stages':{},'model':{}})
            result=collect(out,'a'*40);self.assertEqual(result['status'],'failed');self.assertEqual(result['failure'],'CORE provenance mismatch')

    def test_partial_usage_is_retained_without_inventing_missing_tokens(self):
        with tempfile.TemporaryDirectory() as d:
            out=Path(d);session=out/'session-01';session.mkdir()
            atomic(session/'report.json',{'commit':'a'*40,'status':'running','stages':{'browser':'passed','evaluation':'running'},'model':{'calls_attempted':2}})
            atomic(session/'agent-plan-attempt-1.json',{'usage':{'prompt_tokens':11,'completion_tokens':3}})
            atomic(session/'rendered-evaluation-attempt-1.json',{'partial_content':'fixture partial','usage':None})
            result=collect(out,'a'*40)
            self.assertEqual(result['status'],'incomplete');self.assertEqual(result['prompt_tokens'],11)
            self.assertEqual(result['calls_returned'],1);self.assertEqual(result['unknown_usage_attempts'],1)
            self.assertEqual(result['paid_api_cost_usd'],0)

    def test_resume_refuses_a_live_owner_before_mutating_journal(self):
        import os
        with tempfile.TemporaryDirectory() as d:
            scheduler=Scheduler.create(self.plan(),['campaign-01'],{},total_ms=90000,session_ms=30000,directory=Path(d)/'run',clock=lambda:1000)
            before=(scheduler.directory/'state.json').read_bytes();(scheduler.directory/'runner.lock').write_text(str(os.getpid()))
            with self.assertRaisesRegex(ValueError,'concurrent resume'):Scheduler.resume(scheduler.directory,clock=lambda:2000)
            self.assertEqual((scheduler.directory/'state.json').read_bytes(),before)

    def test_recovery_does_not_overwrite_a_crash_time_checkpoint(self):
        with tempfile.TemporaryDirectory() as d:
            scheduler=Scheduler.create(self.plan(),['campaign-01'],{},total_ms=90000,session_ms=30000,directory=Path(d)/'run',clock=lambda:1000)
            orphan=scheduler.directory/'checkpoints/0002.json';orphan.write_text('{"fixture_crash_snapshot":true}')
            resumed=Scheduler.resume(scheduler.directory,clock=lambda:2000)
            self.assertEqual(orphan.read_text(),'{"fixture_crash_snapshot":true}')
            self.assertEqual(resumed.state['revision'],3)
