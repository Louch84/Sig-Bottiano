#!/usr/bin/env python3
"""MPT Scanner V2 - Better data sources"""
import yfinance as yf

def get_short_data(ticker):
    """Get short data from yfinance"""
    stock = yf.Ticker(ticker)
    info = stock.info
    
    # yfinance sometimes has these
    short_data = {
        "short_ratio": info.get("shortRatio"),
        "short_percent_float": info.get("shortPercentOfFloat"),
        "short_percent_shares": info.get("shortPercentOfSharesOutstanding"),
        "days_to_cover": info.get("daysToCover"),
    }
    return short_data

# Test with MPT
print("MPT short data:")
import json
print(json.dumps(get_short_data("MPT"), indent=2))
