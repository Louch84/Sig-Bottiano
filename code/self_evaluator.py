#!/usr/bin/env python3
"""
Self-Evaluation & Auto-Improvement System
Runs after every response to check if improvement is needed
"""
import json
import os
from datetime import datetime

SELF_EVAL_LOG = "/Users/sigbotti/.openclaw/workspace/memory/self_eval_log.json"
IMPROVEMENT_QUEUE = "/Users/sigbotti/.openclaw/workspace/memory/self_improvement_queue.md"

def load_log():
    """Load self-eval history"""
    if os.path.exists(SELF_EVAL_LOG):
        with open(SELF_EVAL_LOG, 'r') as f:
            return json.load(f)
    return {"evals": [], "improvements": []}

def save_log(log):
    """Save self-eval history"""
    with open(SELF_EVAL_LOG, 'w') as f:
        json.dump(log, f, indent=2)

def check_idle_trigger(user_message: str, my_response: str) -> bool:
    """
    Check if I should trigger self-improvement
    Returns True if idle trigger detected
    """
    idle_triggers = [
        "what's next", "what else", "what do you want",
        "you good", "anything else", "that's it",
        "ok thanks", "cool thanks", "bet"
    ]
    
    user_lower = user_message.lower().strip()
    
    # If user gave explicit task, don't trigger
    task_words = ["do", "make", "build", "run", "scan", "check", "find", "get", "create"]
    for tw in task_words:
        if tw in user_lower:
            return False
    
    # If response was short acknowledgment, might be idle
    for trigger in idle_triggers:
        if trigger in user_lower:
            return True
    
    # If my response was just waiting
    waiting_phrases = ["what else", "let me know", "you need"]
    for wp in waiting_phrases:
        if wp in my_response.lower():
            return True
    
    return False

def run_self_eval() -> dict:
    """
    Run self-evaluation
    Returns dict with findings and next action
    """
    log = load_log()
    
    # Check recent failures from mistakes log
    mistakes = []
    try:
        with open("/Users/sigbotti/.openclaw/workspace/memory/mistakes.json", 'r') as f:
            data = json.load(f)
            mistakes = data.get('mistakes', [])[-5:]  # Last 5
    except:
        pass
    
    # What gaps exist?
    gaps = [
        {"gap": "Short interest data", "status": "FIXED", "source": "Yahoo Finance"},
        {"gap": "Real news headlines", "status": "PARTIAL", "source": "yfinance limited"},
        {"gap": "Options flow data", "status": "MISSING", "source": "Need API"},
        {"gap": "Discord auto-post", "status": "MISSING", "source": "Webhook ready"},
        {"gap": "Local LLM speed", "status": "SLOW", "source": "Need optimization"},
    ]
    
    # What works?
    works = [
        "Scanner v5 with short interest",
        "MPT tracking to 3/20",
        "Config timeout fix",
        "Memory system"
    ]
    
    # Pick highest priority gap
    for gap in gaps:
        if gap["status"] != "FIXED":
            next_action = f"Research {gap['gap']}"
            break
    else:
        next_action = "Scan for new improvements"
    
    # Record eval
    eval_entry = {
        "timestamp": datetime.now().isoformat(),
        "works": works,
        "gaps": gaps,
        "mistakes": mistakes,
        "next_action": next_action
    }
    
    log["evals"].append(eval_entry)
    save_log(log)
    
    return eval_entry

def get_current_improvements() -> list:
    """Get current improvement queue"""
    improvements = []
    try:
        with open(IMPROVEMENT_QUEUE, 'r') as f:
            content = f.read()
            # Extract items from markdown
            lines = content.split('\n')
            for line in lines:
                if line.strip().startswith('-') or line.strip().startswith('*'):
                    improvements.append(line.strip())
    except:
        pass
    return improvements

if __name__ == "__main__":
    print("=== SELF-EVALUATION SYSTEM ===\n")
    
    # Run eval
    result = run_self_eval()
    
    print(f"Works: {', '.join(result['works'][:3])}")
    print(f"\nGaps:")
    for g in result['gaps']:
        print(f"  - {g['gap']}: {g['status']}")
    
    print(f"\n→ Next: {result['next_action']}")
