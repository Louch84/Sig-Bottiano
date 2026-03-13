#!/usr/bin/env python3
"""Lottery Scanner - High risk, high reward penny stocks"""
import yfinance as yf

# Penny stocks with high volatility potential
TICKERS = ["BBBY", "BBIG", "TNA", "TNT", "UVXY", "SQQQ", "SOFI", "PLTR", "RIVN", "LCID", "NIO", "XPEV", "LI", "FSR"]

def scan_lottery(ticker):
    """Scan for lottery ticket setup"""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        score = 0
        details = {}
        
        # Price - must be penny
        price = info.get("currentPrice", 0) or 0
        if price < 5:
            score += 25
            details["price"] = f"${price:.2f} ✅ PENNY"
        elif price < 10:
            score += 15
            details["price"] = f"${price:.2f}"
        else:
            details["price"] = f"${price:.2f}"
        
        # Short interest
        short_ratio = info.get("shortRatio", 0) or 0
        if short_ratio > 5:
            score += 25
            details["short"] = f"{short_ratio:.1f} days ✅ SQUEEZE"
        elif short_ratio > 2:
            score += 10
            details["short"] = f"{short_ratio:.1f} days"
        else:
            details["short"] = f"{short_ratio:.1f}"
        
        # Volume spike
        vol = info.get("volume", 0) or 0
        avg_vol = info.get("averageVolume", 1) or 1
        vol_ratio = vol / avg_vol if avg_vol else 0
        if vol_ratio > 2:
            score += 25
            details["volume"] = f"{vol_ratio:.1f}x 🔥"
        elif vol_ratio > 1.5:
            score += 15
            details["volume"] = f"{vol_ratio:.1f}x"
        else:
            details["volume"] = f"{vol_ratio:.1f}x"
        
        # Market cap - smaller = more lottery
        mcap = info.get("marketCap", 0) or 0
        if mcap < 500e6:
            score += 15
            details["mcap"] = f"${mcap/1e6:.0f}M ✅ SMALL"
        else:
            details["mcap"] = f"${mcap/1e9:.1f}B"
        
        return {"ticker": ticker, "score": score, "details": details}
    except Exception as e:
        return {"ticker": ticker, "error": str(e)}

if __name__ == "__main__":
    print("=== LOTTERY SCANNER ===\n")
    results = [scan_lottery(t) for t in TICKERS]
    results.sort(key=lambda x: x.get("score", 0), reverse=True)
    
    for r in results[:5]:
        print(f"{r['ticker']}: {r.get('score', 0)}/90")
        for k, v in r.get("details", {}).items():
            print(f"  {k}: {v}")
        print()
