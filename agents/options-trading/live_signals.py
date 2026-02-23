#!/usr/bin/env python3
"""
Live Options Signals - Continuous scanning mode
Usage: python3 live_signals.py
"""

import asyncio
import sys
from signals import OptionsSignalsAgent, SignalType, TradeDuration

async def main():
    agent = OptionsSignalsAgent()
    
    print("="*60)
    print("⚡ LIVE OPTIONS SIGNALS")
    print("Press Ctrl+C to stop")
    print("="*60)
    print()
    
    scan = 0
    try:
        while True:
            scan += 1
            print(f"\n--- Scan #{scan} at {asyncio.get_event_loop().time():.0f}s ---")
            
            signals = await agent.scan_for_signals()
            
            if not signals:
                print("No signals this scan.")
            else:
                for signal in signals[:3]:  # Top 3 only
                    emoji = "🟢 CALL" if signal.signal_type == SignalType.CALL else "🔴 PUT"
                    duration = "⚡" if signal.duration == TradeDuration.DAY_TRADE else "📈"
                    print(f"{duration} {signal.symbol} {emoji} ${signal.strike:.0f} {signal.dte}DTE | {signal.confidence:.0%}")
            
            await asyncio.sleep(30)  # Scan every 30 seconds
            
    except KeyboardInterrupt:
        print("\n\nStopped.")
        
        # Summary
        if agent.signals_history:
            dt = len([s for s in agent.signals_history if s.duration == TradeDuration.DAY_TRADE])
            sw = len([s for s in agent.signals_history if s.duration == TradeDuration.SWING])
            calls = len([s for s in agent.signals_history if s.signal_type == SignalType.CALL])
            puts = len([s for s in agent.signals_history if s.signal_type == SignalType.PUT])
            
            print(f"\nSession: {len(agent.signals_history)} signals ({dt} day trades, {sw} swings)")
            print(f"         {calls} calls, {puts} puts")

if __name__ == "__main__":
    asyncio.run(main())
