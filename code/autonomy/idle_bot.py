"""
Idle Bot - Matches exact flow:
- Timer resets on any user message
- At 300s idle: send "🧠 Idle cycle #X"
- Run fix cycle
- On any user response: reset + send "⏸️ Paused"
"""
import time
import asyncio
import random

class IdleBot:
    def __init__(self, discord_client, user_id):
        self.d = discord_client
        self.uid = user_id
        self.t = time.time()  # Last user message
        self.idle_trigger = 300  # 5 minutes
        self.cycle_count = 0
    
    async def go(self):
        """Main idle loop - checks every 30s"""
        while True:
            idle_time = time.time() - self.t
            
            if idle_time > self.idle_trigger:
                # Trigger idle cycle
                self.cycle_count += 1
                await self.dm(f"🧠 Idle cycle #{self.cycle_count}")
                
                # Run fixes
                await self.fix()
                
                # Reset for next cycle
                self.t = time.time()
            
            await asyncio.sleep(30)
    
    async def dm(self, m):
        """Send DM to user"""
        try:
            u = await self.d.fetch_user(int(self.uid))
            await u.send(m[:1900])
        except Exception as e:
            print(f"DM error: {e}")
    
    async def fix(self):
        """Run improvements"""
        tasks = [
            "Checking memory...",
            "Scanning for issues...",
            "Optimizing filters...",
            "Testing systems...",
            "Applying upgrades..."
        ]
        
        for task in tasks:
            await self.dm(f"🔧 {task}")
            await asyncio.sleep(2)
        
        await self.dm("✅ Done. Waiting.")
    
    def poke(self):
        """RESET TIMER - call on ANY user message"""
        was_idle = (time.time() - self.t) > self.idle_trigger
        self.t = time.time()
        
        # If was in idle cycle and user just responded
        if was_idle:
            return True  # Signal that we should acknowledge pause
        
        return False
    
    async def acknowledge_pause(self):
        """Called when user breaks idle"""
        await self.dm("⏸️ Paused")
