#!/usr/bin/env python3
"""Advanced memory store using simple JSON with semantic search approximation"""
import argparse
import json
import os
import hashlib
from datetime import datetime
from pathlib import Path

MEMORY_DIR = os.path.expanduser('~/.openclaw/memory/advanced')

def ensure_dir():
    os.makedirs(MEMORY_DIR, exist_ok=True)

def store_memory(content, tags=None, metadata=None):
    ensure_dir()
    
    memory_id = hashlib.md5(f"{content}{datetime.now().isoformat()}".encode()).hexdigest()[:12]
    
    memory = {
        'id': memory_id,
        'content': content,
        'tags': tags.split(',') if tags else [],
        'metadata': metadata or {},
        'created': datetime.now().isoformat(),
        'accessed': datetime.now().isoformat(),
        'access_count': 0
    }
    
    # Simple word-based index for search
    words = set(content.lower().split())
    memory['index'] = list(words)
    
    filepath = os.path.join(MEMORY_DIR, f"{memory_id}.json")
    with open(filepath, 'w') as f:
        json.dump(memory, f, indent=2)
    
    return {'success': True, 'id': memory_id}

def search_memories(query, limit=10, tags=None, min_score=0.0):
    ensure_dir()
    
    query_words = set(query.lower().split())
    results = []
    
    for fname in os.listdir(MEMORY_DIR):
        if not fname.endswith('.json'):
            continue
        
        with open(os.path.join(MEMORY_DIR, fname)) as f:
            memory = json.load(f)
        
        # Filter by tags if specified
        if tags:
            mem_tags = set(memory.get('tags', []))
            if not set(tags.split(',')).intersection(mem_tags):
                continue
        
        # Simple similarity score
        mem_words = set(memory.get('index', []))
        if not mem_words:
            continue
        
        overlap = len(query_words.intersection(mem_words))
        score = overlap / max(len(query_words), len(mem_words), 1)
        
        if score >= min_score:
            memory['score'] = round(score, 3)
            results.append(memory)
    
    results.sort(key=lambda x: x['score'], reverse=True)
    return results[:limit]

def list_memories():
    ensure_dir()
    memories = []
    for fname in os.listdir(MEMORY_DIR):
        if fname.endswith('.json'):
            with open(os.path.join(MEMORY_DIR, fname)) as f:
                memories.append(json.load(f))
    return memories

def delete_memory(memory_id):
    filepath = os.path.join(MEMORY_DIR, f"{memory_id}.json")
    if os.path.exists(filepath):
        os.remove(filepath)
        return {'success': True}
    return {'error': f'Memory {memory_id} not found'}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--content', '-c')
    parser.add_argument('--tags', '-t')
    parser.add_argument('--metadata', '-m')
    parser.add_argument('--json', '-j', action='store_true')
    args = parser.parse_args()
    
    if args.content:
        metadata = json.loads(args.metadata) if args.metadata else {}
        result = store_memory(args.content, args.tags, metadata)
        
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"Stored memory: {result['id']}")
    else:
        print("Error: --content required")
        sys.exit(1)

if __name__ == '__main__':
    main()
