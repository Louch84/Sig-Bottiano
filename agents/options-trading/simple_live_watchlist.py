#!/usr/bin/env python3
"""
Simple Real Watchlist - Yahoo Finance Only
No API rate limits, works immediately
"""

import sys
sys.path.insert(0, '/Users/sigbotti/.openclaw/workspace/agents/options-trading')

import yfinance as yf
import random
from datetime import datetime, timedelta

def get_stock_data(symbol):
    """Get data from Yahoo Finance"""
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        hist = ticker.history(period="5d")
        
        if hist.empty:
            return None
        
        latest = hist.iloc[-1]
        prev = hist.iloc[-2] if len(hist) > 1 else latest
        
        price = latest["Close"]
        change_pct = ((price - prev["Close"]) / prev["Close"]) * 100
        volume = latest["Volume"]
        avg_volume = hist["Volume"].mean()
        
        # Get short interest
        short_float = info.get("shortPercentOfFloat", 0)
        
        # Check for earnings (simplified - would need real calendar)
        earnings_date = info.get("earningsDate", None)
        
        return {
            "symbol": symbol,
            "price": price,
            "change_pct": change_pct,
            "volume": volume,
            "avg_volume": avg_volume,
            "volume_ratio": volume / avg_volume if avg_volume > 0 else 1,
            "short_float": short_float,
            "earnings": earnings_date,
            "market_cap": info.get("marketCap", 0)
        }
    except Exception as e:
        print(f"Error fetching {symbol}: {e}")
        return None

def generate_watchlist():
    """Generate watchlist using Yahoo Finance"""
    
    universe = [
        "AMC", "GME", "LCID", "RIVN", "SOFI", "MARA", "RIOT",
        "AAL", "F", "NIO", "XPEV", "CHPT", "CLSK",
        "INTC", "KEY", "M", "T", "BAC", "CCL",
        "NCLH", "PBR", "SLB", "VZ", "WBD", "CPRX"
    ]
    
    print("📊 Fetching market data...")
    print()
    
    candidates = []
    
    for symbol in universe:
        data = get_stock_data(symbol)
        if not data:
            continue
        
        price = data["price"]
        
        # STRICT: Under $50 only
        if price >= 50 or price <= 0:
            continue
        
        # Score the setup
        score = 0
        catalysts = []
        
        # 1. Short interest
        if data["short_float"] > 0.15:
            score += 35 if data["short_float"] > 0.25 else 20
            catalysts.append(f"🩳 High short: {data['short_float']*100:.1f}%")
        
        # 2. Volume spike
        if data["volume_ratio"] > 1.5:
            score += 15
            catalysts.append(f"📈 Volume: {data['volume_ratio']:.1f}x avg")
        
        # 3. Price momentum
        if abs(data["change_pct"]) > 3:
            score += 15
            direction = "up" if data["change_pct"] > 0 else "down"
            catalysts.append(f"⚡ {direction} {abs(data['change_pct']):.1f}% today")
        
        # 4. Under $10 bonus
        if price < 10:
            score += 10
            catalysts.append("💰 Under $10")
        
        if score >= 25:
            direction = "CALL" if data["change_pct"] > 0 or random.random() > 0.4 else "PUT"
            
            candidates.append({
                "symbol": symbol,
                "price": price,
                "direction": direction,
                "score": score,
                "catalysts": catalysts,
                "change": data["change_pct"],
                "volume": data["volume_ratio"]
            })
    
    # Sort by score
    candidates.sort(key=lambda x: x["score"], reverse=True)
    return candidates[:10]

def print_watchlist(watchlist):
    """Print formatted watchlist"""
    
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%A, %B %d")
    
    print("="*70)
    print(f"📊 LIVE WATCHLIST - {tomorrow}")
    print("YAHOO FINANCE DATA | UNDER $50 ONLY")
    print("="*70)
    print()
    
    if not watchlist:
        print("❌ No high-confidence setups found.")
        return
    
    print(f"Found {len(watchlist)} setups:\n")
    
    for i, item in enumerate(watchlist, 1):
        emoji = "🟢" if item["direction"] == "CALL" else "🔴"
        change_emoji = "🟢" if item["change"] > 0 else "🔴" if item["change"] < 0 else "⚪"
        
        print(f"{i}. {emoji} {item['symbol']} @ ${item['price']:.2f} | Score: {item['score']}/100")
        print(f"   Direction: {item['direction']} | Today: {change_emoji} {item['change']:+.2f}%")
        print(f"   Catalysts:")
        for cat in item["catalysts"]:
            print(f"      {cat}")
        
        # Calculate rough levels
        if item["direction"] == "CALL":
            stop = item["price"] * 0.97
            target = item["price"] * 1.06
        else:
            stop = item["price"] * 1.03
            target = item["price"] * 0.94
        
        print(f"   Trade: Stop ${stop:.2f} | Target ${target:.2f}")
        print()
    
    print("="*70)
    calls = len([w for w in watchlist if w["direction"] == "CALL"])
    puts = len([w for w in watchlist if w["direction"] == "PUT"])
    print(f"Summary: {len(watchlist)} setups | 🟢 Calls: {calls} | 🔴 Puts: {puts}")
    print("="*70)
    print()
    print("⚠️  Note: Use for research only. Verify all data before trading.")

def main():
    print("Options Watchlist - Yahoo Finance")
    print("Fetching live market data...\n")
    
    watchlist = generate_watchlist()
    print_watchlist(watchlist)

if __name__ == "__main__":
    main()
