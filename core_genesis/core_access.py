"""Local, immutable Git object inspection. No checkout, network, or CORE writes."""
import datetime as dt
import hashlib
import os
from pathlib import Path
import re
import subprocess

DEFAULT_REF = 'v9.2/earth-first'
SUFFIXES = {'.js', '.mjs', '.json', '.html', '.css', '.md', '.py'}

def git(repo, *args):
    return subprocess.check_output(['git', '--no-optional-locks', '-C', str(repo), *args], timeout=30)

def inspect_core(repo=None, ref=None, guard=lambda: None, previous=None):
    repo = Path(repo or os.environ.get('CORE_REPO_PATH', Path.home() / 'core')).expanduser().resolve()
    ref = ref or os.environ.get('CORE_REF', DEFAULT_REF)
    if not re.fullmatch(r'[A-Za-z0-9_./-]+', ref) or ref.startswith('-'):
        raise ValueError('Invalid explicit CORE ref')
    guard()
    # No fallback, fetch, checkout, hooks, or source execution.
    sha = git(repo, 'rev-parse', '--verify', ref + '^{commit}').decode().strip()
    branch = git(repo, 'branch', '--show-current').decode().strip()
    head = git(repo, 'rev-parse', 'HEAD').decode().strip()
    dirty = git(repo, 'status', '--porcelain').decode()
    entries = git(repo, 'ls-tree', '-r', '-z', sha).split(b'\0')
    tree, sources, omissions = [], [], []
    for entry in filter(None, entries):
        meta, raw_path = entry.split(b'\t', 1)
        mode, kind, blob = meta.decode().split()
        path = raw_path.decode()
        tree.append(path)
        parts = Path(path).parts
        selected = (path.startswith('src/') or path in {'README.md', 'PROJECT_STATE.md', 'build.js', 'index.html', 'world.html', 'docs/ARCHITECTURE.md'} or path.startswith(('test/', 'schemas/')))
        safe = not any(p.startswith('.') or re.search(r'secret|credential|password|token|private', p, re.I) for p in parts)
        if not selected or not safe or Path(path).suffix not in SUFFIXES or mode not in {'100644', '100755'}:
            continue
        guard()
        size = int(git(repo, 'cat-file', '-s', blob))
        if size > 2_000_000:
            omissions.append({'path': path, 'reason': 'Over 2 MB per-file bound; not read'})
            continue
        body = git(repo, 'cat-file', 'blob', blob)
        text = body.decode('utf-8')
        if re.search(r'gh[pousr]_[A-Za-z0-9]{20,}|sk-[A-Za-z0-9]{20,}|-----BEGIN .*PRIVATE KEY-----', text):
            omissions.append({'path': path, 'reason': 'Potential credential; content not retained'})
            continue
        sources.append({'id': 'S%d' % (len(sources)+1), 'path': path, 'commit': sha, 'blob_sha': blob,
                        'url': 'https://github.com/vincentleg/core/blob/' + sha + '/' + path,
                        'line_start': 1, 'line_end': len(text.splitlines()), 'full_line_count': len(text.splitlines()),
                        'text': text, 'truncated': False, 'content_sha256': hashlib.sha256(body).hexdigest()})
    if not sources:
        raise ValueError('No eligible CORE sources found')
    return {'snapshot_format': 3, 'repository': 'vincentleg/core', 'local_path': str(repo), 'requested_ref': ref,
            'commit': sha, 'checkout_branch': branch, 'checkout_commit': head, 'checkout_dirty': bool(dirty),
            'read_only': True, 'external_transmission_allowed': False, 'environment': 'local_development',
            'public_production': {'url': 'https://creationofrebornearth.com', 'commit': None,
                                  'status': 'Older production per founder; V9.2 not deployed. Not inspected by this operation.'},
            'retrieved_at': dt.datetime.now(dt.timezone.utc).isoformat(), 'structure': tree, 'file_count': len(tree),
            'sources': sources, 'omissions': omissions, 'requests': [],
            'architecture': {'entrypoints': [p for p in tree if p in {'index.html','world.html','corridor.html','build.js'}],
                             'source_groups': sorted({p.split('/')[1] for p in tree if p.startswith('src/') and p.count('/') > 1}),
                             'tests': [p for p in tree if p.startswith('test/')]},
            'limitations': ['Full eligible source files read from Git objects; uncommitted working files excluded.',
                            'Source inspection only. No CORE tests or browser interactions executed by this operation.',
                            'Architecture groups are file structure evidence, not a semantic completeness guarantee.',
                            'Local source must not be sent to external models without separate authorization.']}
