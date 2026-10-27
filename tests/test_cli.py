import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from agentproof.cli import check, inspect_repository, main, run_check


class AgentProofTests(unittest.TestCase):
    def test_passing_command(self):
        with tempfile.TemporaryDirectory() as path:
            result = run_check(['python', '-c', 'print("ok")'], path)
            self.assertEqual(result['status'], 'passed')
            self.assertIn('ok', result['output'])

    def test_failing_command(self):
        with tempfile.TemporaryDirectory() as path:
            result = run_check(['python', '-c', 'raise SystemExit(3)'], path)
            self.assertEqual(result['exit_code'], 3)

    def test_missing_command(self):
        with tempfile.TemporaryDirectory() as path:
            result = run_check(['agentproof-nonexistent-command-xyz'], path)
            self.assertEqual(result['status'], 'failed')

    def test_invalid_directory(self):
        with self.assertRaises(ValueError):
            inspect_repository('/this/path/does/not/exist')

    def test_skipped_is_not_verified(self):
        with tempfile.TemporaryDirectory() as path:
            report = check(path)
            self.assertEqual(report['verdict'], 'not_verified')

    def test_passing_tests_pass(self):
        with tempfile.TemporaryDirectory() as path:
            report = check(path, ['python', '-c', 'pass'])
            self.assertEqual(report['verdict'], 'passed')

    def test_failed_tests_fail(self):
        with tempfile.TemporaryDirectory() as path:
            report = check(path, ['python', '-c', 'raise SystemExit(1)'])
            self.assertEqual(report['verdict'], 'failed')

    def test_cli_json_output(self):
        with tempfile.TemporaryDirectory() as path:
            from io import StringIO
            output = StringIO()
            with patch('sys.stdout', output):
                code = main([path, '--json', '--test', 'python', '-c', 'pass'])
            self.assertEqual(code, 0)
            self.assertEqual(json.loads(output.getvalue())['verdict'], 'passed')

    def test_timeout(self):
        with tempfile.TemporaryDirectory() as path:
            result = run_check(['python', '-c', 'import time; time.sleep(2)'], path, timeout=1)
            self.assertEqual(result['status'], 'failed')


if __name__ == '__main__':
    unittest.main()
