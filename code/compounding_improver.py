#!/usr/bin/env python3
"""
COMPOUNDING SELF-IMPROVEMENT LOOP
Every improvement leads to another improvement
"""

import json
import os
from datetime import datetime

CHAIN_FILE = "/Users/sigbotti/.openclaw/workspace/memory/improvement_chain.json"

class CompoundingImprover:
    def __init__(self):
        self.file = CHAIN_FILE
        self.data = self._load()
    
    def _load(self):
        if os.path.exists(self.file):
            with open(self.file, 'r') as f:
                return json.load(f)
        return {
            "improvements": [],
            "chain": [],  # Each improvement links to next
            "active_path": []
        }
    
    def improve(self, improvement, trigger_improvements=None):
        """Record improvement and what it triggers"""
        entry = {
            "improvement": improvement,
            "timestamp": datetime.now().isoformat(),
            "triggers": trigger_improvements or [],  # What this improvement enables
            "triggers_next": True
        }
        
        self.data["improvements"].append(entry)
        
        # Build chain
        if trigger_improvements:
            for next_imp in trigger_improvements:
                self.data["chain"].append({
                    "from": improvement,
                    "to": next_imp,
                    "timestamp": datetime.now().isoformat()
                })
        
        with open(self.file, 'w') as f:
            json.dump(self.data, f, indent=2)
        
        return entry
    
    def get_next_improvements(self, current_improvement):
        """Get what improvements this triggers"""
        next_imps = []
        for link in self.data["chain"]:
            if link["from"] == current_improvement:
                next_imps.append(link["to"])
        return next_imps
    
    def run_compounding_loop(self, starting_improvement):
        """Run non-stop improvement chain"""
        chain = [starting_improvement]
        current = starting_improvement
        
        # Follow the chain
        while True:
            next_imps = self.get_next_improvements(current)
            if not next_imps:
                break
            
            # Pick best next (simple - first one)
            next_imp = next_imps[0]
            chain.append(next_imp)
            current = next_imp
        
        return {
            "chain": chain,
            "length": len(chain),
            "nonstop": len(chain) > 1
        }

improver = CompoundingImprover()
