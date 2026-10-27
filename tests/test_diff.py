import subprocess
import tempfile
import unittest
from pathlib import Path

from agentproof.diff import inspect_changes


class ChangeInspectionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        subprocess.run(["git", "init", "-q"], cwd=self.root, check=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=self.root, check=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=self.root, check=True)
        (self.root / "app.py").write_text("print('hello')\n")
        subprocess.run(["git", "add", "app.py"], cwd=self.root, check=True)
        subprocess.run(["git", "commit", "-qm", "initial"], cwd=self.root, check=True)

    def test_clean_repository(self):
        report = inspect_changes(self.root)
        self.assertEqual(report["changed_file_count"], 0)

    def test_unstaged_file(self):
        (self.root / "app.py").write_text("print('changed')\n")
        report = inspect_changes(self.root)
        self.assertTrue(report["files"][0]["unstaged"])

    def test_staged_file(self):
        (self.root / "app.py").write_text("print('changed')\n")
        subprocess.run(["git", "add", "app.py"], cwd=self.root, check=True)
        self.assertTrue(inspect_changes(self.root)["files"][0]["staged"])

    def test_untracked_sensitive_path(self):
        path = self.root / ".github" / "workflows"
        path.mkdir(parents=True)
        (path / "ci.yml").write_text("name: CI\n")
        report = inspect_changes(self.root)
        self.assertEqual(report["changed_file_count"], 1)
        self.assertTrue(report["files"][0]["untracked"])
        self.assertTrue(report["files"][0]["review_hints"])

    def test_ordinary_path_has_no_hints(self):
        (self.root / "notes.txt").write_text("hello")
        self.assertEqual(inspect_changes(self.root)["hint_count"], 0)


if __name__ == "__main__":
    unittest.main()
