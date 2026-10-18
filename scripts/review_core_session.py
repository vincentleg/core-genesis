"""Create evidence-linked findings and review proposals without changing CORE."""
import argparse
import hashlib
import json
from pathlib import Path
p=argparse.ArgumentParser()
p.add_argument('session',help='Private company/core-browser/<run>/session-NN directory')
a=p.parse_args()
root=Path(__file__).resolve().parent.parent
session=Path(a.session).resolve()
if not session.is_relative_to(root/'company/core-browser'): p.error('Expected private CORE browser session')
report=json.loads((session/'report.json').read_text())
findings=[]
for i,action in enumerate(report['actions']):
 if action.get('success') is False:
  screenshot=session/action['screenshot']
  findings.append({'id':'F%d'%(len(findings)+1),'kind':'observed_browser_failure','action_index':i,'observation':action.get('error'),
                   'evidence':{'report':'report.json','screenshot':screenshot.name,'sha256':hashlib.sha256(screenshot.read_bytes()).hexdigest() if screenshot.exists() else None},
                   'proposal':'Reproduce in the same environment and investigate; this may be a harness or offline-environment failure.',
                   'status':'awaiting_human_review','verification':{'status':'not_executed','commit':None},'core_write_authorized':False})
for error in report['errors']:
 findings.append({'id':'F%d'%(len(findings)+1),'kind':'observed_page_error','observation':error,'evidence':{'report':'report.json','trace':'trace.zip'},'proposal':'Reproduce and inspect the captured stack before proposing a code change.','status':'awaiting_human_review','verification':{'status':'not_executed','commit':None},'core_write_authorized':False})
summary_file=session.parent/'summary.json'
summary=json.loads(summary_file.read_text()) if summary_file.exists() else {}
if summary.get('error'):
 findings.append({'id':'F%d'%(len(findings)+1),'kind':'harness_execution_incomplete','observation':summary['error'],
                  'evidence':{'summary':'../summary.json','report':'report.json'},
                  'proposal':'Investigate the HQ controller and runtime limit; do not infer a CORE defect.',
                  'status':'awaiting_human_review','verification':{'status':'not_executed','commit':None},'core_write_authorized':False})
output=session/'review.json'
if output.exists(): p.error('Review already exists; retained unchanged')
output.write_text(json.dumps({'target_commit':report['commit'],'environment':report['environment'],'findings':findings,'workflow':['read_core','test_core','collect_evidence','identify_problems','propose_improvements','verify_changes','request_human_approval'],'verification_status':'No proposed CORE change implemented or verified','authority':'Read-only CORE; no merge, deploy, publication or writes'},indent=2))
print('Review saved:',output,'Findings:',len(findings))
