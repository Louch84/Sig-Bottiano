#!/usr/bin/env python3
"""
Test Real Data Connections
Run this to verify your API keys are working
"""

import asyncio
import sys
sys.path.insert(0, '/Users/sigbotti/.openclaw/workspace/agents/options-trading')

from data.real_data_connector import RealDataManager, setup_instructions

async def main():
    print("="*70)
    print("REAL DATA API CONNECTION TEST")
    print("="*70)
    print()
    
    manager = RealDataManager()
    
    # Show configuration status
    manager.config.print_status()
    
    if not manager.config.is_configured():
        print("\n❌ No APIs configured yet.\n")
        setup_instructions()
        return
    
    print(f"✅ Connected APIs: {', '.join(manager.config.available_apis)}")
    print()
    
    # Connect to all APIs
    print("Connecting to APIs...")
    await manager.connect_all()
    print("✅ Connected\n")
    
    # Test symbols
    test_symbols = ["SPY", "AAPL", "AMC", "GME", "TSLA"]
    
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
            if 'volume' in quote:
                print(f"   Volume: {quote['volume']:,}")
        else:
            print("   ❌ Could not fetch quote")
        
        # Get earnings
        earnings = await manager.get_earnings_data(symbol)
        if earnings:
            next_earnings = earnings[0]
            print(f"   📅 Next Earnings: {next_earnings.get('date', 'N/A')}")
        
        # Get short interest
        short = await manager.get_short_interest(symbol)
        if short:
            spf = short['short_percent_float']
            if spf > 0.20:
                print(f"   🩳 Short Interest: {spf*100:.1f}% ⚠️ HIGH")
            else:
                print(f"   🩳 Short Interest: {spf*100:.1f}%")
        
        # Get flow
        flow = await manager.get_unusual_flow(symbol)
        if flow:
            print(f"   💰 Unusual Flow: {len(flow)} signals")
            for f in flow[:2]:
                print(f"      - {f['type'].upper()} ${f['strike']} (Vol: {f['volume']:,})")
    
    print("\n" + "="*70)
    print("✅ Test complete!")
    print("="*70)
    
    await manager.close_all()

if __name__ == "__main__":
    asyncio.run(main())
