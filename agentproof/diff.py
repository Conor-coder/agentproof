"""Read-only change inventory and explainable filename-based review hints."""
import subprocess
from pathlib import Path

SENSITIVE_PATHS = {
    ".github/workflows/": "CI workflow changed: review permissions and executed commands",
    "auth": "Authentication-related filename: check access controls",
    "permission": "Permission-related filename: check privilege boundaries",
    "secret": "Secrets-related filename: check for credential exposure",
    ".env": "Environment/config file: check for accidental secrets",
    "migration": "Database migration: check backwards compatibility and rollback",
    "payment": "Payment-related filename: check money-handling logic",
}


def _git_paths(root, args):
    result = subprocess.run(["git", *args], cwd=root, capture_output=True,
                            timeout=15, check=False)
    if result.returncode:
        raise ValueError("Unable to inspect Git changes (is this a Git repository?)")
    return [x.decode("utf-8", errors="replace") for x in result.stdout.split(b"\0") if x]


def inspect_changes(root):
    """Collect tracked and untracked local changes without reading file contents."""
    root = Path(root).resolve()
    unstaged = set(_git_paths(root, ["diff", "--name-only", "-z"]))
    staged = set(_git_paths(root, ["diff", "--cached", "--name-only", "-z"]))
    untracked = set(_git_paths(root, ["ls-files", "--others", "--exclude-standard", "-z"]))
    files = []
    for path in sorted(unstaged | staged | untracked):
        lower = path.lower().replace("\\", "/")
        hints = sorted({message for key, message in SENSITIVE_PATHS.items() if key in lower})
        files.append({"path": path, "staged": path in staged,
                      "unstaged": path in unstaged, "untracked": path in untracked,
                      "review_hints": hints})
    return {"status": "completed", "scope": "local working tree only",
            "changed_file_count": len(files),
            "files": files,
            "hint_count": sum(len(f["review_hints"]) for f in files),
            "note": "Filename hints are not security findings; committed changes are not included."}
