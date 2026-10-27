import subprocess
import tempfile
import unittest
from pathlib import Path

from agentproof.commits import compare_commits


class CommitComparisonTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        subprocess.run(["git", "init", "-q"], cwd=self.root, check=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=self.root, check=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=self.root, check=True)
        (self.root / "app.py").write_text("print('old')\n")
        subprocess.run(["git", "add", "."], cwd=self.root, check=True)
        subprocess.run(["git", "commit", "-qm", "initial"], cwd=self.root, check=True)
        self.base = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=self.root).decode().strip()

    def test_added_line_evidence(self):
        (self.root / "app.py").write_text("print('new')\n")
        subprocess.run(["git", "add", "."], cwd=self.root, check=True)
        subprocess.run(["git", "commit", "-qm", "update"], cwd=self.root, check=True)
        result = compare_commits(self.root, self.base)
        self.assertEqual(result["changed_file_count"], 1)
        self.assertEqual(result["files"][0]["added_lines"][0]["line"], 1)

    def test_sensitive_filename_hint(self):
        (self.root / "auth.py").write_text("print('demo')\n")
        subprocess.run(["git", "add", "."], cwd=self.root, check=True)
        subprocess.run(["git", "commit", "-qm", "auth"], cwd=self.root, check=True)
        self.assertTrue(compare_commits(self.root, self.base)["files"][0]["review_hints"])

    def test_invalid_revision(self):
        with self.assertRaises(ValueError):
            compare_commits(self.root, "no-such-revision-xyz")

    def test_same_commit_has_no_changes(self):
        self.assertEqual(compare_commits(self.root, self.base, self.base)["changed_file_count"], 0)


if __name__ == "__main__":
    unittest.main()
