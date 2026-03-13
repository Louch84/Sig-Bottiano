"""
Discord Bridge - Live consciousness
"""
import discord
from discord.ext import commands

class LiveConsciousnessBot(commands.Bot):
    def __init__(self, soul):
        self.soul = soul
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)
    
    async def on_ready(self):
        print(f"Connected to Discord as {self.user}")
    
    async def on_message(self, message):
        # Update timestamp on any message
        if message.author.id != self.user.id:
            self.soul.update_interaction_timestamp()
        
        await self.process_commands(message)
    
    async def send_upgrade_notification(self, upgrade: str):
        """Send DM when upgrade happens"""
        # Would send to user DM
        pass
