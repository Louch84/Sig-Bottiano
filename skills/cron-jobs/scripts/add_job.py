#!/usr/bin/env python3
"""Add a cron job"""
import argparse
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from cron_lib import add_job

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--name', '-n', required=True)
    parser.add_argument('--schedule', '-s', required=True)
    parser.add_argument('--command', '-c', required=True)
    parser.add_argument('--env-file', '-e')
    parser.add_argument('--working-dir', '-w')
    parser.add_argument('--json', '-j', action='store_true')
    args = parser.parse_args()
    
    result = add_job(args.name, args.schedule, args.command, args.env_file, args.working_dir)
    
    if args.json:
        import json
        print(json.dumps(result, indent=2))
    else:
        if result.get('success'):
            print(f"Added job '{args.name}' with schedule '{args.schedule}'")
        else:
            print(f"Error: {result.get('error')}", file=sys.stderr)
            sys.exit(1)

if __name__ == '__main__':
    main()
