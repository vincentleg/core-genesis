"""Small status projection. Never publish source bodies, participant data, traces or model prompts."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent

def hq_status():
    inspection=ROOT/'company/core-inspection.json'
    source=json.loads(inspection.read_text()) if inspection.exists() else {}
    sessions=[]
    for p in sorted((ROOT/'company/core-browser').glob('*/summary.json')):
        record=json.loads(p.read_text())
        sessions.append({k:record.get(k) for k in ['mode','model','commit','requested','completed','successes','passed','runtime_ms','model_calls','cost_usd','sessions']})
        sessions[-1]['sessions']=[{k:r.get(k) for k in ['id','passed','status','task_completion']} for r in record.get('sessions',[])]
        sessions[-1]['run']=p.parent.name
        if not record.get('completed'):
            partial=[json.loads(f.read_text()) for f in p.parent.glob('session-*/report.json')]
            sessions[-1]['model_calls_attempted']=sum(r.get('model',{}).get('calls',0) for r in partial)
            sessions[-1]['model_calls']=sessions[-1]['model_calls_attempted']
            sessions[-1]['model']=json.loads((p.parent/'config.json').read_text()).get('model') if (p.parent/'config.json').exists() else None
            sessions[-1]['partial_actions']=sum(len(r.get('actions',[])) for r in partial)
            sessions[-1]['error']=record.get('error')
    pilot={'planned_sessions':10,'status':'prepared_not_executed','concurrency':1,'paid_inference_allowed':False}
    aggregates=sorted((ROOT/'company/core-pilots').glob('*/aggregate.json'))
    if aggregates:
        actual=json.loads(aggregates[-1].read_text())
        pilot.update({k:actual.get(k) for k in ['attempted','completed','incomplete','successes','wall_elapsed_ms','model_calls','model_calls_completed','prompt_tokens','completion_tokens','evaluations_completed','screenshots','finalized_traces']})
        pilot['status']='executed_with_limitations'
        pilot['scale_ready']=False
    model=ROOT/'company/core-browser/model-preflight.json'
    return {'brand':'CORE HQ','core_access':'read_only','source':{k:source.get(k) for k in ['requested_ref','commit','checkout_branch','checkout_dirty','retrieved_at','environment','file_count']},
            'complete_source_files_read':len(source.get('sources',[])),
            'production':source.get('public_production',{'url':'https://creationofrebornearth.com','commit':None,'status':'Older CORE per founder; local V9.2 not deployed'}),
            'sessions':sessions,'local_model':json.loads(model.read_text()) if model.exists() else {'status':'not_checked'},
            'pilot':pilot,
            'human_testing':{'verified_participants':0,'status':'No participation independently verified. Import support implemented; no recruitment.'},
            'authority':'No CORE writes, merges, pushes or deployments. Changes require human review.',
            'historical_evidence':'Campus replay and synthetic campaigns describe the hackathon and separate Local Solutions prototype, not CORE V9.2 testing.'}
