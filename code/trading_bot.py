#!/usr/bin/env python3
"""Trading Bot - Auto-scan and alert"""
import yfinance as yf
import time
from datetime import datetime

TICKERS = ['MPT', 'LCID', 'MARA', 'SOUN', 'AI', 'NVAX', 'GME', 'AMC', 'BBBY', 'BBIG']

def scan():
    """Scan for squeeze setups"""
    results = []
    
    for ticker in TICKERS:
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            price = info.get('currentPrice', 0)
            vol = info.get('volume', 0)
            avg_vol = info.get('averageVolume', 1)
            
            if not price or not vol:
                continue
            
            vol_ratio = vol / avg_vol if avg_vol else 0
            
            # Score
            score = 0
            if vol_ratio > 1.5: score += 30
            if price < 20: score += 20
            if info.get('shortRatio', 0) > 5: score += 30
            if info.get('shortPercentOfFloat', 0) > 10: score += 20
            
            if score >= 50:
                results.append({
                    'ticker': ticker,
                    'price': price,
                    'vol': vol_ratio,
                    'score': score
                })
        except:
            continue
    
    # Sort by score
    results.sort(key=lambda x: x['score'], reverse=True)
    return results

def alert(results):
    """Send alert if high score"""
    if results and results[0]['score'] >= 70:
        return f"🔥 ALERT: {results[0]['ticker']} - Score: {results[0]['score']}/100"
    return None

# Run scan
if __name__ == "__main__":
    print(f"=== SCAN {datetime.now().strftime('%H:%M')} ===")
    results = scan()
    for r in results[:3]:
        print(f"{r['ticker']}: ${r['price']} | {r['vol']:.1f}x | Score: {r['score']}")
    
    a = alert(results)
    if a:
        print(f"\n{a}")
