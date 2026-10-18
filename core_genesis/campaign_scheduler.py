"""Sequential local-browser campaign execution with durable, bounded, non-replaying journals."""
import hashlib
import json
import math
import os
from pathlib import Path
import re
import signal
import subprocess
import sys
import time
import uuid
from datetime import datetime, timezone
from .browser_campaign import ROOT

CAPTURES=ROOT/'company/core-browser'
CAMPAIGNS=ROOT/'company/core-campaigns'

def sha(file):return hashlib.sha256(file.read_bytes()).hexdigest()
def atomic(file,value):
    temp=file.with_suffix(file.suffix+'.tmp');temp.write_text(json.dumps(value,indent=2)+'\n');os.replace(temp,file)
def plan_hash(plan):return hashlib.sha256(json.dumps(plan,sort_keys=True).encode()).hexdigest()
def load_plan(file):
    plan=json.loads(Path(file).read_text());specs=json.loads((ROOT/'testing/core-v92-journeys.json').read_text())['journeys']
    known={(s['scenario'],s['variant']) for s in specs}
    if not re.fullmatch('[a-f0-9]{40}',plan.get('core_commit','')) or plan.get('model')!='qwen3:8b' or plan.get('model_provider')!='http://127.0.0.1:11434':raise ValueError('Exact commit and installed local Qwen3 only')
    if plan.get('paid_api_cost_limit_usd')!=0 or plan.get('concurrency')!=1:raise ValueError('Sequential zero-paid-cost policy required')
    if not 30000<=plan.get('max_session_runtime_ms',0)<=180000 or not 30000<=plan.get('max_campaign_runtime_ms',0)<=3600000:raise ValueError('Invalid time limits')
    sessions=plan['sessions']
    if not 1<=len(sessions)<=30 or len({s['session_id'] for s in sessions})!=len(sessions):raise ValueError('One to thirty unique session IDs required')
    if plan['journey_catalog_sha256']!=sha(ROOT/'testing/core-v92-journeys.json'):raise ValueError('Journey catalog changed; review the plan')
    for s in sessions:
        if (s['scenario'],s['variant']) not in known or s['core_commit']!=plan['core_commit'] or s['mode']!='local-agent' or s['model']!='qwen3:8b':raise ValueError('Invalid campaign session')
    return plan

def verify_capture(directory):
    hashes=json.loads((directory/'checksums.json').read_text())
    for name,expected in hashes.items():
        file=(directory/name).resolve()
        if not file.is_relative_to(directory.resolve()) or not file.is_file() or sha(file)!=expected:raise ValueError('Capture checksum mismatch: '+name)
    for name in ['config.json','summary.json','session-01/report.json']:
        if name not in hashes:raise ValueError('Incomplete capture manifest: '+name)
    return sha(directory/'checksums.json')

def earth_gate(run,commit):
    if not re.fullmatch(r'\d{8}T\d{6}Z-[a-f0-9]{6}',run):raise ValueError('Invalid Earth gate capture')
    directory=CAPTURES/run;digest=verify_capture(directory)
    report=json.loads((directory/'session-01/report.json').read_text());config=json.loads((directory/'config.json').read_text())
    required=['imagery','ai_globe_interaction','corrected_mission_selector','location']
    if config['commit']!=commit or config['suite']!='earth-agent' or config['model']!='qwen3:8b' or not report.get('ai_directed') or not report.get('browser_tasks_passed') or not all(report['tasks'].get(k) for k in required):raise ValueError('Passing real AI Earth browser gate required')
    if report.get('earth_interaction',{}).get('forced') is not False:raise ValueError('Unforced actual interaction required')
    return {'capture':run,'manifest_sha256':digest,'browser_pass':True,'evaluation_status':report['stages']['evaluation']}

