#!/usr/bin/env python3
"""MPT-Style Scanner V2 - Fixed data"""
import yfinance as yf

TICKERS = ["MPT", "NLY", "AGNC", "GME", "AMC", "NVAX", "MARA", "SOUN", "AI", "LCID", "BBAI", "PATH"]

def scan_ticker(ticker):
    """Scan with correct field names"""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        score = 0
        details = {}
        
        # Short ratio (days to cover)
        short_ratio = info.get("shortRatio", 0) or 0
        if short_ratio > 5:
            score += 20
            details["short_ratio"] = f"{short_ratio:.1f} days ✅"
        else:
            details["short_ratio"] = f"{short_ratio:.1f}"
        
        # Short % of float - might need different field
        # Try shares short / float
        # yfinance format is sometimes wrong
        
        # Volume ratio
        vol = info.get("volume", 0) or 0
        avg_vol = info.get("averageVolume", 1) or 1
        vol_ratio = vol / avg_vol if avg_vol else 0
        if vol_ratio >= 1.5:
            score += 15
            details["vol_ratio"] = f"{vol_ratio:.1f}x ✅"
        else:
            details["vol_ratio"] = f"{vol_ratio:.1f}x"
        
        # Price
        price = info.get("currentPrice", 0) or 0
        if 1 <= price <= 20:
            score += 10
            details["price"] = f"${price:.2f} ✅"
        else:
            details["price"] = f"${price:.2f}"
        
        # Market cap
        mcap = info.get("marketCap", 0) or 0
        if mcap < 5e9:  # Under $5B
            score += 5
            details["mcap"] = f"${mcap/1e9:.1f}B ✅"
        else:
            details["mcap"] = f"${mcap/1e9:.1f}B"
        
        return {"ticker": ticker, "score": score, "details": details, "price": price}
    except Exception as e:
        return {"ticker": ticker, "error": str(e)}

if __name__ == "__main__":
    print("=== MPT-STYLE SCANNER V2 ===\n")
    results = [scan_ticker(t) for t in TICKERS]
    results.sort(key=lambda x: x.get("score", 0), reverse=True)
    
    for r in results:
        print(f"{r['ticker']}: {r.get('score', 0)}/50")
        for k, v in r.get("details", {}).items():
            print(f"  {k}: {v}")
        print()
