#!/usr/bin/env python3
"""Stock Analyzer - Quick Analysis Tool"""
import yfinance as yf
import pandas as pd
import sys

def analyze(ticker):
    stock = yf.Ticker(ticker)
    info = stock.info
    
    print(f"=== {ticker} ANALYSIS ===")
    print(f"Price: ${info.get('currentPrice', 'N/A')}")
    print(f"Volume: {info.get('volume', 'N/A'):,}")
    print(f"Avg Volume: {info.get('averageVolume', 'N/A'):,}")
    print(f"Market Cap: ${info.get('marketCap', 'N/A'):,}")
    print(f"P/E: {info.get('trailingPE', 'N/A')}")
    print(f"52W High: ${info.get('fiftyTwoWeekHigh', 'N/A')}")
    print(f"52W Low: ${info.get('fiftyTwoWeekLow', 'N/A')}")
    
    # Squeeze indicators
    vol = info.get('volume', 0)
    avg_vol = info.get('averageVolume', 1)
    if vol and avg_vol:
        vol_ratio = vol / avg_vol
        print(f"Volume Ratio: {vol_ratio:.2f}x")
        if vol_ratio > 1.5:
            print("⚠️ HIGH VOLUME ALERT")
    
    return info

if __name__ == "__main__":
    t = sys.argv[1].upper() if len(sys.argv) > 1 else "MPT"
    analyze(t)
