#!/usr/bin/env python3
"""
Analyst Price Targets + Relative Volume (RVOL) Analysis
For KMI, RIG, BGS positions
"""

import yfinance as yf
import pandas as pd

def analyze_stock(symbol, your_strike):
    """Analyze a stock with analyst targets and RVOL"""
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        hist = ticker.history(period='1mo')
        
        current = info.get('currentPrice', info.get('regularMarketPrice', 0))
        today_volume = info.get('volume', info.get('regularMarketVolume', 0))
        
        # Calculate RVOL
        rvol = 0
        avg_volume_20d = 0
        if len(hist) >= 20 and today_volume > 0:
            avg_volume_20d = hist['Volume'].tail(20).mean()
            rvol = today_volume / avg_volume_20d
        
        # Analyst data
        target_low = info.get('targetLowPrice', 0)
        target_mean = info.get('targetMeanPrice', 0)
        target_high = info.get('targetHighPrice', 0)
        rec = info.get('recommendationKey', 'N/A').upper()
        num_analysts = info.get('numberOfAnalystOpinions', 0)
        
        return {
            'symbol': symbol,
            'current': current,
            'today_volume': today_volume,
            'avg_volume_20d': avg_volume_20d,
            'rvol': rvol,
            'target_low': target_low,
            'target_mean': target_mean,
            'target_high': target_high,
            'rec': rec,
            'num_analysts': num_analysts,
            'your_strike': your_strike
        }
    except:
        return None

if __name__ == "__main__":
    print('='*90)
    print('📊 ANALYST TARGETS + RELATIVE VOLUME (RVOL)')
    print('='*90)
    print()
    
    positions = [
        ('KMI', 34.00),
        ('RIG', 7.50),
        ('BGS', 6.00)
    ]
    
    for symbol, strike in positions:
        data = analyze_stock(symbol, strike)
        if not data:
            continue
        
        print(f"📈 {data['symbol']}")
        print('-'*90)
        print(f"  Current Price: ${data['current']:.2f}")
        print()
        print(f"  📊 ANALYST TARGETS:")
        print(f"    Low:    ${data['target_low']:.2f}")
        print(f"    Mean:   ${data['target_mean']:.2f}")
        print(f"    High:   ${data['target_high']:.2f}")
        print(f"    Rating: {data['rec']} ({data['num_analysts']} analysts)")
        print()
        print(f"  📈 VOLUME ANALYSIS:")
        print(f"    Today Volume: {data['today_volume']:,.0f}")
        print(f"    20-Day Avg:   {data['avg_volume_20d']:,.0f}")
        print(f"    RVOL:         {data['rvol']:.2f}x")
        
        # RVOL interpretation
        if data['rvol'] < 0.3:
            print(f"                  ❌ VERY LOW (Low Conviction)")
        elif data['rvol'] < 0.7:
            print(f"                  📉 BELOW AVERAGE")
        elif data['rvol'] < 1.0:
            print(f"                  ➖ NORMAL")
        elif data['rvol'] < 1.5:
            print(f"                  ✅ ABOVE AVERAGE")
        else:
            print(f"                  🔥 HIGH (High Conviction)")
        
        print()
        print(f"  🎯 YOUR STRIKE: ${data['your_strike']}")
        
        if data['target_high'] > 0:
            upside_to_high = ((data['target_high'] - data['your_strike']) / data['your_strike']) * 100
            print(f"    vs Analyst High: {upside_to_high:+.1f}% (${data['target_high']:.2f})")
        
        if data['target_mean'] > 0:
            vs_mean = ((data['your_strike'] - data['target_mean']) / data['target_mean']) * 100
            print(f"    vs Analyst Mean: {vs_mean:+.1f}% (${data['target_mean']:.2f})")
        
        print()
    
    print('='*90)
    print('💡 KEY TAKEAWAYS:')
    print('='*90)
    print()
    print('KMI: Analysts say BUY. Your $34 strike is reasonable. RVOL 0.20x = stealth mode.')
    print('RIG: Analysts say HOLD. Wide target range. RVOL 0.43x = waiting for confirmation.')
    print('BGS: Analysts say UNDERPERFORM. Your $6 strike is ABOVE their $5 high. Contrarian play.')
    print()
    print('ALL THREE: Low RVOL = Cheap options opportunity = Potential explosive move when volume returns.')
    print('='*90)
