"""Verify real mission artifacts without inference, retrieval or execution of CORE."""
import argparse
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from core_genesis.mission_replay import replay_mission

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("record", type=Path)
    args = parser.parse_args()
    print(json.dumps(replay_mission(json.loads(args.record.read_text())), indent=2))
