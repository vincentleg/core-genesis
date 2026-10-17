"""Build a strictly static, secret-free replay site. No inference or deploy calls."""
import json
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from core_genesis.crusoe import load_api_key

RECORDS = {"story": "20261017-123548-c377d6", "continuation": "20261017-123736-61ea83", "verified": "20261017-124001-ae2c9e"}

def build():
    out = ROOT / "public"
    out.mkdir(exist_ok=True)
    for name in ("world.html", "world.css", "world.js", "campus.js", "economy.js"):
        shutil.copyfile(ROOT / "web" / name, out / ("index.html" if name == "world.html" else name))
    shutil.copytree(ROOT / "web/vendor", out / "vendor", dirs_exist_ok=True)
    evidence = out / "evidence"
    evidence.mkdir(exist_ok=True)
    records = []
    for name, identity in RECORDS.items():
        record = json.loads((ROOT / "experiments" / (identity + ".json")).read_text())
        (evidence / (name + ".json")).write_text(json.dumps(record, separators=(",", ":")))
        records.append({"id": identity, "file": name + ".json", "status": record["status"]})
    (evidence / "manifest.json").write_text(json.dumps({"records": records, "mode": "VERIFIED REPLAY", "external_api_calls": 0}))
    (out / "capabilities.json").write_text(json.dumps({"live": False, "mode": "public_static_replay", "note": "Public experience has no inference endpoint. Run the Python server locally for budget-controlled live evolution."}))
    (out / "vercel.json").write_text(json.dumps({"version": 2, "cleanUrls": True, "headers": [{"source": "/(.*)", "headers": [{"key": "X-Content-Type-Options", "value": "nosniff"}, {"key": "Content-Security-Policy", "value": "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'"}]}]}))
    (out / ".vercelignore").write_text(".vercel\n")
    try:
        secret = load_api_key().encode()
    except RuntimeError:
        secret = None
    files = [p for p in out.rglob("*") if p.is_file() and ".vercel" not in p.parts]
    if secret and any(secret in p.read_bytes() for p in files):
        raise RuntimeError("Secret scan rejected publication")
    forbidden = [p for p in files if p.name.startswith(".env") or p.suffix == ".py"]
    if forbidden:
        raise RuntimeError("Unexpected server/credential files in static output")
    print("Static world built: %d files; genuine evidence; no inference endpoints or credentials." % len(files))

if __name__ == "__main__":
    build()
