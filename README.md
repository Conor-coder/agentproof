# AgentProof

**Don't just generate code. Verify it.**

[![AgentProof tests](https://github.com/Conor-coder/agentproof/actions/workflows/tests.yml/badge.svg)](https://github.com/Conor-coder/agentproof/actions/workflows/tests.yml)

AgentProof is an early Python command-line tool for evidence-based checks of local software projects, including AI-generated code.

## MVP features

- Inspect Git working-tree status without changing files.
- Inventory staged, unstaged and untracked local files, with explainable filename-based review hints (CI, authentication, secrets, migrations and payments).
- Compare two commits with `--base` and `--head`, returning changed filenames, bounded added-line previews and explainable review hints.
- Run a test command **only when explicitly supplied**.
- Return pass/fail/skip status, bounded command output, and optional JSON.
- Enforce timeouts and exit non-zero when verification fails or is skipped.
- Work without dependencies, API keys, or LLM calls.

**Important:** A passing test command is not proof that code is secure or correct. Security scanning, code review agents and sandboxing are not yet implemented.

## Try it

Requires Python 3.10+ and Git on PATH. From this repository:

```bash
python -m agentproof . --test python -m unittest discover -s tests -v
```

JSON report (put `--json` before `--test`):

```bash
python -m agentproof . --json --test python -m unittest discover -s tests -v
```

Inspect local changes without running tests:

```bash
python -m agentproof .
```

This reports local changed files and any filename-based review hints. It returns `not_verified` and exits with code 2 because no test was executed.

**Scope:** This inventory covers local working-tree changes, not committed differences between branches. Hints are prompts for human review, **not verified vulnerabilities**.

## Compare committed changes

```bash
python -m agentproof . --base HEAD~1 --head HEAD
python -m agentproof . --base HEAD~1 --json
```

This reports added-line previews (up to 25 per file, 160 characters per line) and filename-based review prompts. **Diff previews can include credentials or sensitive code; avoid sharing JSON reports publicly without checking them.** The comparison currently omits deleted-file evidence and limits Git diff output to 1 MB. The verdict is still based on the explicitly supplied test command, not review hints.

## Run development tests

```bash
python -m unittest discover -s tests -v
```

GitHub Actions runs these tests on pushes and pull requests.

## Safety

Test commands execute with your current user permissions. Only run tests from trusted repositories, preferably in an isolated disposable environment. AgentProof does not automatically execute target code, but commands you supply can modify files.

## Roadmap

1. Expand diff analysis to deletions, rename detection and evidence-based risk rules.
2. Safe opt-in static checks.
3. Optional LLM review with file/line evidence.
4. Claude Code integration and specialist reviewers.

This is an experimental MVP, not a security certification tool.
