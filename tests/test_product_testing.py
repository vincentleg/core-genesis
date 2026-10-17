"""Synthetic transport fixtures never enter published evidence."""
import json
from pathlib import Path
import tempfile
import unittest
from core_genesis.audience import AudiencePanel, ROLES, CONTEXTS
from core_genesis.budget import RequestBudget
from core_genesis.crusoe import DEFAULT_MODEL

class CompanyFixture:
    def __init__(self, root):
        self.directory=root/'company';self.directory.mkdir()
        self.budget=RequestBudget(root/'budget', history=root/'history')
    def guard(self):
        pass
    @staticmethod
    def write(path, value):
        path.write_text(json.dumps(value))
    def snapshot(self):
        return {'id':'mission-20261017-150000-aaaaaa','status':'complete','artifacts':{'prototype':{'test_report':{'passed':True,'outcome':{'tests_run':7}},'spec':{'title':'Unit fixture'},'files':{'app.py':'unit fixture hash'}}}}

class FeedbackTransport:
    model=DEFAULT_MODEL
    max_retries=0
    last_status=200
    def chat(self,messages,**kwargs):
        response={'category':'usability','position':'conditional','concern':'Unit fixture concern','recommendation':'Validate with actual people','uncertainty':'Synthetic hypothesis'}
        return {'model':self.model,'usage':{'prompt_tokens':5,'completion_tokens':5,'total_tokens':10},'choices':[{'message':{'content':json.dumps(response)}}]}

class ProductTestingTests(unittest.TestCase):
    def test_hundred_person_capacity_requires_separate_five_call_batches_and_independent_contexts(self):
        with tempfile.TemporaryDirectory() as directory:
            panel=AudiencePanel(CompanyFixture(Path(directory)))
            panel.create(100)
            self.assertEqual(panel.snapshot()['reviews'],[])
            panel.prepare_batch();panel.run_batch(FeedbackTransport())
            state=panel.snapshot()
            self.assertEqual(len(state['reviews']),5)
            self.assertEqual(state['status'],'ready')
            self.assertEqual(state['batches'][0]['usage']['physical_requests'],5)
            self.assertEqual(state['analysis']['actual_customers'],0)
            self.assertTrue(all('reviews' not in r['input'] for r in state['reviews']))
            self.assertEqual(len({(role,context) for role in ROLES for context in CONTEXTS}),100)
            with self.assertRaises(ValueError):
                panel.create(101)

    def test_final_partial_batch_stops_at_target_and_never_automatically_continues(self):
        with tempfile.TemporaryDirectory() as directory:
            panel=AudiencePanel(CompanyFixture(Path(directory)));panel.create(7)
            panel.prepare_batch();panel.run_batch(FeedbackTransport())
            self.assertEqual(len(panel.snapshot()['reviews']),5)
            panel.prepare_batch();panel.run_batch(FeedbackTransport())
            state=panel.snapshot();self.assertEqual(len(state['reviews']),7);self.assertEqual(state['status'],'complete')
            self.assertEqual([b['planned_calls'] for b in state['batches']],[5,2])
            self.assertEqual(len({r['persona']['id'] for r in state['reviews']}),7)
            with self.assertRaises(ValueError):
                panel.prepare_batch()
