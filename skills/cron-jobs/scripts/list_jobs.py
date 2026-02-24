#!/usr/bin/env python3
"""List all cron jobs"""
import argparse
import sys
import json
import os
sys.path.insert(0, os.path.dirname(__file__))
from cron_lib import list_jobs

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--json', '-j', action='store_true')
    args = parser.parse_args()
    
    jobs = list_jobs()
    
    if args.json:
        print(json.dumps(jobs, indent=2))
    else:
        if not jobs:
            print("No jobs configured")
        else:
            print(f"{'Name':<20} {'Schedule':<20} {'Command':<30}")
            print("-" * 70)
            for name, job in jobs.items():
                cmd = job['command'][:27] + '...' if len(job['command']) > 30 else job['command']
                enabled = '✓' if job.get('enabled', True) else '✗'
                print(f"{enabled} {name:<18} {job['schedule']:<20} {cmd:<30}")

if __name__ == '__main__':
    main()
