#!/usr/bin/env python3
"""Remove a cron job"""
import argparse
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from cron_lib import remove_job

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--name', '-n', required=True)
    parser.add_argument('--json', '-j', action='store_true')
    args = parser.parse_args()
    
    result = remove_job(args.name)
    
    if args.json:
        import json
        print(json.dumps(result, indent=2))
    else:
        if result.get('success'):
            print(f"Removed job '{args.name}'")
        else:
            print(f"Error: {result.get('error')}", file=sys.stderr)
            sys.exit(1)

if __name__ == '__main__':
    main()
