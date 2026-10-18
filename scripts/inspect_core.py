"""Record local CORE provenance privately. No API calls."""
import argparse
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from core_genesis.core_access import inspect_core
p = argparse.ArgumentParser()
p.add_argument('--repo')
p.add_argument('--ref')
p.add_argument('--output', default='company/core-inspection.json')
a = p.parse_args()
s = inspect_core(a.repo, a.ref)
out = Path(a.output).resolve()
root = Path(__file__).resolve().parent.parent / 'company'
if not out.is_relative_to(root):
    p.error('Inspection bodies must stay in private company/ storage')
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(s, indent=2))
print(json.dumps({k:s[k] for k in ['requested_ref','commit','checkout_branch','checkout_dirty','file_count','architecture','limitations']}))
print('Full source files read:', len(s['sources']))
