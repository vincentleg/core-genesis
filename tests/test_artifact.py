"""Real generated artifact process tests plus bounded-input/authority invariants."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from core_genesis import artifact_builder as builder

SPEC = {'application_title': 'Local solutions', 'introduction': 'Submit a local observation and a proposal for human review.', 'require_location': True,
        'minimum_description_chars': 20, 'maximum_description_chars': '2000', 'design_rationale': 'Keep human authority explicit.',
        'integration_plan': ['Maintainers inspect the isolated prototype.', 'Request separate authorization before CORE changes.'], 'source_ids': ['S1']}
SNAPSHOT = {'commit': 'a'*40, 'sources': [], 'limitations': ['Unit-test fixture, not live repository evidence']}


class ArtifactTests(unittest.TestCase):
    def test_path_and_spec_cannot_expand_executable_authority(self):
        for identity in ['../../core', 'mission-../../x', 'unknown']:
            with self.assertRaises(ValueError):
                builder.run_directory(identity)
        for edit in [{'maximum_description_chars': '__import__("os")'}, {'source_ids': ['invented']}, {'require_location': 'false'}]:
            with self.assertRaises(ValueError):
                builder.validate_spec({**SPEC, **edit}, ['S1'])
        self.assertEqual(builder.validate_spec(SPEC, ['S1'])['maximum_description_chars'], 2000)

    def test_generated_application_executes_seven_real_tests_and_cannot_be_overwritten(self):
        with tempfile.TemporaryDirectory() as directory:
            root, manifest = builder.build('mission-20261017-150000-aaaaaa', builder.validate_spec(SPEC, ['S1']), {}, SNAPSHOT, Path(directory).resolve()/'artifact')
            report = builder.verify(root)
            self.assertTrue(report['passed'], report['stderr'])
            self.assertEqual(report['outcome']['tests_run'], 7)
            self.assertEqual(report['exit_code'], 0)
            self.assertEqual(report['outcome']['guard_violations'], [])
            self.assertEqual(json.loads((root/'build-report.json').read_text()), report)
            before = (root/'build-report.json').read_bytes()
            builder.verify(root, persist=False)
            self.assertEqual(before, (root/'build-report.json').read_bytes())
            with self.assertRaises(ValueError):
                builder.build(root.name, SPEC, {}, SNAPSHOT, Path(directory).resolve()/'artifact')

    def test_modified_executable_is_never_run(self):
        with tempfile.TemporaryDirectory() as directory:
            root, _ = builder.build('mission-20261017-150000-bbbbbb', builder.validate_spec(SPEC, ['S1']), {}, SNAPSHOT, Path(directory).resolve()/'artifact')
            (root/'app.py').write_text('raise RuntimeError("untrusted")')
            with patch('core_genesis.artifact_builder.subprocess.run') as process:
                with self.assertRaises(ValueError):
                    builder.verify(root)
                process.assert_not_called()
