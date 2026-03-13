#!/usr/bin/env python3
"""Short Squeeze Scanner"""
import yfinance as yf
import pandas as pd

TICKERS = ['MPT', 'LCID', 'MARA', 'SOUN', 'AI', 'NVAX', 'GME', 'AMC', 'BBBY', 'BBIG']

def check_squeeze(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        price = info.get('currentPrice', 0)
        vol = info.get('volume', 0)
        avg_vol = info.get('averageVolume', 1)
        
        if not price or not vol:
            return None
            
        vol_ratio = vol / avg_vol if avg_vol else 0
        
        # Simple squeeze score
        score = 0
        if vol_ratio > 1.5: score += 30
        if price < 20: score += 20
        if info.get('shortRatio', 0) > 5: score += 30
        if info.get('shortPercentOfFloat', 0) > 10: score += 20
        
        return {
            'ticker': ticker,
            'price': price,
            'vol_ratio': vol_ratio,
            'score': score
        }
    except:
        return None

print("=== SHORT SQUEEZE SCANNER ===")
results = []
for t in TICKERS:
    r = check_squeeze(t)
    if r:
        results.append(r)
        print(f"{r['ticker']}: ${r['price']} | {r['vol_ratio']:.1f}x vol | Score: {r['score']}")

# Sort by score
results.sort(key=lambda x: x['score'], reverse=True)
print("\n=== TOP PICKS ===")
for r in results[:3]:
    print(f"  {r['ticker']}: {r['score']}/100")
