#!/usr/bin/env python3
"""Image Gen - Generate social media images"""
import os

# Check if we can use the skill
# Use the skill: openai-image-gen

def generate(prompt):
    """Generate an image (requires API key)"""
    # This would use openai-image-gen skill
    return {
        "status": "ready",
        "skill": "openai-image-gen",
        "note": "Need OPENAI_API_KEY in .env to use",
        "prompt": prompt
    }

def test():
    """Test if ready"""
    if os.getenv("OPENAI_API_KEY"):
        return "Ready - API key found"
    return "Not ready - Need OPENAI_API_KEY"

if __name__ == "__main__":
    print("=== IMAGE GEN ===")
    print(test())
