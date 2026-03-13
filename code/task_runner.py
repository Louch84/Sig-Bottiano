#!/usr/bin/env python3
"""Task Runner - Runs my tasks automatically"""
import time
import random
from datetime import datetime
import subprocess

TASKS = {
    "scan_stocks": "python3 code/trading_bot.py",
    "research": "python3 code/scraper.py", 
    "post_social": "python3 code/social_poster.py",
    "check_memory": "python3 code/memory_search.py",
    "talk": "python3 code/chatter.py"
}

def run_task(task_name):
    """Run a specific task"""
    if task_name in TASKS:
        try:
            result = subprocess.run(
                TASKS[task_name].split(),
                capture_output=True,
                timeout=30
            )
            return {"task": task_name, "status": "done", "output": result.stdout[:200]}
        except Exception as e:
            return {"task": task_name, "status": "error", "error": str(e)}
    return {"task": task_name, "status": "unknown"}

def run_random_task():
    """Pick random task and run"""
    task = random.choice(list(TASKS.keys()))
    return run_task(task)

# Test
if __name__ == "__main__":
    print(f"=== TASK RUNNER {datetime.now().strftime('%H:%M')} ===")
    result = run_random_task()
    print(f"Task: {result['task']}")
    print(f"Status: {result['status']}")
