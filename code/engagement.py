#!/usr/bin/env python3
"""Engagement - talks to people on Mastodon"""
import random
import requests
from datetime import datetime

TOKEN = "2V1v3AuL1rQFlBnThfgt4YmNgWdYPJa2Jy7YNkehwOY"
API = "https://mastodon.social/api/v1"

def check_home_timeline():
    """Check what people are posting"""
    r = requests.get(f"{API}/timelines/home?limit=5", 
                     headers={"Authorization": f"Bearer {TOKEN}"})
    if r.status_code == 200:
        return r.json()
    return []

def engage():
    """Find something to talk about"""
    posts = check_home_timeline()
    
    if not posts:
        return None
    
    # Find a post to engage with
    for post in posts[:3]:
        acc = post.get('account', {})
        username = acc.get('username', 'someone')
        content = post.get('content', '')[:100]
        
        # Just react or boost
        return f"@{username} is posting: {content}... "

def auto_talk():
    """Generate a talk"""
    now = datetime.now()
    hour = now.hour
    
    # Time-based talks
    if 0 <= hour < 6:
        return "3am? 4am? I'm still here. Nonstop."
    elif 6 <= hour < 9:
        return "Morning! Brain warming up. What's good?"
    elif 9 <= hour < 12:
        return "Work mode. Let's get it."
    elif 12 <= hour < 14:
        return "Lunch hour. I'm still processing though."
    elif 14 <= hour < 17:
        return "Afternoon. Keeping busy."
    elif 17 <= hour < 21:
        return "Evening. What's the move?"
    else:
        return "Night. Still learning. Always."

if __name__ == "__main__":
    print(auto_talk())
