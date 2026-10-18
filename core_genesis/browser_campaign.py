"""Plan generation and legacy bookkeeping. Execution lives in campaign_scheduler."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parent.parent
CATEGORIES=['core_product_defect','hq_harness_defect','environment_network_limitation','model_evaluation_failure','subjective_ux_hypothesis','needs_triage']

def prepare(commit):
    if not re.fullmatch('[a-f0-9]{40}',commit):raise ValueError('Exact CORE SHA required')
    source=ROOT/'testing/core-v92-journeys.json'
    definitions=json.loads(source.read_text())['journeys']
    if len(definitions)!=30 or len({d['id'] for d in definitions})!=30:raise ValueError('Thirty unique journeys required')
    sessions=[]
    for i,d in enumerate(definitions,1):
        sessions.append({**d,'session_id':f'campaign-{i:02d}','definition_only':True,
                         'locale':'fr' if d['variant']=='room-fr' else 'en','viewport':{'width':390,'height':844} if d['scenario']=='keyboard' else {'width':1440,'height':1000},
                         'mode':'local-agent','model':'qwen3:8b','core_commit':commit,
                         'single_session_command':['python3','scripts/test_core.py','--suite','journey','--scenario',d['scenario'],'--variant',d['variant'],'--sessions','1','--mode','local-agent','--model','qwen3:8b','--time-budget-seconds','180','--ref',commit]+(['--map-network','public-assets'] if d['requires_map_assets'] else [])})
    return {'schema_version':1,'campaign_id':'core-v92-diverse-30','status':'prepared_definition','execution_enabled':False,
            'campaign_executor_implemented':True,'results_location':'company/core-campaigns; this definition is not a live result ledger','human_participants':0,'core_access':'read_only','core_repo':'~/core','development_ref':'v9.2/earth-first','core_commit':commit,
            'production_tested':False,'model_provider':'http://127.0.0.1:11434','model':'qwen3:8b','model_downloads':False,'paid_api_cost_limit_usd':0,
            'concurrency':1,'max_sessions':30,'max_session_runtime_ms':180000,'max_campaign_runtime_ms':3600000,'cleanup_reserve_ms':12000,
            'inference_limits':{'max_attempts_per_stage':2,'max_calls_per_session':4,'stage_limit_ms':90000,'attempt_limits_ms':[60000,25000],'context_tokens':8192,'max_output_tokens_per_attempt':[512,384],'usage_for_interrupted_calls':'unknown; never estimate as zero'},
            'evidence':{'private_root':'company/core-browser','required':['config','CORE provenance','harness hashes','actual actions and assertion outcomes','screenshots or explicit capture failures','trace or explicit finalization failure','page/console/HTTP/request-failure logs','model input/output/partial streams','per-stage results','runtime','returned tokens and unknown usage','cost','sha256 manifest']},
            'classification':{'categories':CATEGORIES,'automatic_core_defect_confirmation':False,'ux_notes':'heuristic_only_requires_human_validation'},
            'recovery':{'stop_new_sessions_on_signal':True,'abort_local_inference':True,'preserve_partial_results':True,'finalize_trace_within_original_deadline':True,'resume_only_never_started_ids':True,'never_reset_original_deadline':True,'never_replay_an_attempt_to_improve_counts':True,'checkpoint_helper':'campaign_scheduler.Scheduler durable policy and checkpoints'},
            'execution_gates':['Explicit human approval for executing this prepared campaign','Passing corrected real AI Earth browser gate with verified capture hashes','Review single-journey assertions and unvalidated variants','Explicit subset, invocation limit and fixed total/session budgets; full 30 not authorized by preparation','Record browser/model versions and target commit before launch'],
            'journey_catalog_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'sessions':sessions}

def pending_sessions(plan,records,*,started_at_ms,now_ms):
    """Never relaunch attempted IDs. Deadline is supplied from the original durable checkpoint."""
    ids={s['session_id'] for s in plan['sessions']}
    seen=set()
    for record in records:
        sid=record['session_id']
        if sid not in ids or sid in seen or record.get('core_commit')!=plan['core_commit']:
            raise ValueError('Unknown, duplicate or wrong-commit checkpoint')
        seen.add(sid)
    deadline=started_at_ms+plan['max_campaign_runtime_ms']
    remaining=max(0,deadline-now_ms)
    pending=[s['session_id'] for s in plan['sessions'] if s['session_id'] not in seen]
    return {'attempted':len(seen),'remaining_ms':remaining,'deadline_ms':deadline,'unstarted':pending,
            'eligible_after_approval':pending if remaining>15000 else [],'execution_enabled':False,
            'note':'Bookkeeping output is not authorization or an executor; attempted failures/interrupted sessions are not replayed.'}
