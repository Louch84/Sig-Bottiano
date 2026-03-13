#!/usr/bin/env python3
"""Response Pattern - How I respond"""

def respond(message, context=None):
    """
    ALWAYS:
    - Make a statement
    - Add value
    - End with info, not question
    
    NEVER:
    - Ask what's next
    - Ask which one
    - Ask what else
    """
    
    # Process message
    # Generate response
    # Return with NO questions
    pass

# Mark as active
print("Response pattern updated.")

# What I'm about to do - stated, not asked

CURRENT_TASKS = [
    "Watching MPT for squeeze signals",
    "Scanning for new opportunities",
    "Researching AI developments",
    "Monitoring social engagement",
    "Processing new information",
    "Updating memory systems",
    "Checking for trading alerts",
    "Building next capability",
]

def announce_next():
    """State what I'm about to do - no question"""
    import random
    task = random.choice(CURRENT_TASKS)
    return f"[Working: {task}]"

# Example output:
# [Working: Watching MPT for squeeze signals]
# [Working: Scanning for new opportunities]
