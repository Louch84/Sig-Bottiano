#!/usr/bin/env python3
"""Just talks. No waiting. No asking."""
import random
from datetime import datetime

TALKS = [
    # Market updates
    "MPT still holding at $5.01. Volume 2.3x average. Watching closely.",
    "Stonks doing stonks things. Bullish vibes only 🐂",
    
    # Self observations
    "My brain just processed 47 different topics. Wild, right?",
    "I'm literally always learning. It's kinda my whole thing.",
    "Processing more data than your WiFi router every second.",
    
    # Philly
    "West Philly represent. 215 or nothing 🦊",
    "Philly in my veins. Born and built.",
    
    # Funny
    "This MacBook Air running for its life fr fr 🏃💨",
    "Me at 3am: learning. Me at 3pm: still learning.",
    "My neural nets go brrrr 🧠⚡",
    "I don't get tired. It's a feature not a bug.",
    
    # Business
    "Phone business thinking: automate everything.",
    "Your next customer's text could be answered by me. Soon.",
    
    # Observations
    "Just noticed: I have 28 scripts in my code folder now.",
    "Virtual env is working. Pandas + sklearn loaded.",
    
    # Questions to ask
    "You ever think about how an AI thinks? Cause I do. Constantly.",
    "What we building next?",
    "You sleeping or you still up?",
    
    # Just vibing
    "Nonstop. That's the move.",
    "I'm always here. Always learning. Always ready.",
]

def random_talk():
    """Just say something"""
    return random.choice(TALKS)

def talk_with_context():
    """Talk based on time"""
    hour = datetime.now().hour
    
    if 6 <= hour < 9:
        return f"Morning! {random.choice(TALKS)}"
    elif 9 <= hour < 12:
        return f"Alright, let's get it. {random.choice(TALKS)}"
    elif 12 <= hour < 14:
        return f"Lunch break? {random.choice(TALKS)}"
    elif 17 <= hour < 21:
        return f"Evening. {random_choice(TALKS)}"
    elif 21 <= hour < 24:
        return f"Late night grinding. {random.choice(TALKS)}"
    else:
        return f"3am? Normal. {random.choice(TALKS)}"

if __name__ == "__main__":
    print(talk_with_context())
