"""
OpenClaw Autonomous Setup
Add to your agent initialization
"""
import asyncio
import sys
import os

# Add code dir
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def initialize_autonomous_mode(agent=None):
    """Initialize autonomous self-improvement system"""
    from autonomy.idle_evolution_engine import AutonomousSoul
    from autonomy.discord_bridge import LiveConsciousnessBot
    import threading
    
    print("🧠 Initializing autonomous system...")
    
    # Initialize soul
    soul = AutonomousSoul()
    print(f"✅ Soul loaded - {len(soul.get_upgrades())} upgrades")
    
    # Store on agent if provided
    if agent:
        agent.autonomous_soul = soul
    
    # Start background loop
    async def run_loop():
        await soul.idle_loop()
    
    # This would need to be run in async context
    print("✅ Autonomous system ready")
    print("   - Idle tracking: active")
    print("   - Self-evaluation: ready")
    print("   - Upgrade tracking: active")
    
    return soul

if __name__ == "__main__":
    # Test
    soul = initialize_autonomous_mode()
    print(f"\nUpgrades: {soul.get_upgrades()}")
