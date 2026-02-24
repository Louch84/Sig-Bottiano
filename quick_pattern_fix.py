#!/usr/bin/env python3
"""
Quick Low Conviction Pattern Fix
Test specific improvements without long backtests
"""

import sys
sys.path.insert(0, '/Users/sigbotti/.openclaw/workspace')
sys.path.insert(0, '/Users/sigbotti/.openclaw/workspace/agents/options-trading')

import yfinance as yf
import pandas as pd
import numpy as np

def quick_test_pattern(symbol: str, rvol_threshold: float = 0.5, hold_days: int = 3):
    """Quick single-symbol test"""
    ticker = yf.Ticker(symbol)
    df = ticker.history(period="1y")
    
    if len(df) < 30:
        return None
    
    signals = []
    
    for i in range(20, len(df) - hold_days):
        # Calculate metrics
        price_change = (df['Close'].iloc[i] - df['Close'].iloc[i-1]) / df['Close'].iloc[i-1] * 100
        avg_volume = df['Volume'].iloc[i-20:i].mean()
        rvol = df['Volume'].iloc[i] / avg_volume if avg_volume > 0 else 1
        sma20 = df['Close'].iloc[i-20:i].mean()
        high_20d = df['High'].iloc[i-20:i].max()
        distance_to_high = (high_20d - df['Close'].iloc[i]) / df['Close'].iloc[i] * 100
        
        # Check pattern
        if (price_change > 0.3 and 
            rvol < rvol_threshold and 
            df['Close'].iloc[i] > sma20 and
            distance_to_high < 5):
            
            # Simulate trade
            entry = df['Close'].iloc[i]
            exit_price = df['Close'].iloc[i + hold_days]
            ret = (exit_price - entry) / entry * 7  # 7x options leverage
            
            signals.append({
                'date': df.index[i].strftime('%Y-%m-%d'),
                'price_change': round(price_change, 2),
                'rvol': round(rvol, 2),
                'return': round(ret * 100, 2)
            })
    
    return signals

# Test different configurations
configs = [
    {'name': 'Original (RVOL<0.3, 5d)', 'rvol': 0.3, 'hold': 5},
    {'name': 'Relaxed (RVOL<0.5, 3d)', 'rvol': 0.5, 'hold': 3},
    {'name': 'More Relaxed (RVOL<0.7, 3d)', 'rvol': 0.7, 'hold': 3},
    {'name': 'Quick Exit (RVOL<0.5, 1d)', 'rvol': 0.5, 'hold': 1},
]

symbols = ['NOK', 'T', 'F', 'BAC']

print("="*70)
print("🔧 LOW CONVICTION PATTERN - QUICK FIX TEST")
print("="*70)
print()

for config in configs:
    print(f"\n📊 Testing: {config['name']}")
    print("-"*70)
    
    all_returns = []
    total_signals = 0
    
    for symbol in symbols:
        signals = quick_test_pattern(symbol, config['rvol'], config['hold'])
        if signals:
            returns = [s['return'] for s in signals]
            all_returns.extend(returns)
            total_signals += len(signals)
            wins = sum(1 for r in returns if r > 0)
            print(f"  {symbol}: {len(signals)} signals, {wins}/{len(signals)} wins, avg return {np.mean(returns):.1f}%")
    
    if all_returns:
        wins = sum(1 for r in all_returns if r > 0)
        win_rate = wins / len(all_returns) * 100
        avg_ret = np.mean(all_returns)
        
        print(f"\n  TOTAL: {total_signals} signals across {len(symbols)} symbols")
        print(f"  Win Rate: {win_rate:.1f}%")
        print(f"  Avg Return: {avg_ret:.1f}%")
        
        if win_rate > 50 and avg_ret > 0:
            print(f"  ✅ This config has EDGE")
        elif win_rate > 40:
            print(f"  ⚠️  Marginal edge")
        else:
            print(f"  ❌ No edge")
    else:
        print(f"  No signals found")

print()
print("="*70)
print("RECOMMENDATION:")
print("="*70)
print("Based on quick test, use the config with best win rate + return.")
print("Then update advanced_options_scanner.py with new thresholds.")
