"""Read-only committed change review with bounded, line-referenced evidence."""
import re
import subprocess
from pathlib import Path

from .diff import SENSITIVE_PATHS

HUNK = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@")


def compare_commits(root, base, head="HEAD"):
    """Compare two existing Git revisions; no shell, checkout or file writes."""
    root = Path(root).resolve()
    if not root.is_dir():
        raise ValueError("Directory does not exist")
    for ref in (base, head):
        if not ref or ref.startswith("-") or "\x00" in ref:
            raise ValueError("Invalid Git revision")
        result = subprocess.run(["git", "rev-parse", "--verify", "--end-of-options",
                                 ref + "^{commit}"], cwd=root, capture_output=True,
                                timeout=15, check=False)
        if result.returncode:
            raise ValueError("Unknown Git revision: " + ref)
    result = subprocess.run(
        ["git", "diff", "--no-ext-diff", "--no-textconv", "--unified=0",
         "--no-renames", base, head, "--"], cwd=root,
        capture_output=True, timeout=30, check=False)
    if result.returncode:
        raise ValueError("Git diff comparison failed")
    # Cap output to avoid unbounded memory and accidental exposure of large diffs.
    raw = result.stdout[:1_000_000]
    truncated = len(result.stdout) > len(raw)
    files = []
    current = None
    line_no = None
    for line in raw.decode("utf-8", "replace").splitlines():
        if line.startswith("+++ b/"):
            path = line[6:]
            hints = sorted({msg for key, msg in SENSITIVE_PATHS.items()
                            if key in path.lower()})
            current = {"path": path, "review_hints": hints, "added_lines": []}
            files.append(current)
            line_no = None
        elif line.startswith("+++ /dev/null"):
            current = None
            line_no = None
        elif current:
            match = HUNK.match(line)
            if match:
                line_no = int(match.group(1))
            elif line.startswith("+") and not line.startswith("+++"):
                if line_no is not None:
                    if len(current["added_lines"]) < 25:
                        current["added_lines"].append({
                            "line": line_no, "preview": line[1:161]})
                    line_no += 1
            elif line.startswith(" ") and line_no is not None:
                line_no += 1
    return {"status": "completed", "base": base, "head": head,
            "changed_file_count": len(files), "files": files,
            "truncated": truncated,
            "note": "Line previews may contain sensitive code. Filename hints are not verified findings."}
