"""Fixed test entrypoint. Audit guard blocks subprocesses, outside writes and non-loopback networking."""
import json
import os
from pathlib import Path
import sys
import time
import unittest

ROOT = Path(__file__).resolve().parent
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT))
violations = []

def guard(event, args):
    denied = event in {'subprocess.Popen', 'os.system', 'os.exec', 'os.spawn', 'ctypes.dlopen'}
    if event in {'socket.connect', 'socket.bind'}:
        address = args[1]
        denied = not isinstance(address, tuple) or address[0] != '127.0.0.1'
    if event == 'open' and isinstance(args[0], (str, bytes, os.PathLike)):
        mode, flags = args[1], args[2]
        writes = isinstance(mode, str) and any(x in mode for x in 'wax+') or isinstance(flags, int) and flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC)
        if writes:
            denied = ROOT not in Path(args[0]).resolve().parents
    if event in {'os.remove', 'os.rmdir', 'os.mkdir', 'os.rename'}:
        for path in args[:2] if event == 'os.rename' else args[:1]:
            if isinstance(path, (str, bytes, os.PathLike)) and ROOT not in Path(path).resolve().parents:
                denied = True
    if denied:
        violations.append(event)
        raise PermissionError('Operations guard blocked ' + event)

sys.addaudithook(guard)
(ROOT / '.test-work').mkdir(exist_ok=True)
import test_app
started = time.perf_counter()
suite = unittest.defaultTestLoader.loadTestsFromModule(test_app)
result = unittest.TextTestRunner(verbosity=2, stream=sys.stderr).run(suite)
print(json.dumps({'passed': result.wasSuccessful() and not violations, 'tests_run': result.testsRun,
    'failures': len(result.failures), 'errors': len(result.errors), 'skipped': len(result.skipped),
    'latency_s': round(time.perf_counter() - started, 4), 'guard_violations': violations,
    'guard': 'Fixed audited scaffold and test commands only; no generated code or shell. Python audit hook is defense in depth, not an OS security sandbox.',
    'external_network_requests': 0 if not violations else None,
    'tests': [{'id': test.id(), 'traceback': trace} for test, trace in result.failures + result.errors]}))
sys.exit(0 if result.wasSuccessful() and not violations else 1)
