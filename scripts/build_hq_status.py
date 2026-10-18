"""Export only the safe HQ status projection; no inference, historical rebuild, or deployment."""
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from core_genesis.hq_status import hq_status
out=Path(__file__).resolve().parent.parent/'public/hq-status.json'
out.write_text(json.dumps(hq_status(),indent=2))
print('Safe status exported:',out)
