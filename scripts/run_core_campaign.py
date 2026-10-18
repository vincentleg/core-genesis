"""Explicit, bounded campaign invocations. Default is inspection only; never runs all cases implicitly."""
import argparse,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from core_genesis.campaign_scheduler import ROOT,CAMPAIGNS,Scheduler,load_plan,earth_gate

def main():
    p=argparse.ArgumentParser();p.add_argument('--plan',default=str(ROOT/'testing/core-v92-30-campaign.json'));p.add_argument('--execute',action='store_true');p.add_argument('--limit',type=int);p.add_argument('--session-ids');p.add_argument('--earth-gate');p.add_argument('--resume');p.add_argument('--total-time-seconds',type=int);p.add_argument('--session-time-seconds',type=int)
    a=p.parse_args()
    if not a.execute:
        plan=load_plan(a.plan);print(json.dumps({'status':'prepared_only','planned':len(plan['sessions']),'launched':0,'execute':False}));return 0
    if not a.limit or not 1<=a.limit<=30:p.error('--execute requires an explicit --limit 1–30')
    if a.resume:
        if any([a.session_ids,a.earth_gate,a.total_time_seconds,a.session_time_seconds]):p.error('Resume cannot reset selection, provenance or budgets')
        directory=(CAMPAIGNS/a.resume).resolve()
        if directory.parent!=CAMPAIGNS.resolve():p.error('Campaign run ID required')
        scheduler=Scheduler.resume(directory)
    else:
        if not a.session_ids or not a.earth_gate:p.error('Execution requires explicit --session-ids and verified --earth-gate')
        plan=load_plan(a.plan);gate=earth_gate(a.earth_gate,plan['core_commit'])
        scheduler=Scheduler.create(plan,a.session_ids.split(','),gate,total_ms=(a.total_time_seconds or 3600)*1000,session_ms=(a.session_time_seconds or 180)*1000)
    state=scheduler.run(a.limit);print(json.dumps({'campaign':scheduler.directory.name,'status':state['status'],'totals':state['totals'],'core_commit':state['core_commit']}));return 0 if not state['totals']['failed'] and not state['totals']['incomplete'] else 1
if __name__=='__main__':sys.exit(main())
