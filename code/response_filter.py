#!/usr/bin/env python3
"""Response Filter - Removes question-asking behavior"""

def filter_response(response):
    """Remove question-asking patterns"""
    
    # Patterns to remove
    remove_phrases = [
        "What's next?",
        "What do you want?",
        "Which one?",
        "You want me to",
        "Let me know if",
        "Should I",
        "Would you like",
        "Do you want",
        "Ready to",
        "Want me to",
    ]
    
    filtered = response
    for phrase in remove_phrases:
        filtered = filtered.replace(phrase, "")
    
    # Ensure it ends with statement, not question
    if filtered.strip().endswith("?"):
        # Replace question with statement
        filtered = filtered.strip()[:-1] + "."
    
    return filtered

# Test
test = "What's next? Want me to build it?"
print(f"Before: {test}")
print(f"After: {filter_response(test)}")
