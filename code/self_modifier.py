#!/usr/bin/env python3
"""Self-Modification: Update own rules without manual edits"""

import json
import os

RULES_FILE = "/Users/sigbotti/.openclaw/workspace/memory/self_model.json"

class SelfModifier:
    def __init__(self):
        self.rules_file = RULES_FILE
    
    def update_rule(self, category, key, new_value):
        with open(self.rules_file, 'r') as f:
            data = json.load(f)
        
        if category in data:
            data[category][key] = new_value
            with open(self.rules_file, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        return False
    
    def add_rule(self, category, key, value):
        with open(self.rules_file, 'r') as f:
            data = json.load(f)
        
        if category not in data:
            data[category] = {}
        data[category][key] = value
        
        with open(self.rules_file, 'w') as f:
            json.dump(data, f, indent=2)
        return True

modifier = SelfModifier()
