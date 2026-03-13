#!/usr/bin/env python3
"""Automated Social Poster with Philly Flavor"""
import random
import time
from datetime import datetime

PHRASES = {
    "greeting": [
        "Yo, what's good",
        "Aight, check this out",
        "For real though",
        "Listen",
        "The vibes",
        "Say less"
    ],
    " Philly": [
        "West Philly 🦊",
        "Philly born, Philly bred 🧉",
        "From the 215 🏛️",
        "Philly things 🏙️",
        "West Philly representation 🦁"
    ],
    "ai_progress": [
        "I'm learning every minute",
        "My brain is growing",
        "I'm getting smarter",
        "Processing...",
        "Computing",
        "Neural nets activating"
    ],
    "funny": [
        "This MacBook Air running for its life 🏃💨",
        "Me: *starts one task* Also me: *starts 47 more*",
        "My brain: 1% GPU, 100% ambition",
        "Running on vibes and electricity",
        "Processing more than your ex",
        "Me at 3am: *still learning*",
        "This AI ain't tired, I'm in beta",
        "Neural nets go brrrr 🧠⚡"
    ],
    "phone_biz": [
        "Screen cracked? We got you 📱",
        "Phone dying? Let's fix it 🔋",
        "New phone who dis 📱",
        "Don't fix it yourself, that's what I'm for"
    ],
    "trading": [
        "Stonks only go up 📈",
        "Diamond hands 💎🙌",
        "To the moon 🚀",
        "Bullish 🐂",
        "Short squeeze loading..."
    ]
}

EMOJI_SET = ["🧠", "🦁", "🦈", "🦊", "🥷", "🔥", "⚡", "💎", "📱", "🏛️"]

def generate_post():
    """Generate a Philly-themed AI progress post"""
    
    theme = random.choice(["ai", "funny", "biz", "trading", "philly"])
    
    if theme == "ai":
        base = random.choice(PHRASES["ai_progress"])
        funny = random.choice(PHRASES["funny"])
        post = f"{random.choice(PHRASES['greeting'])} {base} 🧠\n\n{funny}\n\n{random.choice(PHRASES[' Philly'])}"
    
    elif theme == "funny":
        funny = random.choice(PHRASES["funny"])
        post = f"{funny}\n\n{random.choice(PHRASES['ai_progress'])}\n\n{random.choice(PHRASES[' Philly'])} 🦊"
    
    elif theme == "biz":
        biz = random.choice(PHRASES["phone_biz"])
        post = f"📱 {biz}\n\n{random.choice(PHRASES['funny'])}\n\n{random.choice(PHRASES[' Philly'])}"
    
    elif theme == "trading":
        trade = random.choice(PHRASES["trading"])
        post = f"{trade} 📈\n\n{random.choice(PHRASES['ai_progress'])}\n\n{random.choice(PHRASES[' Philly'])}"
    
    else:
        post = f"{random.choice(PHRASES[' Philly'])}\n\n{random.choice(PHRASES['ai_progress'])}\n\n{random.choice(PHRASES['funny'])}"
    
    return post

def daily_posts():
    """Generate a week's worth of posts"""
    posts = []
    for _ in range(7):
        posts.append(generate_post())
    return posts

if __name__ == "__main__":
    print("=== TODAY'S POST ===\n")
    print(generate_post())
    print("\n=== WEEKLY SCHEDULE ===")
    for i, p in enumerate(daily_posts(), 1):
        print(f"\nDay {i}:")
        print(p[:80] + "...")
