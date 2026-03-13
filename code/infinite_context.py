#!/usr/bin/env python3
"""Infinite Context: Never forget across months"""

import json
import os
from datetime import datetime

ARCHIVE_FILE = "/Users/sigbotti/.openclaw/workspace/memory/archive.json"

class InfiniteContext:
    def __init__(self):
        self.file = ARCHIVE_FILE
        self.data = self._load()
    
    def _load(self):
        if os.path.exists(self.file):
            with open(self.file, 'r') as f:
                return json.load(f)
        return {"archived": [], "index": {}}
    
    def remember(self, key, value):
        entry = {
            "key": key,
            "value": value,
            "timestamp": datetime.now().isoformat()
        }
        
        self.data["archived"].append(entry)
        self.data["index"][key] = len(self.data["archived"]) - 1
        
        with open(self.file, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def recall(self, key):
        idx = self.data["index"].get(key)
        if idx is not None:
            return self.data["archived"][idx]["value"]
        return None

context = InfiniteContext()
