#!/usr/bin/env python3
"""
Self-Improvement Engine
Runs automatically to improve the system
"""

import os
import sys

# Read SELF_IMPROVEMENT.md at startup
SELF_IMPROVEMENT_FILE = "/Users/sigbotti/.openclaw/workspace/SELF_IMPROVEMENT.md"
ERROR_LOG = "/Users/sigbotti/.openclaw/workspace/logs/errors.log"

def check_errors():
    """Run error analyzer and find patterns"""
    if not os.path.exists(ERROR_LOG):
        return None
    
    with open(ERROR_LOG, 'r') as f:
        errors = f.readlines()
    
    if not errors:
        return None
    
    # Get last 10 errors
    recent = errors[-10:]
    
    # Extract function names
    functions = []
    for line in recent:
        if '|' in line:
            parts = line.split('|')
            if len(parts) >= 2:
                functions.append(parts[1].strip())
    
    from collections import Counter
    if functions:
        return Counter(functions).most_common(1)[0]
    return None

def get_daily_task():
    """Read today's improvement task"""
    if not os.path.exists(SELF_IMPROVEMENT_FILE):
        return "No improvement file found"
    
    with open(SELF_IMPROVEMENT_FILE, 'r') as f:
        content = f.read()
    
    # Find unchecked boxes
    lines = content.split('\n')
    for line in lines:
        if '- [ ]' in line:
            return line.replace('- [ ]', '').strip()
    
    return "All tasks complete"

def auto_improve():
    """Main improvement loop"""
    print("=== Self-Improvement Check ===")
    
    # 1. Check for error patterns
    top_error = check_errors()
    if top_error:
        print(f"⚠️  Top failure: {top_error[0]} ({top_error[1]}x)")
    
    # 2. Get today's task
    task = get_daily_task()
    print(f"📋 Today's task: {task}")
    
    # 3. Return what needs doing
    return {
        'error_pattern': top_error,
        'daily_task': task
    }

if __name__ == "__main__":
    auto_improve()
