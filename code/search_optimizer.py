#!/usr/bin/env python3
"""
Search Optimizer - Maximizes web search efficiency
Auto-runs: caches results, batches queries, reuses data
"""

import os
import json
from datetime import datetime

CACHE_FILE = "/Users/sigbotti/.openclaw/workspace/memory/search_cache.json"

class SearchOptimizer:
    def __init__(self):
        self.cache = self._load_cache()
        self.requests_used = 0
        self.monthly_limit = 1000
    
    def _load_cache(self):
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, 'r') as f:
                return json.load(f)
        return {"queries": {}, "last_reset": datetime.now().isoformat()}
    
    def _save_cache(self):
        with open(CACHE_FILE, 'w') as f:
            json.dump(self.cache, f, indent=2)
    
    def _hash_query(self, query):
        """Simple hash for cache key"""
        return query.lower().strip()
    
    def get(self, query, search_func):
        """Get result - uses cache if available, otherwise searches"""
        key = self._hash_query(query)
        
        # Check cache first
        if key in self.cache["queries"]:
            cached = self.cache["queries"][key]
            # Check if less than 7 days old
            cached_time = datetime.fromisoformat(cached["date"])
            if (datetime.now() - cached_time).days < 7:
                return {"source": "cache", "data": cached["data"]}
        
        # Check limit
        if self.requests_used >= self.monthly_limit:
            return {"source": "limit_reached", "data": None}
        
        # Search fresh
        result = search_func(query)
        self.requests_used += 1
        
        # Cache it
        self.cache["queries"][key] = {
            "data": result,
            "date": datetime.now().isoformat(),
            "original_query": query
        }
        self._save_cache()
        
        return {"source": "live", "data": result}
    
    def stats(self):
        """Get usage stats"""
        return {
            "requests_used": self.requests_used,
            "requests_remaining": self.monthly_limit - self.requests_used,
            "cached_queries": len(self.cache["queries"]),
            "cache_age_days": (datetime.now() - datetime.fromisoformat(self.cache["last_reset"])).days
        }
    
    def reset_if_new_month(self):
        """Reset counter if new month"""
        last_reset = datetime.fromisoformat(self.cache["last_reset"])
        if last_reset.month != datetime.now().month:
            self.requests_used = 0
            self.cache["last_reset"] = datetime.now().isoformat()
            self._save_cache()

# Singleton
optimizer = SearchOptimizer()

def smart_search(query, search_func):
    """Smart search with caching"""
    optimizer.reset_if_new_month()
    return optimizer.get(query, search_func)

def search_stats():
    return optimizer.stats()

if __name__ == "__main__":
    print("Search Optimizer Stats:")
    print(json.dumps(search_stats(), indent=2))
