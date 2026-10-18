"""Write a preparation artifact only; no browser, network, inference, recruitment or CORE writes."""
import argparse,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from core_genesis.browser_campaign import ROOT,prepare
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--commit',required=True);a=p.parse_args()
    plan=prepare(a.commit);target=ROOT/'testing/core-v92-30-campaign.json'
    target.write_text(json.dumps(plan,indent=2)+'\n')
    print(json.dumps({'artifact':str(target),'planned_sessions':len(plan['sessions']),'sessions_launched_by_preparation':0,'execution_enabled':False,'paid_api_cost_usd':0}))
