"""Bounded, versioned artifact assembly and real Operations verification. No generated commands/code."""
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time
from .schemas import strict, obj, array, enum

ROOT = Path(__file__).resolve().parent.parent
SCAFFOLD = Path(__file__).resolve().parent / 'scaffolds/local_solutions'
FILES = ('app.py', 'index.html', 'app.js', 'style.css', 'test_app.py', 'verify.py', 'README.md')
SPEC_SCHEMA = strict('local_solutions_design', obj({
    'application_title': {'type': 'string', 'maxLength': 80},
    'introduction': {'type': 'string', 'maxLength': 300},
    'require_location': {'type': 'boolean'},
    'minimum_description_chars': {'type': 'integer', 'minimum': 10, 'maximum': 40},
    'maximum_description_chars': enum(['1000', '2000', '4000']),
    'design_rationale': {'type': 'string', 'maxLength': 500},
    'integration_plan': array({'type': 'string', 'maxLength': 220}, 2, 4),
    'source_ids': array({'type': 'string'}, 1, 4)}))


def validate_spec(spec, source_ids):
    if set(spec) != set(SPEC_SCHEMA['json_schema']['schema']['properties']):
        raise ValueError('Design must use the bounded specification schema')
    for key, limit in [('application_title', 80), ('introduction', 300), ('design_rationale', 500)]:
        if not isinstance(spec[key], str) or not 4 <= len(spec[key]) <= limit:
            raise ValueError('Invalid product specification: ' + key)
    if type(spec['require_location']) is not bool or type(spec['minimum_description_chars']) is not int or not 10 <= spec['minimum_description_chars'] <= 40 or spec['maximum_description_chars'] not in ['1000', '2000', '4000']:
        raise ValueError('Design exceeds allowlisted validation choices')
    if not isinstance(spec['source_ids'], list) or not spec['source_ids'] or not set(spec['source_ids']) <= set(source_ids):
        raise ValueError('Design references unknown Research evidence')
    if not isinstance(spec['integration_plan'], list) or not 2 <= len(spec['integration_plan']) <= 4 or not all(isinstance(v, str) and 4 <= len(v) <= 220 for v in spec['integration_plan']):
        raise ValueError('Invalid integration plan')
    return {**spec, 'maximum_description_chars': int(spec['maximum_description_chars'])}


def run_directory(identity, base=None):
    if not re.fullmatch(r'mission-\d{8}-\d{6}-[0-9a-f]{6}', identity):
        raise ValueError('Invalid artifact mission identity')
    base = Path(base or ROOT / 'artifacts/core-local-solutions').absolute()
    directory = base / 'runs' / identity
    for path in (base, base / 'runs', directory):
        if path.is_symlink() or path.resolve() != path.absolute():
            raise ValueError('Artifact paths must not traverse symlinks')
    return directory


def build(identity, spec, research, snapshot, base=None):
    directory = run_directory(identity, base)
    if directory.exists():
        raise ValueError('Immutable mission artifact already exists')
    directory.mkdir(parents=True)
    for name in FILES:
        shutil.copyfile(SCAFFOLD / name, directory / name)
    (directory / 'spec.json').write_text(json.dumps(spec, indent=2))
    (directory / 'research-brief.json').write_text(json.dumps({'mission_id': identity, 'commit': snapshot['commit'], 'brief': research,
        'sources': snapshot['sources'], 'limitations': snapshot['limitations']}, indent=2))
    manifest = {'mission_id': identity, 'implementation': 'Audited predefined Python scaffold plus real Nemotron-selected specification. No model-generated code or shell executes.',
                'files': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in directory.iterdir() if p.is_file()}}
    (directory / 'manifest.json').write_text(json.dumps(manifest, indent=2))
    return directory, manifest


def verify(directory, persist=True):
    directory = Path(directory).resolve()
    # Reject modified executable inputs before launching the fixed test process.
    for name in FILES:
        if (directory / name).read_bytes() != (SCAFFOLD / name).read_bytes():
            raise ValueError('Operations refuses altered executable scaffold: ' + name)
    started = time.time()
    result = subprocess.run([sys.executable, '-I', str(directory / 'verify.py')], cwd=str(directory), capture_output=True, text=True, timeout=35)
    try:
        outcome = json.loads(result.stdout.strip())
    except ValueError:
        outcome = {'passed': False, 'tests_run': 0, 'failures': 0, 'errors': 1, 'parse_error': True}
    report = {'started_at': started, 'finished_at': time.time(), 'command': ['python3', '-I', 'verify.py'], 'exit_code': result.returncode,
              'stdout': result.stdout, 'stderr': result.stderr, 'outcome': outcome, 'passed': result.returncode == 0 and outcome.get('passed') is True,
              'scope': 'Actual isolated scaffold tests and loopback HTTP acceptance; no original CORE execution or external network permitted.'}
    if persist:
        (directory / 'build-report.json').write_text(json.dumps(report, indent=2))
    return report


def activate(directory, base=None):
    base = Path(base or ROOT / 'artifacts/core-local-solutions')
    # Stable command; versioned run sources remain intact.
    for name in (*FILES, 'spec.json', 'manifest.json', 'research-brief.json', 'build-report.json'):
        shutil.copyfile(Path(directory) / name, base / name)
    (base / 'active.json').write_text(json.dumps({'mission_id': Path(directory).name}))
