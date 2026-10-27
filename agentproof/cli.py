"""Small, read-only local verification CLI. No LLM or network needed."""
import argparse
import json
import subprocess
from pathlib import Path

from .diff import inspect_changes


def run_check(command, cwd, timeout=120):
    """Execute an explicitly configured command without invoking a shell."""
    try:
        result = subprocess.run(command, cwd=cwd, capture_output=True, text=True,
                                timeout=timeout, check=False)
        return {'status': 'passed' if result.returncode == 0 else 'failed',
                'exit_code': result.returncode,
                'output': (result.stdout + result.stderr)[-4000:]}
    except subprocess.TimeoutExpired:
        return {'status': 'failed', 'reason': f'timed out after {timeout}s'}
    except OSError as exc:
        return {'status': 'failed', 'reason': type(exc).__name__}


def inspect_repository(root):
    root = Path(root).resolve()
    if not root.is_dir():
        raise ValueError('Target must be an existing directory')
    git = run_check(['git', 'status', '--short'], root, 15)
    return {'directory': str(root), 'git_status': git}


def check(root, test_command=None, timeout=120):
    """Test execution is opt-in; change inspection is read-only."""
    report = {'tool': 'AgentProof', 'version': '0.2.0',
              'repository': inspect_repository(root), 'checks': {}}
    try:
        report['changes'] = inspect_changes(root)
    except (ValueError, OSError, subprocess.TimeoutExpired) as exc:
        report['changes'] = {'status': 'unavailable', 'reason': type(exc).__name__}
    if test_command:
        report['checks']['tests'] = run_check(test_command, Path(root).resolve(), timeout)
    else:
        report['checks']['tests'] = {'status': 'skipped', 'reason': 'No test command supplied'}
    statuses = [v['status'] for v in report['checks'].values()]
    report['verdict'] = ('failed' if 'failed' in statuses else
                         'passed' if statuses and all(s == 'passed' for s in statuses) else 'not_verified')
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(prog='agentproof', description='Evidence-based checks for AI-generated code')
    parser.add_argument('path', nargs='?', default='.', help='Local project directory')
    parser.add_argument('--test', nargs=argparse.REMAINDER, help='Explicit test command; put this option last')
    parser.add_argument('--timeout', type=int, default=120, help='Test timeout in seconds (default: 120)')
    parser.add_argument('--json', action='store_true', help='Print machine-readable JSON')
    args = parser.parse_args(argv)
    if args.timeout < 1 or args.timeout > 3600:
        parser.error('--timeout must be between 1 and 3600 seconds')
    if args.test is not None and not args.test:
        parser.error('--test requires a command')
    try:
        report = check(args.path, args.test, args.timeout)
    except ValueError as exc:
        parser.error(str(exc))
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"AgentProof v{report['version']} | {report['verdict'].upper()}")
        print(f"Directory: {report['repository']['directory']}")
        print(f"Git status: {report['repository']['git_status']['status']}")
        changes = report['changes']
        print(f"Changed files: {changes.get('changed_file_count', 'unavailable')}")
        for item in changes.get('files', []):
            print(f"  {item['path']}")
            for hint in item['review_hints']:
                print(f"    REVIEW: {hint}")
        for name, result in report['checks'].items():
            print(f"{name}: {result['status']}")
            if result.get('output'):
                print(result['output'].strip())
    return 1 if report['verdict'] == 'failed' else 0 if report['verdict'] == 'passed' else 2
