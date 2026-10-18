"""Preparation and interruption fixtures only; never browser-session evidence."""
import unittest
from core_genesis.browser_campaign import prepare,pending_sessions

class CampaignTests(unittest.TestCase):
    def test_prepared_definition_has_distinct_journeys_and_no_automatic_execution(self):
        plan=prepare('a'*40)
        self.assertEqual(len(plan['sessions']),30)
        self.assertEqual(len({s['id'] for s in plan['sessions']}),30)
        self.assertEqual(len({s['scenario'] for s in plan['sessions']}),10)
        self.assertTrue(all(s['definition_only'] and 'status' not in s for s in plan['sessions']))
        self.assertFalse(plan['execution_enabled']);self.assertTrue(plan['campaign_executor_implemented'])
        self.assertEqual(plan['max_campaign_runtime_ms'],3600000)
        self.assertTrue(all(s['max_runtime_ms']<=180000 for s in plan['sessions']))
        self.assertTrue(all('--sessions' in s['single_session_command'] and s['single_session_command'][s['single_session_command'].index('--sessions')+1]=='1' for s in plan['sessions']))

    def test_interrupted_attempt_is_not_replayed_and_original_deadline_stays_fixed(self):
        plan=prepare('a'*40)
        records=[{'session_id':'campaign-01','core_commit':'a'*40,'status':'interrupted'}]
        result=pending_sessions(plan,records,started_at_ms=1000,now_ms=2000)
        self.assertNotIn('campaign-01',result['eligible_after_approval'])
        self.assertEqual(result['deadline_ms'],3601000)
        expired=pending_sessions(plan,records,started_at_ms=1000,now_ms=3601001)
        self.assertEqual(expired['remaining_ms'],0);self.assertEqual(expired['eligible_after_approval'],[])
        self.assertEqual(len(expired['unstarted']),29)

    def test_invalid_or_duplicate_checkpoint_is_rejected(self):
        plan=prepare('a'*40);r={'session_id':'campaign-01','core_commit':'a'*40}
        for records in [[r,r],[{'session_id':'campaign-31','core_commit':'a'*40}],[{'session_id':'campaign-01','core_commit':'b'*40}]]:
            with self.assertRaises(ValueError):pending_sessions(plan,records,started_at_ms=0,now_ms=0)
