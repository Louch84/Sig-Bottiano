#!/usr/bin/env python3
"""Git clone wrapper"""
import subprocess
import argparse
import sys
import os

def git_clone(url, dest=None, branch=None, token=None, depth=None):
    if token and 'github.com' in url:
        url = url.replace('https://', f'https://{token}@')
    
    cmd = ['git', 'clone']
    if branch:
        cmd.extend(['-b', branch])
    if depth:
        cmd.extend(['--depth', str(depth)])
    cmd.append(url)
    if dest:
        cmd.append(dest)
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        return {
            'success': result.returncode == 0,
            'stdout': result.stdout,
            'stderr': result.stderr
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', '-u', required=True)
    parser.add_argument('--dest', '-d')
    parser.add_argument('--branch', '-b')
    parser.add_argument('--token', '-t', default=os.getenv('GITHUB_TOKEN'))
    parser.add_argument('--depth', type=int)
    parser.add_argument('--json', '-j', action='store_true')
    args = parser.parse_args()
    
    result = git_clone(args.url, args.dest, args.branch, args.token, args.depth)
    
    if args.json:
        import json
        print(json.dumps(result, indent=2))
    else:
        if result.get('success'):
            print(f"Cloned to {args.dest or os.path.basename(args.url).replace('.git', '')}")
        else:
            print(f"Error: {result.get('error', result.get('stderr'))}", file=sys.stderr)
            sys.exit(1)

if __name__ == '__main__':
    main()
