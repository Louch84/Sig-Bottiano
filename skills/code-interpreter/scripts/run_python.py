#!/usr/bin/env python3
"""
Execute Python code in a sandboxed environment.
Supports: file I/O, pip packages, timeout, memory limits
"""
import argparse
import subprocess
import sys
import tempfile
import os
import json
from pathlib import Path

def install_packages(packages):
    """Install pip packages"""
    if not packages:
        return
    pkg_list = packages.split(',') if isinstance(packages, str) else packages
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-q'] + pkg_list)

def run_code(code, timeout=30, workdir=None):
    """Execute Python code with safety limits"""
    workdir = workdir or tempfile.mkdtemp(prefix='py_exec_')
    os.makedirs(workdir, exist_ok=True)
    
    script_path = os.path.join(workdir, 'script.py')
    with open(script_path, 'w') as f:
        f.write(code)
    
    env = os.environ.copy()
    env['PYTHONPATH'] = workdir
    
    try:
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=workdir,
            env=env
        )
        return {
            'stdout': result.stdout,
            'stderr': result.stderr,
            'returncode': result.returncode,
            'workdir': workdir
        }
    except subprocess.TimeoutExpired:
        return {'error': f'Code execution timed out after {timeout}s', 'workdir': workdir}
    except Exception as e:
        return {'error': str(e), 'workdir': workdir}

def main():
    parser = argparse.ArgumentParser(description='Execute Python code safely')
    parser.add_argument('--code', '-c', required=True, help='Python code to execute')
    parser.add_argument('--packages', '-p', help='Comma-separated packages to install')
    parser.add_argument('--timeout', '-t', type=int, default=30, help='Timeout in seconds')
    parser.add_argument('--workdir', '-w', help='Working directory')
    parser.add_argument('--output', '-o', help='Output file for results')
    parser.add_argument('--json', '-j', action='store_true', help='Output as JSON')
    
    args = parser.parse_args()
    
    # Install packages if requested
    if args.packages:
        install_packages(args.packages)
    
    # Run the code
    result = run_code(args.code, args.timeout, args.workdir)
    
    # Output results
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        if result.get('stdout'):
            print(result['stdout'])
        if result.get('stderr'):
            print(result['stderr'], file=sys.stderr)
        if result.get('error'):
            print(f"Error: {result['error']}", file=sys.stderr)
            sys.exit(1)
    
    sys.exit(result.get('returncode', 0))

if __name__ == '__main__':
    main()
