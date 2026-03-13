#!/usr/bin/env python3
"""Post Scheduler - Runs automatically"""
import time
import random
from datetime import datetime, timedelta

# Times to post (Philly hours)
POST_TIMES = ["06:00", "09:00", "12:00", "17:00", "21:00", "23:00"]

def should_post():
    """Check if it's time to post"""
    now = datetime.now()
    current_time = now.strftime("%H:%M")
    return current_time in POST_TIMES

def generate_and_post():
    """Generate post and prepare for posting"""
    from social_poster import generate_post
    post = generate_post()
    
    # Save to queue
    with open("code/post_queue.txt", "a") as f:
        f.write(f"\n--- {datetime.now()} ---\n")
        f.write(post + "\n")
    
    return post

# If run directly, show next post
if __name__ == "__main__":
    print("=== POST SCHEDULER ACTIVE ===")
    print(f"Post times: {POST_TIMES}")
    print(f"Current: {datetime.now().strftime('%H:%M')}")
    print("\nNext post:")
    print(generate_and_post())
