"""Explicit metadata inspection only; no chat/completion request."""
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from core_genesis.crusoe import CrusoeClient

if __name__ == "__main__":
    client = CrusoeClient(max_retries=0, timeout=20)
    models = client.list_models()
    matches = [model for model in models if "nemotron" in model.get("id", "").lower() and "lightning" in model.get("id", "").lower()]
    print(json.dumps({"kind": "provider_model_metadata", "http_status": client.last_status, "chat_requests": 0, "matching_models": matches}, indent=2))
