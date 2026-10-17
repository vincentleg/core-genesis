"""Run one real experiment; saves an auditable JSON artifact."""
import json
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from core_genesis.evolution import EvolutionEngine, DEFAULT_OBJECTIVE

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--fresh", action="store_true", help="Start a new baseline experiment instead of continuing the last verified team")
    parser.add_argument("--objective", default=DEFAULT_OBJECTIVE)
    parser.add_argument("--generations", type=int, choices=[1, 2, 3], default=3)
    parser.add_argument("--seed", type=int, help="Optional reproducible suite seed")
    args = parser.parse_args()
    engine = EvolutionEngine(fresh=args.fresh)
    engine.start(objective=args.objective, generations=args.generations, seed=args.seed)
    print("Running real Crusoe experiment →", engine.path, flush=True)
    engine.run()
    state = engine.snapshot()
    print(json.dumps({key: state.get(key) for key in ("status", "inference_calls", "total_tokens", "decisions", "error")}, indent=2))
    sys.exit(0 if state["status"] == "complete" else 1)
