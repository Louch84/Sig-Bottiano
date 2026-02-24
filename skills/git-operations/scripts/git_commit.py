#!/usr/bin/env python3
"""Git commit wrapper"""
import subprocess
import argparse
import sys
import os

def git_commit(repo_path, message, add_all=False, files=None):
    try:
        if add_all:
            subprocess.run(['git', 'add', '-A'], cwd=repo_path, check=True)
        elif files:
            for f in files.split(','):
                subprocess.run(['git', 'add', f.strip()], cwd=repo_path, check=True)
        
        result = subprocess.run(
            ['git', 'commit', '-m', message],
            cwd=repo_path,
            capture_output=True,
            text=True
        )
        return {
            'success': result.returncode == 0,
            'stdout': result.stdout,
            'stderr': result.stderr
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--repo', '-r', default='.')
    parser.add_argument('--message', '-m', required=True)
    parser.add_argument('--all', '-a', action='store_true')
    parser.add_argument('--files', '-f')
    parser.add_argument('--json', '-j', action='store_true')
    args = parser.parse_args()
    
    result = git_commit(args.repo, args.message, args.all, args.files)
    
    if args.json:
        import json
        print(json.dumps(result, indent=2))
    else:
        if result.get('success'):
            print("Committed successfully")
        else:
            print(f"Error: {result.get('error', result.get('stderr'))}", file=sys.stderr)
            sys.exit(1)

if __name__ == '__main__':
    main()