def command_for(plan,spec,capture,budget_seconds):
    # Never execute command text supplied in a plan.
    command=[sys.executable,str(ROOT/'scripts/test_core.py'),'--suite','journey','--scenario',spec['scenario'],'--variant',spec['variant'],'--mode','local-agent','--model','qwen3:8b','--sessions','1','--run-id',capture,'--time-budget-seconds',str(budget_seconds),'--ref',plan['core_commit']]
    viewport=spec.get('viewport',{'width':1440,'height':1000})
    command+=['--viewport',f"{viewport['width']}x{viewport['height']}"]
    if spec['requires_map_assets']:command+=['--map-network','public-assets']
    return command

def collect(directory,commit):
    result={'capture':directory.name,'status':'incomplete','browser_status':'unknown','evaluation_status':'unknown','evidence_status':'partial','calls_attempted':0,'calls_returned':0,'prompt_tokens':0,'completion_tokens':0,'unknown_usage_attempts':0,'paid_api_cost_usd':0}
    report_file=directory/'session-01/report.json'
    if report_file.exists():
        r=json.loads(report_file.read_text());result.update(browser_status=r.get('stages',{}).get('browser','unknown'),evaluation_status=r.get('stages',{}).get('evaluation','unknown'),failure=r.get('failure'),failure_category=r.get('failure_category'),infrastructure_stop=r.get('infrastructure_stop',False),runtime_ms=r.get('runtime_ms'),raw_status=r.get('status'),trace_retained=(directory/'session-01/trace.zip').exists(),screenshots=len(list(directory.glob('session-*/*.png'))))
        attempts=[json.loads(f.read_text()) for f in directory.glob('session-*/*-attempt-*.json')]
        result['calls_attempted']=max(len(attempts),r.get('model',{}).get('calls_attempted',0))
        for a in attempts:
            usage=a.get('usage')
            if usage:
                result['calls_returned']+=1;result['prompt_tokens']+=usage.get('prompt_tokens') or 0;result['completion_tokens']+=usage.get('completion_tokens') or 0
        result['unknown_usage_attempts']=result['calls_attempted']-sum(bool(a.get('usage')) and all(a['usage'].get(k) is not None for k in ['prompt_tokens','completion_tokens']) for a in attempts)
        if r.get('commit')!=commit:result.update(status='failed',failure='CORE provenance mismatch',failure_category='hq_harness_defect');return result
    else:return result
    try:
        result['manifest_sha256']=verify_capture(directory)
        config=json.loads((directory/'config.json').read_text());summary=json.loads((directory/'summary.json').read_text())
        if config.get('commit')!=commit or summary.get('commit')!=commit or config.get('model')!='qwen3:8b' or config.get('max_cost_usd')!=0:raise ValueError('Capture target/model/cost provenance mismatch')
        result['evidence_status']='finalized'
        if r.get('status') in ['running','interrupted','incomplete_budget'] or not r.get('ai_directed'):return result
        result['status']='completed' if r.get('passed') and result['trace_retained'] and result['calls_returned']>0 else 'failed'
    except (OSError,ValueError,KeyError) as error:
        result['evidence_error']=str(error)
        if 'provenance mismatch' in str(error):result.update(status='failed',failure='CORE provenance mismatch',failure_category='hq_harness_defect')
    return result

