#!/usr/bin/env python3
"""Search advanced memory"""
import argparse
import json
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from store_memory import search_memories

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--query', '-q', required=True)
    parser.add_argument('--limit', '-l', type=int, default=10)
    parser.add_argument('--filter-tags', '-t')
    parser.add_argument('--min-score', type=float, default=0.0)
    parser.add_argument('--json', '-j', action='store_true')
    args = parser.parse_args()
    
    results = search_memories(args.query, args.limit, args.filter_tags, args.min_score)
    
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        if not results:
            print("No memories found")
        else:
            for r in results:
                print(f"[{r['score']}] {r['id'][:8]}: {r['content'][:80]}...")
                if r.get('tags'):
                    print(f"     Tags: {', '.join(r['tags'])}")
                print()

if __name__ == '__main__':
    main()
