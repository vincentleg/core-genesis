"""Publish only the static HQ status interface; never deploy operational records."""
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'dist/hq'
OUT.mkdir(parents=True, exist_ok=True)
ALLOWED = ('hq.html', 'hq.css', 'hq.js', 'hq-status.json')
for name in ALLOWED:
    shutil.copyfile(ROOT / 'public' / name, OUT / name)
shutil.copyfile(ROOT / 'public/hq.html', OUT / 'index.html')
assert {p.name for p in OUT.iterdir()} == {*ALLOWED, 'index.html'}, 'Unexpected deployment files'
print('Static HQ output: five allowlisted files; no APIs, private evidence or backend.')
