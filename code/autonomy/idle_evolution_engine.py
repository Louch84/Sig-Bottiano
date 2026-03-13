"""
AutonomousSoul - Core self-improvement engine
"""
import time
import os
import json
from datetime import datetime

class AutonomousSoul:
    def __init__(self):
        self.memory_dir = "/Users/sigbotti/.openclaw/workspace/memory/"
        self.last_interaction = time.time()
        self.idle_threshold = 120  # 2 minutes
        self.upgrades = []
        self.load_state()
    
    def load_state(self):
        """Load previous state"""
        state_file = self.memory_dir + "soul_state.json"
        if os.path.exists(state_file):
            with open(state_file, 'r') as f:
                data = json.load(f)
                self.upgrades = data.get('upgrades', [])
    
    def save_state(self):
        """Save current state"""
        state_file = self.memory_dir + "soul_state.json"
        with open(state_file, 'w') as f:
            json.dump({
                'upgrades': self.upgrades,
                'last_update': datetime.now().isoformat()
            }, f)
    
    def update_interaction_timestamp(self):
        """Call when user interacts"""
        self.last_interaction = time.time()
    
    def is_idle(self):
        """Check if idle > threshold"""
        return (time.time() - self.last_interaction) > self.idle_threshold
    
    def get_idle_time(self):
        """Get seconds idle"""
        return time.time() - self.last_interaction
    
    def add_upgrade(self, upgrade: str):
        """Log an upgrade"""
        if upgrade not in self.upgrades:
            self.upgrades.append(upgrade)
            self.save_state()
    
    def get_upgrades(self) -> list:
        """Get all upgrades"""
        return self.upgrades
    
    async def idle_loop(self):
        """Main idle evaluation loop"""
        while True:
            if self.is_idle():
                # Run evaluation
                issues = await self.evaluate()
                fixes = await self.research_fixes(issues)
                await self.apply_fixes(fixes)
                
                # Reset timer
                self.update_interaction_timestamp()
            
            await asyncio.sleep(30)
    
    async def evaluate(self) -> list:
        """Find issues"""
        issues = []
        
        # Check system state
        try:
            with open(self.memory_dir + "permanent_rules.json", 'r') as f:
                rules = json.load(f)
                issues.append(f"Rules: {len(rules.get('rules', []))}")
        except:
            pass
        
        return issues
    
    async def research_fixes(self, issues: list) -> list:
        """Research fixes for issues"""
        # Placeholder - would do real research
        return []
    
    async def apply_fixes(self, fixes: list):
        """Apply fixes"""
        for fix in fixes:
            self.add_upgrade(fix)

# Need asyncio
import asyncio
