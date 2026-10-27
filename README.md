# AgentProof

**Don't just generate code. Verify it.**

[![AgentProof tests](https://github.com/Conor-coder/agentproof/actions/workflows/tests.yml/badge.svg)](https://github.com/Conor-coder/agentproof/actions/workflows/tests.yml)

AgentProof is an early Python command-line tool for evidence-based checks of local software projects, including AI-generated code.

## MVP features

- Inspect Git working-tree status without changing files.
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

Inspect without running tests:

```bash
python -m agentproof .
```

This reports `not_verified` and exits with code 2 because no test was executed.

## Run development tests

```bash
python -m unittest discover -s tests -v
```

GitHub Actions runs these tests on pushes and pull requests.

## Safety

Test commands execute with your current user permissions. Only run tests from trusted repositories, preferably in an isolated disposable environment. AgentProof does not automatically execute target code, but commands you supply can modify files.

## Roadmap

1. Git diff summaries and change-risk indicators.
2. Safe opt-in static checks.
3. Optional LLM review with file/line evidence.
4. Claude Code integration and specialist reviewers.

This is an experimental MVP, not a security certification tool.
