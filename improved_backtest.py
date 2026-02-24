#!/usr/bin/env python3
"""
Improved Pattern Backtester - Updated Thresholds
"""

import sys
sys.path.insert(0, '/Users/sigbotti/.openclaw/workspace')
sys.path.insert(0, '/Users/sigbotti/.openclaw/workspace/agents/options-trading')

import yfinance as yf
import pandas as pd
import numpy as np
from typing import Dict, List

def improved_backtest(symbol: str, period: str = "1y") -> Dict:
    """
    Backtest with IMPROVED thresholds:
    - RVOL < 0.6 (was 0.3)
    - Price change > 0.3% (was 0.5%)
    - Price change < 3% (don't chase)
    - Near highs < 5% (was 3%)
    - Hold 2-3 days (was 5)
    """
    ticker = yf.Ticker(symbol)
    df = ticker.history(period=period)
    
    if len(df) < 30:
        return {'error': 'insufficient_data'}
    
    trades = []
    
    for i in range(20, len(df) - 5):
        # Calculate metrics
        price_change = (df['Close'].iloc[i] - df['Close'].iloc[i-1]) / df['Close'].iloc[i-1] * 100
        avg_volume = df['Volume'].iloc[i-20:i].mean()
        rvol = df['Volume'].iloc[i] / avg_volume if avg_volume > 0 else 1
        sma20 = df['Close'].iloc[i-20:i].mean()
        high_20d = df['High'].iloc[i-20:i].max()
        distance_to_high = (high_20d - df['Close'].iloc[i]) / df['Close'].iloc[i] * 100
        
        # IMPROVED CRITERIA (5 checks, need 4)
        checks = {
            'price_up': price_change > 0.3,
            'not_extended': price_change < 3.0,
            'low_volume': rvol < 0.6,
            'above_sma20': df['Close'].iloc[i] > sma20,
            'near_highs': distance_to_high < 5.0
        }
        
        if sum(checks.values()) >= 4:
            # Pattern found - simulate entry
            entry_price = df['Close'].iloc[i]
            entry_date = df.index[i]
            
            # Hold for 3 days OR exit on volume spike
            exit_price = None
            exit_date = None
            exit_reason = None
            
            for j in range(1, 4):  # Max 3 day hold
                if i + j >= len(df):
                    break
                    
                current_close = df['Close'].iloc[i + j]
                current_volume = df['Volume'].iloc[i + j]
                
                # Exit on volume spike (>2x average)
                if current_volume > avg_volume * 2:
                    exit_price = current_close
                    exit_date = df.index[i + j]
                    exit_reason = 'volume_spike'
                    break
                
                # Exit on SMA break
                if current_close < sma20:
                    exit_price = current_close
                    exit_date = df.index[i + j]
                    exit_reason = 'sma_break'
                    break
            
            # Time-based exit
            if exit_price is None:
                exit_price = df['Close'].iloc[i + 3]
                exit_date = df.index[i + 3]
                exit_reason = 'time_stop'
            
            # Calculate returns
            stock_return = (exit_price - entry_price) / entry_price
            option_return = stock_return * 7  # 7x leverage estimate
            
            trades.append({
                'entry_date': entry_date,
                'exit_date': exit_date,
                'entry_price': entry_price,
                'exit_price': exit_price,
                'stock_return': stock_return * 100,
                'option_return': option_return * 100,
                'exit_reason': exit_reason,
                'hold_days': (exit_date - entry_date).days,
                'rvol': round(rvol, 2),
                'price_change': round(price_change, 2)
            })
    
    if not trades:
        return {'symbol': symbol, 'trades': 0}
    
    returns = [t['option_return'] for t in trades]
    winning = [r for r in returns if r > 0]
    
    return {
        'symbol': symbol,
        'trades': len(trades),
        'win_rate': round(len(winning) / len(returns) * 100, 1),
        'avg_return': round(np.mean(returns), 2),
        'best_trade': round(max(returns), 1),
        'worst_trade': round(min(returns), 1),
        'profit_factor': round(abs(sum(winning)) / abs(sum(r for r in returns if r < 0)), 2) if any(r < 0 for r in returns) else float('inf'),
        'avg_hold_days': round(np.mean([t['hold_days'] for t in trades]), 1),
        'exit_reasons': {
            'volume_spike': sum(1 for t in trades if t['exit_reason'] == 'volume_spike'),
            'sma_break': sum(1 for t in trades if t['exit_reason'] == 'sma_break'),
            'time_stop': sum(1 for t in trades if t['exit_reason'] == 'time_stop')
        },
        'sample_trades': trades[:3]  # First 3 for inspection
    }


def main():
    print("="*70)
    print("📊 IMPROVED LOW CONVICTION PATTERN - BACKTEST")
    print("="*70)
    print()
    print("NEW THRESHOLDS:")
    print("  RVOL < 0.6 (was 0.3) - More signals")
    print("  Price change > 0.3% (was 0.5%) - More entries")
    print("  Price change < 3% - Don't chase extended moves")
    print("  Near highs < 5% (was 3%) - More opportunities")
    print("  Need 4 of 5 criteria (was 3 of 4)")
    print("  Hold 2-3 days OR exit on volume spike")
    print()
    
    symbols = ['NOK', 'T', 'F', 'BAC', 'KMI', 'SOFI']
    
    all_results = []
    
    for symbol in symbols:
        try:
            print(f"Testing {symbol}...", end=' ')
            result = improved_backtest(symbol)
            
            if 'trades' in result and result['trades'] > 0:
                print(f"✅ {result['trades']} trades, {result['win_rate']}% win rate")
                all_results.append(result)
            else:
                print(f"⚠️  No signals")
                
        except Exception as e:
            print(f"❌ Error: {str(e)[:40]}")
            continue
    
    if all_results:
        print()
        print("="*70)
        print("SUMMARY ACROSS ALL SYMBOLS")
        print("="*70)
        
        total_trades = sum(r['trades'] for r in all_results)
        avg_win_rate = np.mean([r['win_rate'] for r in all_results])
        avg_return = np.mean([r['avg_return'] for r in all_results])
        
        print(f"Total Signals: {total_trades}")
        print(f"Avg Win Rate: {avg_win_rate:.1f}%")
        print(f"Avg Return: {avg_return:.1f}%")
        print(f"Symbols with edge: {sum(1 for r in all_results if r['win_rate'] > 50)}/{len(all_results)}")
        
        print()
        print("="*70)
        for r in all_results:
            status = "✅" if r['win_rate'] > 50 else "⚠️" if r['win_rate'] > 40 else "❌"
            print(f"{status} {r['symbol']}: {r['win_rate']}% win rate ({r['trades']} trades)")
        print("="*70)
        
        if avg_win_rate > 50:
            print("\n🎉 PATTERN HAS EDGE - Ready to trade!")
        elif avg_win_rate > 40:
            print("\n⚠️  MARGINAL EDGE - Trade smaller size")
        else:
            print("\n❌ NEEDS MORE WORK")
    else:
        print("\nNo results to analyze")


if __name__ == "__main__":
    main()
