"""Validate a consented platform export after mapping to the local schema; no network."""
import argparse
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from core_genesis.human_testing import validate_human_record
p=argparse.ArgumentParser()
p.add_argument('input')
p.add_argument('--output',default='company/human-testing/import.json')
a=p.parse_args()
result=validate_human_record(json.loads(Path(a.input).read_text()))
out=Path(a.output).resolve()
root=Path(__file__).resolve().parent.parent/'company/human-testing'
if not out.is_relative_to(root): p.error('Human records must stay in private company/human-testing/')
out.parent.mkdir(parents=True,exist_ok=True)
if out.exists(): p.error('Refusing to overwrite an existing study; choose a new output')
out.write_text(json.dumps(result,indent=2))
print(json.dumps({'actual_human_participants':result['actual_human_participants'],'task_metrics':result['task_metrics'],'verification':result['verification']}))
