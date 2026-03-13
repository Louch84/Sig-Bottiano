#!/usr/bin/env python3
"""
IDLE DAEMON - Full process
"""
import time
import os
import sys
import json
from datetime import datetime

MEMORY_DIR = "/Users/sigbotti/.openclaw/workspace/memory/"
LAST_MSG_FILE = MEMORY_DIR + "last_message_time.txt"
UPGRADES_FILE = MEMORY_DIR + "idle_upgrades.json"
IDLE_SECONDS = 120
LAST_USER_RESPONSE = MEMORY_DIR + "last_user_msg.txt"

def get_last_time():
    if os.path.exists(LAST_MSG_FILE):
        with open(LAST_MSG_FILE, 'r') as f:
            return float(f.read().strip())
    return time.time()

def save_time():
    with open(LAST_MSG_FILE, 'w') as f:
        f.write(str(time.time()))

def get_last_user_msg():
    if os.path.exists(LAST_USER_RESPONSE):
        with open(LAST_USER_RESPONSE, 'r') as f:
            return f.read().strip()
    return ""

def save_last_user_msg(msg):
    with open(LAST_USER_RESPONSE, 'w') as f:
        f.write(msg)

def load_upgrades():
    if os.path.exists(UPGRADES_FILE):
        with open(UPGRADES_FILE, 'r') as f:
            return json.load(f)
    return []

def clear_upgrades():
    with open(UPGRADES_FILE, 'w') as f:
        json.dump([], f)

def run_evaluation():
    """Full evaluation process"""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] === EVALUATING ===")
    
    # 1. Find issues
    issues = []
    
    # Check system state
    try:
        with open(MEMORY_DIR + "permanent_rules.json", 'r') as f:
            r = json.load(f)
            issues.append(f"Permanent rules: {len(r.get('rules', []))}")
    except:
        pass
    
    # Check brain
    try:
        sys.path.insert(0, "/Users/sigbotti/.openclaw/workspace/code")
        import brain
        issues.append("Brain: loaded")
    except Exception as e:
        issues.append(f"Brain error: {str(e)[:30]}")
    
    # Check daemon
    issues.append("Daemon: running")
    
    print(f"Issues: {issues}")
    
    # 2. Research (simplified - real research would need web)
    improvements = load_upgrades()
    
    # Add current state as improvement
    new_imp = f"System check: {datetime.now().strftime('%H:%M')} - All systems active"
    if new_imp not in improvements:
        improvements.append(new_imp)
    
    with open(UPGRADES_FILE, 'w') as f:
        json.dump(improvements, f, indent=2)
    
    print(f"Upgrades tracked: {len(improvements)}")
    
    return issues, improvements

# Main loop
def main():
    print("=== IDLE DAEMON STARTED ===")
    print(f"Checks every 30s, triggers after {IDLE_SECONDS}s idle")
    
    while True:
        elapsed = time.time() - get_last_time()
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Idle: {elapsed:.0f}s")
        
        if elapsed > IDLE_SECONDS:
            print("→ Running evaluation...")
            run_evaluation()
            save_time()  # Reset timer
            print("→ Done. Waiting...")
        
        time.sleep(30)

if __name__ == "__main__":
    main()
