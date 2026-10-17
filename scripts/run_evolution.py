"""Run one real experiment; saves an auditable JSON artifact."""
import json
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from core_genesis.engine import Engine

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--fresh", action="store_true", help="Start a new baseline experiment instead of continuing the last verified team")
    args = parser.parse_args()
    engine = Engine(fresh=args.fresh)
    engine.start()
    print("Running real Crusoe experiment →", engine.path, flush=True)
    engine.run()
    state = engine.snapshot()
    print(json.dumps({key: state.get(key) for key in ("status", "inference_calls", "total_tokens", "decisions", "error")}, indent=2))
    sys.exit(0 if state["status"] == "complete" else 1)
