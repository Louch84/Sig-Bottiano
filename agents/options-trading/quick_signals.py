#!/usr/bin/env python3
"""
Quick Options Signals - Command Line Tool
Instant CALL/PUT signals with day trade vs swing labels

Usage:
    python3 quick_signals.py           # Scan all and show top signals
    python3 quick_signals.py --live    # Continuous scanning
    python3 quick_signals.py SPY TSLA  # Scan specific symbols
"""

import sys
import asyncio
from simple_signals import OptionsSignalsAgent, SignalType, TradeDuration

def print_banner():
    print("="*60)
    print("⚡ OPTIONS SIGNALS")
    print("Simple CALL/PUT | Day Trade vs Swing")
    print("="*60)
    print()

def print_signal(signal):
    """Print formatted signal"""
    duration_emoji = "⚡" if signal.duration == TradeDuration.DAY_TRADE else "📈"
    signal_emoji = "🟢 CALL" if signal.signal_type == SignalType.CALL else "🔴 PUT"
    
    print(f"{duration_emoji} {signal.symbol} | {signal_emoji} | {signal.confidence:.0%} confidence")
    print(f"   Entry: ${signal.entry_price:.2f} | Strike: ${signal.strike:.2f} | {signal.dte} DTE")
    print(f"   Stop: ${signal.stop_loss:.2f} | T1: ${signal.target_1:.2f} | T2: ${signal.target_2:.2f}")
    print(f"   R:R = 1:{signal.risk_reward:.1f}")
    print(f"   {signal.rationale}")
    print()

async def main():
    args = sys.argv[1:]
    
    agent = OptionsSignalsAgent()
    
    # If symbols provided, use those instead
    if args and not args[0].startswith("--"):
        agent.watchlist = args
    
    print_banner()
    print(f"Scanning: {', '.join(agent.watchlist)}\n")
    
    if "--live" in args:
        # Continuous mode
        await agent.run_continuous(interval_seconds=30)
    else:
        # Single scan
        print("Running scan...\n")
        signals = await agent.scan_for_signals()
        
        if not signals:
            print("No high-confidence signals found.")
            print("Try running with --live for continuous scanning.\n")
            return
        
        # Separate by type
        day_trades = [s for s in signals if s.duration == TradeDuration.DAY_TRADE]
        swings = [s for s in signals if s.duration == TradeDuration.SWING]
        
        if day_trades:
            print(f"⚡ DAY TRADE SIGNALS ({len(day_trades)} found)\n")
            for signal in day_trades[:3]:  # Top 3
                print_signal(signal)
        
        if swings:
            print(f"📈 SWING TRADE SIGNALS ({len(swings)} found)\n")
            for signal in swings[:3]:  # Top 3
                print_signal(signal)
        
        print("="*60)
        print(f"Total signals: {len(signals)}")
        print("Run with --live flag for continuous updates")
        print("="*60)

if __name__ == "__main__":
    asyncio.run(main())
