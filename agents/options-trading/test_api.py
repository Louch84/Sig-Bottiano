#!/usr/bin/env python3
"""
Test Real Data Connections with Virtual Environment
"""

import sys
import os

# Add project path
sys.path.insert(0, '/Users/sigbotti/.openclaw/workspace/agents/options-trading')

# Load environment variables from .env file
from dotenv import load_dotenv
env_path = '/Users/sigbotti/.openclaw/workspace/agents/options-trading/data/.env'
load_dotenv(env_path)

# Verify key is loaded
finnhub_key = os.getenv("FINNHUB_API_KEY", "")
if finnhub_key and "your_" not in finnhub_key:
    print(f"✅ Finnhub key loaded: {finnhub_key[:10]}...")
else:
    print("❌ Finnhub key not found in .env")
    sys.exit(1)

from data.real_data_connector import RealDataManager, setup_instructions
import asyncio

async def main():
    print("="*70)
    print("REAL DATA API CONNECTION TEST")
    print("="*70)
    print()
    
    manager = RealDataManager()
    
    # Show configuration status
    manager.config.print_status()
    
    if not manager.config.is_configured():
        print("\n❌ No APIs configured.\n")
        setup_instructions()
        return
    
    print(f"✅ Connected APIs: {', '.join(manager.config.available_apis)}")
    print()
    
    # Connect to all APIs
    print("Connecting to APIs...")
    await manager.connect_all()
    print("✅ Connected\n")
    
    # Test symbols
    test_symbols = ["AAPL", "TSLA", "AMC", "GME"]
    
    print(f"Fetching data for: {', '.join(test_symbols)}\n")
    print("-"*70)
    
    for symbol in test_symbols:
        print(f"\n📊 {symbol}:")
        
        # Get quote
        quote = await manager.get_best_quote(symbol)
        if quote:
            print(f"   Price: ${quote['price']:.2f} (via {quote['source']})")
            if 'change_percent' in quote:
                emoji = "🟢" if quote['change_percent'] > 0 else "🔴"
                print(f"   Change: {emoji} {quote['change_percent']:.2f}%")
        else:
            print("   ❌ Could not fetch quote")
        
        # Get earnings
        earnings = await manager.get_earnings_data(symbol)
        if earnings:
            print(f"   📅 Earnings: {len(earnings)} events found")
        
        # Get short interest
        short = await manager.get_short_interest(symbol)
        if short:
            spf = short['short_percent_float']
            print(f"   🩳 Short: {spf*100:.1f}%")
    
    print("\n" + "="*70)
    print("✅ Test complete!")
    print("="*70)
    
    await manager.close_all()

if __name__ == "__main__":
    asyncio.run(main())
