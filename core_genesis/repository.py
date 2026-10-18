"""Bounded public GitHub GETs. Never checks out, executes or writes to CORE."""
import datetime as dt
import hashlib
import json
from pathlib import PurePosixPath
import re
import urllib.parse
import urllib.request
import http.client
import urllib.error

REPO = "vincentleg/core"
API = "https://api.github.com/repos/" + REPO
DENIED = {".git", "node_modules", "vendor", "dist", "build", ".aws", "coverage"}


def safe_path(path):
    parts = PurePosixPath(path).parts
    return bool(parts) and not path.startswith("/") and ".." not in parts and not any(
        part in DENIED or part.startswith(".env") or re.search(r"(secret|credential|private.key|token|password)", part, re.I)
        for part in parts) and PurePosixPath(path).suffix.lower() in {".md", ".json", ".js", ".mjs", ".jsx", ".ts", ".tsx", ".py", ".yml", ".yaml"}


def read_public(url, limit, guard=lambda: None):
    guard()
    if not url.startswith((API + "/", API + "?", "https://raw.githubusercontent.com/" + REPO + "/")) and url != API:
        raise ValueError("Only the fixed public CORE repository may be retrieved")
    request = urllib.request.Request(url, headers={"User-Agent": "CORE-HQ-read-only-research", "Accept": "application/vnd.github+json"})
    for attempt in range(2):
        guard()
        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                if response.geturl().split("/")[2] not in {"api.github.com", "raw.githubusercontent.com"}:
                    raise ValueError("Unexpected GitHub redirect")
                data = response.read(limit + 1)
                if len(data) > limit:
                    raise ValueError("GitHub response exceeds the bounded retrieval limit")
                return data
        except (http.client.IncompleteRead, urllib.error.URLError):
            if attempt:
                raise


def fetch_snapshot(guard=lambda: None, read=read_public, previous=None):
    requests = []
    def get(url, limit=1024 * 1024, raw=False):
        data = read(url, limit, guard)
        requests.append({"method": "GET", "url": url, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()})
        return data.decode("utf-8") if raw else json.loads(data)
    metadata = get(API)
    if metadata.get("private") or metadata.get("full_name", "").lower() != REPO:
        raise ValueError("CORE must be the expected public repository")
    # Branch metadata avoids downloading a potentially huge commit patch payload.
    branch = get(API + "/branches/" + urllib.parse.quote(metadata["default_branch"], safe=""))
    sha = branch["commit"]["sha"]
    if not re.fullmatch(r"[0-9a-f]{40}", sha):
        raise ValueError("Invalid immutable commit")
    if previous and previous.get("snapshot_format") == 2 and previous.get("commit") == sha and previous.get("repository") == REPO and len(previous.get("sources", [])) >= 2:
        cached = json.loads(json.dumps(previous))
        cached["source_requests"] = previous.get("source_requests", previous["requests"])
        cached.update(requests=requests, head_rechecked_at=dt.datetime.now(dt.timezone.utc).isoformat(), cache_reused=True)
        return cached
    tree = get(API + "/git/trees/" + sha + "?recursive=1", 2 * 1024 * 1024)
    if tree.get("truncated"):
        raise ValueError("Repository tree was truncated; no complete-tree claims permitted")
    paths = [entry["path"] for entry in tree["tree"] if entry["type"] == "blob"]
    candidates = [entry for entry in tree["tree"] if entry["type"] == "blob" and entry.get("mode") == "100644" and entry.get("size", 0) <= 80000 and safe_path(entry["path"]) and not entry["path"].endswith(("-lock.json", ".min.js"))]
    def rank(entry):
        path = entry["path"].lower()
        return (0 if path == "readme.md" else 1 if path == "package.json" else 2 if path in {"server.js", "src/app.tsx", "src/app.jsx", "src/app/page.tsx"} else 3 if any(s in path for s in ("test/", "tests/", "api/", "auth", "store", "schema")) else 4 if path.startswith("src/") else 5, path.count("/"), path)
    by_path = {entry["path"]: entry for entry in candidates}
    preferred = ("README.md", "docs/ARCHITECTURE.md", "docs/MASTER_ROADMAP.md", "docs/AUTHORITY_POLICY.md", "build.js")
    chosen = [by_path[path] for path in preferred if path in by_path]
    for prefix in ("src/", "lib/", "scripts/", "test/", "schemas/"):
        options = sorted([entry for entry in candidates if entry["path"].startswith(prefix)], key=rank)
        if options and len(chosen) < 8:
            chosen.append(options[0])
    chosen += [entry for entry in sorted(candidates, key=rank) if entry not in chosen][:8 - len(chosen)]
    sources, omissions = [], []
    for entry in chosen:
        path = entry["path"]
        text = get("https://raw.githubusercontent.com/" + REPO + "/" + sha + "/" + urllib.parse.quote(path, safe="/"), 80000, raw=True)
        # Fail closed on likely hardcoded credentials; never store the body.
        if re.search(r"(?:gh[pousr]_[A-Za-z0-9]{20,}|sk-[A-Za-z0-9]{20,}|-----BEGIN .*PRIVATE KEY-----)", text):
            omissions.append({"path": path, "reason": "Potential credential material; content not retained"})
            continue
        lines, used, excerpt = text.splitlines(), 0, []
        for number, line in enumerate(lines[:70], 1):
            if used + len(line.encode()) > 1100:
                break
            excerpt.append(line)
            used += len(line.encode()) + 1
        if not excerpt:
            omissions.append({"path": path, "reason": "No bounded text excerpt available"})
            continue
        source = {"id": "S%d" % (len(sources) + 1), "path": path, "commit": sha, "blob_sha": entry["sha"],
                  "url": "https://github.com/" + REPO + "/blob/" + sha + "/" + urllib.parse.quote(path, safe="/"),
                  "line_start": 1, "line_end": len(excerpt), "text": "\n".join(excerpt),
                  "full_line_count": len(lines), "truncated": len(excerpt) < len(lines),
                  "content_sha256": hashlib.sha256(text.encode()).hexdigest()}
        sources.append(source)
    if len(sources) < 2:
        raise ValueError("Insufficient safe public evidence")
    return {"snapshot_format": 2, "repository": REPO, "read_only": True, "commit": sha, "default_branch": metadata["default_branch"],
            "retrieved_at": dt.datetime.now(dt.timezone.utc).isoformat(), "metadata_url": API,
            "file_count": len(paths), "structure": sorted([p for p in paths if safe_path(p)], key=lambda p: (
                0 if "/" not in p else 1 if p.startswith(("src/", "scripts/", "test/", "tests/", ".github/")) else 2 if p.startswith("docs/") else 3, p))[:240],
            "sources": sources, "omissions": omissions, "requests": requests,
            "limitations": ["Only eight bounded file excerpts inspected; source absence is not evidence of absence.",
                           "No code, tests, deployments or runtime behavior of CORE were executed.",
                           "Recommendations are hypotheses requiring maintainer review."]}
