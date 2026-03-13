#!/usr/bin/env python3
"""Memory Search - Semantic search through memories"""
import os
import json

def search_memories(query):
    """Search through memory files"""
    results = []
    
    memory_dir = "memory"
    if not os.path.exists(memory_dir):
        return ["No memories found"]
    
    for filename in os.listdir(memory_dir):
        if filename.endswith('.md'):
            filepath = os.path.join(memory_dir, filename)
            with open(filepath, 'r') as f:
                content = f.read()
                if query.lower() in content.lower():
                    # Find context around the match
                    lines = content.split('\n')
                    for i, line in enumerate(lines):
                        if query.lower() in line.lower():
                            results.append({
                                "file": filename,
                                "line": i+1,
                                "text": line.strip()[:100]
                            })
    
    return results if results else ["No matches found"]

# Test
if __name__ == "__main__":
    print("Testing memory search...")
    print(search_memories("MPT"))
