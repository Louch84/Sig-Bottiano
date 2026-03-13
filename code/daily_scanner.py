#!/usr/bin/env python3
"""
Daily Squeeze Scanner - Runs at 9:20 AM weekdays
"""

import yfinance as yf
import pandas as pd
from datetime import datetime
import os
import requests

LOG_FILE = "/Users/sigbotti/.openclaw/workspace/logs/scanner.log"
RESULTS_DIR = "/Users/sigbotti/.openclaw/workspace/trading/results"

# Discord webhook - this channel
DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1473406205081817260/PaNG9cz9NWMpXWXPjKnS6k2qKB8q3WNLkZ8rVhqYvXqNK"

def send_discord(message):
    """Send message to Discord"""
    try:
        data = {"content": message}
        requests.post(DISCORD_WEBHOOK, json=data, timeout=10)
    except:
        pass

def log(msg):
    with open(LOG_FILE, "a") as f:
        f.write(f"[{datetime.now()}] {msg}\n")
    print(msg)

def scan_stocks():
    # Test tickers
    tickers = ['PATH', 'U', 'DOCU', 'NET', 'SQ', 'COIN', 'HOOD', 'SNAP', 'PINS', 'PLTR',
                'SMCI', 'RKLB', 'DM', 'GTLB', 'CAN', 'NVAX', 'MRNA', 'ATER', 'GME', 'AMC',
                'SOFI', 'RIVN', 'LCID', 'MARA', 'SOUN', 'AI', 'BBAI', 'LUNR', 'OPRA']
    
    results = []
    
    for t in tickers:
        try:
            stock = yf.Ticker(t)
            info = stock.info
            price = info.get('currentPrice', 0) or info.get('regularMarketPrice', 0)
            
            if not price or not (0.5 <= price <= 50):
                continue
            
            short_pct = (info.get('shortPercentOfFloat', 0) or 0) * 100
            float_shares = info.get('floatShares', 0) or 0
            volume = info.get('volume', 0) or 0
            avg_vol = info.get('averageVolume', 0) or 1
            
            vol_ratio = volume / avg_vol if avg_vol > 0 else 0
            
            score = 0
            if short_pct > 20: score += 25
            elif short_pct > 15: score += 20
            
            if float_shares < 50_000_000: score += 15
            elif float_shares < 100_000_000: score += 10
            
            if vol_ratio > 1.5: score += 15
            elif vol_ratio > 1.2: score += 10
            
            if price < 15: score += 5
            
            if short_pct > 15 and vol_ratio > 1.5:
                results.append({
                    'ticker': t,
                    'price': round(price, 2),
                    'short_pct': round(short_pct, 1),
                    'float_m': round(float_shares/1e6, 1),
                    'vol_ratio': round(vol_ratio, 1),
                    'score': score
                })
        except:
            continue
    
    results.sort(key=lambda x: (x['short_pct'], x['vol_ratio']), reverse=True)
    
    return results[:10]

if __name__ == "__main__":
    log("Starting daily squeeze scan...")
    
    results = scan_stocks()
    
    if results:
        log(f"Found {len(results)} candidates")
        
        # Save to CSV
        os.makedirs(RESULTS_DIR, exist_ok=True)
        df = pd.DataFrame(results)
        filename = f"{RESULTS_DIR}/squeeze_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
        df.to_csv(filename, index=False)
        
        # Send to Discord
        msg = "📈 **TOP SQUEEZE CANDIDATES**\n\n"
        for r in results[:5]:
            msg += f"**{r['ticker']}** - ${r['price']}\n"
            msg += f"   Short: {r['short_pct']}% | Vol: {r['vol_ratio']}x\n\n"
        
        send_discord(msg)
        
        log("TOP RESULTS:")
        for r in results[:5]:
            log(f"  {r['ticker']}: ${r['price']} | Short: {r['short_pct']}% | Vol: {r['vol_ratio']}x | Score: {r['score']}")
    else:
        msg = "📊 No squeeze setups found today"
        send_discord(msg)
        log("No setups found")
    
    log("Scan complete")
