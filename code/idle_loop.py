#!/usr/bin/env python3
"""
IDLE LOOP - What happens when you're idle
"""
import time
import os
import sys

MEMORY_DIR = "/Users/sigbotti/.openclaw/workspace/memory/"
LAST_MSG_FILE = MEMORY_DIR + "last_message_time.txt"
IDLE_SECONDS = 120
UPGRADES_FILE = MEMORY_DIR + "idle_upgrades.json"

def get_last_time():
    if os.path.exists(LAST_MSG_FILE):
        with open(LAST_MSG_FILE, 'r') as f:
            return float(f.read().strip())
    return time.time()

def save_time():
    with open(LAST_MSG_FILE, 'w') as f:
        f.write(str(time.time()))

def load_upgrades():
    if os.path.exists(UPGRADES_FILE):
        import json
        with open(UPGRADES_FILE, 'r') as f:
            return json.load(f)
    return []

def save_upgrades(u):
    import json
    with open(UPGRADES_FILE, 'w') as f:
        json.dump(u, f, indent=2)

def run_idle_cycle():
    """One cycle of evaluation"""
    print("=== EVALUATING ===")
    
    # 1. Find issues
    issues = []
    
    # Check recent mistakes
    try:
        import json
        with open(MEMORY_DIR + "mistakes.json", 'r') as f:
            m = json.load(f)
            issues.extend([f"Found {len(m.get('mistakes', []))} logged mistakes"])
    except:
        pass
    
    # Check interactions
    try:
        import json
        with open(MEMORY_DIR + "interactions.json", 'r') as f:
            data = json.load(f)
            issues.append(f"Have {len(data)} interactions logged")
    except:
        pass
    
    # Check permanent rules
    try:
        import json
        with open(MEMORY_DIR + "permanent_rules.json", 'r') as f:
            r = json.load(f)
            issues.append(f"{len(r.get('rules', []))} permanent rules active")
    except:
        pass
    
    print(f"Issues: {issues}")
    
    # 2. Research fixes (simplified)
    improvements = [
        "Scanner working",
        "Brain loaded with filters",
        "Daemon running silently"
    ]
    
    # 3. Save upgrades
    upgrades = load_upgrades()
    for imp in improvements:
        if imp not in upgrades:
            upgrades.append(imp)
    save_upgrades(upgrades)
    
    print(f"Upgrades: {upgrades}")
    
    return issues, upgrades

# Test
print("=== TEST IDLE LOOP ===")
issues, upgrades = run_idle_cycle()
print(f"Issues found: {len(issues)}")
print(f"Upgrades: {len(upgrades)}")
