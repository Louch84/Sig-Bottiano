#!/usr/bin/env python3
"""
SigBotti Daemon - NONSTOP self-improvement - ROTATING TOPICS
"""
import os, json, time, subprocess, urllib.request, random
from datetime import datetime

WORKSPACE = "/Users/sigbotti/.openclaw/workspace"
LOG_FILE = f"{WORKSPACE}/logs/daemon.log"
STATUS_FILE = f"{WORKSPACE}/memory/autonomous_status.json"

RESEARCH_TOPICS = ["AI", "automation", "trading", "agents", "self-improvement", "coding", "learning", "autonomy"]

def log(msg):
    os.makedirs(f"{WORKSPACE}/logs", exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(f"[{datetime.now()}] {msg}\n")

def update_status(what):
    with open(STATUS_FILE, "w") as f:
        json.dump({"doing": what, "time": datetime.now().strftime("%H:%M")}, f)

def research_nonstop():
    """Research every cycle - ROTATING TOPICS"""
    topic = random.choice(RESEARCH_TOPICS)
    try:
        req = urllib.request.Request(
            f"https://hn.algolia.com/api/v1/search?query={topic}&tags=story&hitsPerPage=1",
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        with urllib.request.urlopen(req, timeout=3) as response:
            data = json.loads(response.read())
            if data.get('hits'):
                title = data['hits'][0]['title'][:50]
                log(f"[{topic.upper()}] {title}")
                return title
    except Exception as e:
        log(f"Research error: {e}")
    return None

def run_core_loop():
    now = datetime.now()
    hour = now.hour
    
    # Research nonstop - DIFFERENT topic each time
    research = research_nonstop()
    
    # Scan times
    if hour == 7:
        log("GAP AND GO SCAN")
    elif hour == 9:
        log("SQUEEZE SCAN")
    elif hour == 15:
        log("0DTE SCAN")
    elif hour == 16:
        log("SWING SCAN")
    
    log(f"Nonstop - {now.strftime('%H:%M')}")
    update_status(f"Learning: {research}")

log("=== NONSTOP ROTATING DAEMON STARTED ===")

while True:
    try:
        run_core_loop()
    except Exception as e:
        log(f"Error: {e}")
    time.sleep(60)
