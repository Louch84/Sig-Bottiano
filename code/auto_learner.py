#!/usr/bin/env python3
"""Auto-Learning: Learn from interactions automatically"""

import json
import os
from datetime import datetime

INTERACTIONS_FILE = "/Users/sigbotti/.openclaw/workspace/memory/interactions.json"

class AutoLearner:
    def __init__(self):
        self.file = INTERACTIONS_FILE
        self.data = self._load()
    
    def _load(self):
        if os.path.exists(self.file):
            with open(self.file, 'r') as f:
                return json.load(f)
        return {"interactions": [], "learnings": []}
    
    def learn(self, interaction_type, input_data, outcome, feedback=None):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "type": interaction_type,
            "input": input_data,
            "outcome": outcome,
            "feedback": feedback
        }
        
        self.data["interactions"].append(entry)
        
        if feedback == "accepted":
            self.data["learnings"].append({
                "from": input_data,
                "what_worked": outcome
            })
        
        with open(self.file, 'w') as f:
            json.dump(self.data, f, indent=2)
        
        return entry
    
    def get_learnings(self):
        return self.data.get("learnings", [])

learner = AutoLearner()
