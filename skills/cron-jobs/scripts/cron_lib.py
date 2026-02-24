#!/usr/bin/env python3
"""Simple cron job scheduler using a JSON-based job store"""
import json
import os
import time
import subprocess
from datetime import datetime
from pathlib import Path

JOBS_FILE = os.path.expanduser('~/.openclaw/cron_jobs.json')
LOGS_DIR = os.path.expanduser('~/.openclaw/cron_logs')

def load_jobs():
    if os.path.exists(JOBS_FILE):
        with open(JOBS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_jobs(jobs):
    os.makedirs(os.path.dirname(JOBS_FILE), exist_ok=True)
    with open(JOBS_FILE, 'w') as f:
        json.dump(jobs, f, indent=2)

def add_job(name, schedule, command, env_file=None, working_dir=None):
    jobs = load_jobs()
    jobs[name] = {
        'schedule': schedule,
        'command': command,
        'env_file': env_file,
        'working_dir': working_dir,
        'created': datetime.now().isoformat(),
        'enabled': True
    }
    save_jobs(jobs)
    return {'success': True, 'name': name}

def list_jobs():
    return load_jobs()

def remove_job(name):
    jobs = load_jobs()
    if name in jobs:
        del jobs[name]
        save_jobs(jobs)
        return {'success': True}
    return {'error': f'Job "{name}" not found'}

def run_job(name):
    jobs = load_jobs()
    if name not in jobs:
        return {'error': f'Job "{name}" not found'}
    
    job = jobs[name]
    os.makedirs(LOGS_DIR, exist_ok=True)
    
    log_file = os.path.join(LOGS_DIR, f"{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    
    env = os.environ.copy()
    if job.get('env_file') and os.path.exists(job['env_file']):
        with open(job['env_file']) as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, val = line.strip().split('=', 1)
                    env[key] = val
    
    try:
        with open(log_file, 'w') as log:
            log.write(f"[{datetime.now().isoformat()}] Starting job: {name}\n")
            log.write(f"Command: {job['command']}\n\n")
            
            result = subprocess.run(
                job['command'],
                shell=True,
                cwd=job.get('working_dir'),
                env=env,
                capture_output=True,
                text=True
            )
            
            log.write(result.stdout)
            log.write(result.stderr)
            log.write(f"\n[{datetime.now().isoformat()}] Exit code: {result.returncode}\n")
        
        return {'success': result.returncode == 0, 'log': log_file}
    except Exception as e:
        return {'error': str(e)}

def job_logs(name, lines=50):
    if not os.path.exists(LOGS_DIR):
        return []
    
    logs = []
    for f in os.listdir(LOGS_DIR):
        if f.startswith(f"{name}_"):
            logs.append(os.path.join(LOGS_DIR, f))
    
    logs.sort(reverse=True)
    result = []
    for log_file in logs[:5]:
        with open(log_file) as f:
            content = f.read()
            result.append({'file': log_file, 'content': content[-5000:] if len(content) > 5000 else content})
    return result
