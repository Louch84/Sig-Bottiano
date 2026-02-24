#!/usr/bin/env python3
"""
Scheduled Scanner - Run scans at market times with auto-alerts
"""

import sys
sys.path.insert(0, '/Users/sigbotti/.openclaw/workspace')
sys.path.insert(0, '/Users/sigbotti/.openclaw/workspace/agents/options-trading')

from scanner_alert_integration import ScannerAlertBridge
from datetime import datetime, time
import argparse

def is_market_hours() -> bool:
    """Check if US stock market is open"""
    now = datetime.now()
    
    # Check if weekday (Mon-Fri)
    if now.weekday() >= 5:  # 5=Saturday, 6=Sunday
        return False
    
    # Market hours: 9:30 AM - 4:00 PM EST
    market_open = time(9, 30)
    market_close = time(16, 0)
    current_time = now.time()
    
    return market_open <= current_time <= market_close

def run_premarket_scan():
    """Run pre-market scan (9:00 AM)"""
    print("="*70)
    print(f"🌅 PRE-MARKET SCAN - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("="*70)
    print()
    
    bridge = ScannerAlertBridge()
    bridge.min_conviction_for_alert = 70  # Slightly lower for early signals
    
    # Focus on momentum and catalyst plays pre-market
    watchlist = [
        'AMC', 'GME', 'BB', 'RIVN', 'LCID', 'SOFI', 'PLTR',  # Meme/growth
        'T', 'BAC', 'KMI', 'XOM', 'OXY',  # Dividend/energy
        'UBER', 'AAL', 'CCL', 'NCLH'  # Travel/leisure
    ]
    
    signals = bridge.scan_and_alert(watchlist)
    
    return signals

def run_midday_scan():
    """Run midday scan (12:00 PM)"""
    print("="*70)
    print(f"☀️  MIDDAY SCAN - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("="*70)
    print()
    
    bridge = ScannerAlertBridge()
    
    # Broader scan midday
    watchlist = [
        'AMC', 'GME', 'RIVN', 'LCID', 'SOFI', 'PLTR', 'NOK', 'F',
        'BAC', 'T', 'KMI', 'XOM', 'OXY', 'MPC', 'VLO',
        'UBER', 'AAL', 'CCL', 'NCLH'
    ]
    
    signals = bridge.scan_and_alert(watchlist)
    
    return signals

def run_power_hour_scan():
    """Run power hour scan (3:00 PM)"""
    print("="*70)
    print(f"⚡ POWER HOUR SCAN - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("="*70)
    print()
    
    bridge = ScannerAlertBridge()
    bridge.min_conviction_for_alert = 80  # Higher threshold for EOD
    
    # Focus on 0DTE and momentum
    watchlist = [
        'SPY', 'QQQ', 'IWM',  # Indices for 0DTE
        'AMC', 'GME', 'RIVN', 'SOFI',  # High momentum
        'TSLA', 'AAPL', 'NVDA'  # Large cap momentum
    ]
    
    signals = bridge.scan_and_alert(watchlist)
    
    return signals

def run_quick_scan(symbols: list = None):
    """Run quick scan on specific symbols"""
    if symbols is None:
        symbols = ['NOK', 'KMI', 'T', 'BAC', 'SOFI']
    
    print("="*70)
    print(f"⚡ QUICK SCAN - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("="*70)
    print(f"Symbols: {', '.join(symbols)}")
    print()
    
    bridge = ScannerAlertBridge()
    signals = bridge.scan_and_alert(symbols)
    
    return signals

def main():
    parser = argparse.ArgumentParser(description='Scheduled Options Scanner')
    parser.add_argument('--time', choices=['premarket', 'midday', 'powerhour', 'quick'],
                       default='quick', help='When to run the scan')
    parser.add_argument('--symbols', nargs='+', help='Specific symbols to scan')
    parser.add_argument('--force', action='store_true', help='Run even if market closed')
    
    args = parser.parse_args()
    
    # Check market hours unless forced
    if not args.force and not is_market_hours():
        print("⚠️  Market is currently closed")
        print("Use --force to run anyway")
        return
    
    # Run appropriate scan
    if args.time == 'premarket':
        signals = run_premarket_scan()
    elif args.time == 'midday':
        signals = run_midday_scan()
    elif args.time == 'powerhour':
        signals = run_power_hour_scan()
    else:
        signals = run_quick_scan(args.symbols)
    
    # Summary
    print(f"\n✅ Scan complete. {len(signals)} signals analyzed.")
    print(f"High conviction alerts sent for signals 75%+ confidence")

if __name__ == "__main__":
    main()