class Scheduler:
    def __init__(self,directory,state,plan,*,clock=None,runner=None):
        self.directory=Path(directory);self.state=state;self.plan=plan;self.clock=clock or (lambda:int(time.time()*1000));self.runner=runner or self.run_child;self.stop_requested=False;self.child=None
    @classmethod
    def create(cls,plan,selected,gate,*,total_ms,session_ms,directory=None,clock=None,runner=None):
        valid={s['session_id'] for s in plan['sessions']}
        if not selected or len(selected)!=len(set(selected)) or not set(selected)<=valid:raise ValueError('Explicit unique selected IDs required')
        if not 30000<=total_ms<=plan['max_campaign_runtime_ms'] or not 30000<=session_ms<=plan['max_session_runtime_ms']:raise ValueError('Limits may only reduce plan caps')
        directory=Path(directory or CAMPAIGNS/(datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ-')+uuid.uuid4().hex[:6]));directory.mkdir(parents=True,exist_ok=False)
        now=(clock or (lambda:int(time.time()*1000)))()
        state={'schema_version':1,'status':'ready','core_commit':plan['core_commit'],'plan_sha256':plan_hash(plan),'selected_ids':selected,'started_at_ms':now,'deadline_ms':now+total_ms,'last_updated_ms':now,'session_limit_ms':session_ms,'records':[],'earth_gate':gate,'human_participants':0,'execution_authorization':'explicit CLI subset/limit','revision':0}
        atomic(directory/'plan.json',plan)
        policy={k:state[k] for k in ['core_commit','plan_sha256','selected_ids','started_at_ms','deadline_ms','session_limit_ms']}
        atomic(directory/'policy.json',policy);state['policy_sha256']=sha(directory/'policy.json')
        obj=cls(directory,state,plan,clock=clock,runner=runner);obj.persist('created');return obj
    @classmethod
    def resume(cls,directory,*,clock=None,runner=None):
        directory=Path(directory)
        lock=directory/'runner.lock'
        if lock.exists():
            try:os.kill(int(lock.read_text()),0)
            except ProcessLookupError:pass
            else:raise ValueError('Another scheduler is active; refusing concurrent resume')
        state=json.loads((directory/'state.json').read_text());plan=load_plan(directory/'plan.json')
        policy=json.loads((directory/'policy.json').read_text())
        if state.get('policy_sha256')!=sha(directory/'policy.json') or any(state.get(k)!=v for k,v in policy.items()):raise ValueError('Original campaign policy/deadline changed')
        if len({r['session_id'] for r in state['records']})!=len(state['records']) or any(r['session_id'] not in state['selected_ids'] or r.get('core_commit')!=plan['core_commit'] or not re.fullmatch(r'\d{8}T\d{6}Z-[a-f0-9]{6}',r.get('capture','')) for r in state['records']):raise ValueError('Invalid session checkpoint')
        if state['plan_sha256']!=plan_hash(plan):raise ValueError('Immutable campaign plan changed')
        if state.get('earth_gate',{}).get('capture'):
            checked=earth_gate(state['earth_gate']['capture'],plan['core_commit'])
            if checked['manifest_sha256']!=state['earth_gate']['manifest_sha256']:raise ValueError('Earth gate evidence changed')
        now=(clock or (lambda:int(time.time()*1000)))()
        if now<state['last_updated_ms']:raise ValueError('Clock moved backwards; refusing to extend budget')
        for record in state['records']:
            if record['status']=='running':
                pid=record.get('child_pid')
                if pid:
                    try:os.kill(pid,0)
                    except ProcessLookupError:pass
                    else:raise ValueError('Recorded child is still alive; refusing concurrent resume')
                recovered=collect(CAPTURES/record['capture'],plan['core_commit']);record.update(recovered,recovered=True)
                if record['status']=='running':record['status']='incomplete'
        obj=cls(directory,state,plan,clock=clock,runner=runner);obj.persist('resumed_without_replaying_attempts');return obj
    def persist(self,event):
        previous_revisions=[int(f.stem) for f in (self.directory/'checkpoints').glob('*.json') if f.stem.isdigit()]
        self.state['revision']=max([self.state['revision'],*previous_revisions])+1;self.state['last_updated_ms']=max(self.clock(),self.state['last_updated_ms'])
        folder=self.directory/'checkpoints';folder.mkdir(exist_ok=True)
        snapshot={**self.state,'event':event};atomic(folder/f"{self.state['revision']:04d}.json",snapshot);atomic(self.directory/'state.json',self.state)
    def totals(self):
        records=self.state['records'];statuses=['completed','failed','incomplete','running']
        return {'selected':len(self.state['selected_ids']),'attempted':len(records),**{s:sum(r['status']==s for r in records) for s in statuses},'unstarted':len(self.state['selected_ids'])-len(records),**{k:sum(r.get(k,0) for r in records) for k in ['calls_attempted','calls_returned','prompt_tokens','completion_tokens','unknown_usage_attempts','paid_api_cost_usd']},'human_participants':0}
    def interrupt(self,*_):
        self.stop_requested=True
    def run_child(self,spec,capture,deadline_ms):
        remaining=deadline_ms-self.clock();seconds=max(30,math.floor(remaining/1000))
        command=command_for(self.plan,spec,capture,seconds)
        log=self.directory/(spec['session_id']+'.log')
        with log.open('wb') as output:
            self.child=subprocess.Popen(command,cwd=ROOT,stdout=output,stderr=subprocess.STDOUT,start_new_session=True)
            self.state['records'][-1]['child_pid']=self.child.pid;self.persist('child_started')
            while self.child.poll() is None:
                if self.stop_requested or self.clock()>=deadline_ms-12000:
                    self.child.terminate()
                    try:self.child.wait(timeout=max(0.01,min(10,(deadline_ms-self.clock())/1000)))
                    except subprocess.TimeoutExpired:
                        
                        try:os.killpg(self.child.pid,signal.SIGKILL)
                        except ProcessLookupError:pass
                        self.child.wait(timeout=1)
                    break
                try:self.child.wait(timeout=0.25)
                except subprocess.TimeoutExpired:pass
        self.child=None
        return collect(CAPTURES/capture,self.plan['core_commit'])
    def run(self,limit):
        if not 1<=limit<=30:raise ValueError('Explicit invocation limit of 1–30 required')
        lock=self.directory/'runner.lock'
        try:
            fd=os.open(lock,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600);os.write(fd,str(os.getpid()).encode());os.close(fd)
        except FileExistsError:
            pid=int(lock.read_text())
            try:os.kill(pid,0)
            except ProcessLookupError:lock.unlink();return self.run(limit)
            raise ValueError('Another scheduler owns this campaign')
        previous={sig:signal.getsignal(sig) for sig in [signal.SIGTERM,signal.SIGINT]}
        for sig in previous:signal.signal(sig,self.interrupt)
        anchor_wall=self.clock();anchor_mono=time.monotonic();original_clock=self.clock
        self.clock=lambda:max(original_clock(),anchor_wall+int((time.monotonic()-anchor_mono)*1000))
        launched=0
        try:
            seen={r['session_id'] for r in self.state['records']};specs={s['session_id']:s for s in self.plan['sessions']}
            for sid in self.state['selected_ids']:
                if sid in seen:continue
                if self.stop_requested or launched>=limit or self.clock()>=self.state['deadline_ms']-30000:break
                capture=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ-')+uuid.uuid4().hex[:6]
                deadline=min(self.clock()+self.state['session_limit_ms'],self.state['deadline_ms'])
                record={'session_id':sid,'core_commit':self.plan['core_commit'],'scenario':specs[sid]['id'],'status':'running','capture':capture,'started_at_ms':self.clock(),'deadline_ms':deadline};self.state['records'].append(record);self.persist('reserved_before_launch');launched+=1
                try:record.update(self.runner(specs[sid],capture,deadline))
                except Exception as error:record.update(status='incomplete',scheduler_error=str(error));self.stop_requested=True
                record['finished_at_ms']=self.clock();self.persist('result_collected')
                if record.get('failure')=='CORE provenance mismatch' or record.get('infrastructure_stop'):self.stop_requested=True
            total=self.totals();self.state.update(totals=total,status='interrupted' if self.stop_requested else 'finished' if total['unstarted']==0 else 'budget_reached' if self.clock()>=self.state['deadline_ms']-30000 else 'invocation_limit_reached');self.persist('invocation_finished')
            atomic(self.directory/'checksums.json',{str(f.relative_to(self.directory)):sha(f) for f in self.directory.rglob('*') if f.is_file() and f.name not in ['checksums.json','runner.lock']})
            return self.state
        finally:
            self.clock=original_clock
            for sig,handler in previous.items():signal.signal(sig,handler)
            lock.unlink(missing_ok=True)
