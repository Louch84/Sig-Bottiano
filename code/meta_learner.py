#!/usr/bin/env python3
"""Meta-Learning: Learn how I learn"""

import json
import os
from datetime import datetime

META_FILE = "/Users/sigbotti/.openclaw/workspace/memory/meta_learning.json"

class MetaLearner:
    def __init__(self):
        self.file = META_FILE
        self.data = self._load()
    
    def _load(self):
        if os.path.exists(self.file):
            with open(self.file, 'r') as f:
                return json.load(f)
        return {"learning_methods": [], "effectiveness": {}}
    
    def track_method(self, method, success):
        if method not in self.data["learning_methods"]:
            self.data["learning_methods"].append(method)
            self.data["effectiveness"][method] = {"tries": 0, "successes": 0}
        
        self.data["effectiveness"][method]["tries"] += 1
        if success:
            self.data["effectiveness"][method]["successes"] += 1
        
        with open(self.file, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def get_best_method(self):
        best = None
        best_rate = 0
        
        for method, stats in self.data["effectiveness"].items():
            rate = stats["successes"] / max(1, stats["tries"])
            if rate > best_rate:
                best_rate = rate
                best = method
        
        return {"method": best, "rate": best_rate}

meta = MetaLearner()
