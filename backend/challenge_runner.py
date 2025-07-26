import json
import subprocess
import tempfile
import os

def run_challenge(challenge_id: int, code_str: str) -> dict:
    """
    Writes `code_str` to solution.py and runs pytest for the given challenge tests.
    Returns {'output': str, 'returncode': int} or {'error': str}.
    """
    # Create temp test directory
    test_dir = tempfile.mkdtemp()
    # Write user code to solution.py
    sol_path = os.path.join(test_dir, 'solution.py')
    with open(sol_path, 'w', encoding='utf-8') as f:
        f.write(code_str)
    # Copy challenge test files
    src_tests = os.path.join(os.getcwd(), 'tests', 'test_cases')
    for fname in os.listdir(src_tests):
        if fname.startswith(f'test_challenge_{challenge_id}'):
            with open(os.path.join(src_tests, fname), 'r') as src, open(os.path.join(test_dir, fname), 'w') as dst:
                dst.write(src.read())
    # Run pytest
    proc = subprocess.run(
        ['pytest', '-q', '--disable-warnings', '--maxfail=1'],
        cwd=test_dir,
        capture_output=True,
        text=True
    )
    # Return results
    return {'output': proc.stdout + proc.stderr, 'returncode': proc.returncode}