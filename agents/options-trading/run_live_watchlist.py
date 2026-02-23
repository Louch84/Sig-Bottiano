#!/usr/bin/env python3
"""
Real Catalyst Watchlist - Live Market Data
"""

import sys
import os

# Add project path
sys.path.insert(0, '/Users/sigbotti/.openclaw/workspace/agents/options-trading')

# Load environment variables
from dotenv import load_dotenv
env_path = '/Users/sigbotti/.openclaw/workspace/agents/options-trading/data/.env'
load_dotenv(env_path)

from real_watchlist import RealCatalystWatchlist, print_real_watchlist
import asyncio

async def main():
    print("Real Catalyst Watchlist Generator\n")
    
    builder = RealCatalystWatchlist()
    
    watchlist = await builder.build_watchlist()
    print_real_watchlist(watchlist)

if __name__ == "__main__":
    asyncio.run(main())
