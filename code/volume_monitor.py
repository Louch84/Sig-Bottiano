#!/usr/bin/env python3
"""
Volume Monitor - Alerts when squeeze candidates hit 1.5x volume
Run continuously during market hours
"""

import yfinance as yf
import time
import requests
from datetime import datetime

DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1473406205081817260/PaNG9cz9NWMpXWXPjKnS6k2qKB8q3WNLkZ8rVhqYvXqNKqLkZ8rVhqYvXqNK"

TICKERS = ['LCID', 'MARA', 'SOUN', 'AI', 'NVAX', 'PATH', 'BBAI', 'GME', 'AMC']
CHECK_INTERVAL = 300  # 5 minutes

def send_alert(msg):
    try:
        requests.post(DISCORD_WEBHOOK, json={"content": msg}, timeout=10)
    except:
        pass

def check_volume():
    alerts = []
    
    for t in TICKERS:
        try:
            s = yf.Ticker(t)
            i = s.info
            
            p = i.get('currentPrice', 0) or i.get('regularMarketPrice', 0)
            if not p or not (1 <= p <= 50):
                continue
            
            sp = (i.get('shortPercentOfFloat', 0) or 0) * 100
            v = i.get('volume', 0) or 0
            av = i.get('averageVolume', 0) or 1
            vr = v / av if av > 0 else 0
            
            # Alert if high short + volume spike
            if sp > 20 and vr >= 1.5:
                alerts.append(f"${t}: ${p} | Short: {sp:.1f}% | Vol: {vr:.1f}x 🚨")
                
        except:
            pass
    
    return alerts

def run_monitor():
    print(f"Volume monitor started at {datetime.now()}")
    
    while True:
        alerts = check_volume()
        
        if alerts:
            msg = "🚨 **VOLUME SPIKE DETECTED**\n\n" + "\n".join(alerts)
            send_alert(msg)
            print(f"ALERT: {alerts}")
        
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    run_monitor()
