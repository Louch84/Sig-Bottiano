#!/usr/bin/env python3
"""
Quick options chain fetcher demo
"""

import yfinance as yf
import sys

symbol = sys.argv[1] if len(sys.argv) > 1 else 'AMC'

try:
    ticker = yf.Ticker(symbol)
    expirations = ticker.options
    
    if not expirations:
        print(f"No options data available for {symbol}")
        sys.exit(1)
    
    # Get 0DTE or nearest expiration
    chain = ticker.option_chain(expirations[0])
    
    print(f"{symbol} Options Chain for {expirations[0]}")
    print("="*60)
    print()
    
    # Get current stock price
    info = ticker.info
    current = info.get('currentPrice', info.get('regularMarketPrice', 0))
    print(f"Stock Price: ${current:.2f}")
    print()
    
    calls = chain.calls
    puts = chain.puts
    
    # Find ATM options
    atm_calls = calls[(calls['strike'] >= current * 0.95) & (calls['strike'] <= current * 1.15)].head(5)
    atm_puts = puts[(puts['strike'] >= current * 0.85) & (puts['strike'] <= current * 1.05)].head(5)
    
    print("CALLS (Near ATM):")
    print(f"{'Strike':<10} {'Last':<8} {'Bid':<8} {'Ask':<8} {'IV%':<8} {'Vol':<8}")
    print("-"*60)
    for idx, row in atm_calls.iterrows():
        last = row['lastPrice'] if row['lastPrice'] > 0 else (row['bid'] + row['ask']) / 2 if row['bid'] > 0 else 0
        print(f"${row['strike']:<9.2f} {last:<8.2f} {row['bid']:<8.2f} {row['ask']:<8.2f} {row['impliedVolatility']*100:<7.1f}% {row['volume']:<8.0f}")
    
    print()
    print("PUTS (Near ATM):")
    print(f"{'Strike':<10} {'Last':<8} {'Bid':<8} {'Ask':<8} {'IV%':<8} {'Vol':<8}")
    print("-"*60)
    for idx, row in atm_puts.iterrows():
        last = row['lastPrice'] if row['lastPrice'] > 0 else (row['bid'] + row['ask']) / 2 if row['bid'] > 0 else 0
        print(f"${row['strike']:<9.2f} {last:<8.2f} {row['bid']:<8.2f} {row['ask']:<8.2f} {row['impliedVolatility']*100:<7.1f}% {row['volume']:<8.0f}")
    
    print()
    print("="*60)
    
    # Calculate put/call ratio
    total_call_vol = calls['volume'].sum()
    total_put_vol = puts['volume'].sum()
    if total_call_vol > 0:
        pc_ratio = total_put_vol / total_call_vol
        print(f"Put/Call Volume Ratio: {pc_ratio:.2f}")
        if pc_ratio < 0.7:
            print("  Sentiment: Bullish (more call volume)")
        elif pc_ratio > 1.3:
            print("  Sentiment: Bearish (more put volume)")
        else:
            print("  Sentiment: Neutral")
    
    print()
    print(f"Total Call Volume: {int(total_call_vol):,}")
    print(f"Total Put Volume: {int(total_put_vol):,}")
    print(f"Open Interest - Calls: {int(calls['openInterest'].sum()):,}")
    print(f"Open Interest - Puts: {int(puts['openInterest'].sum()):,}")

except Exception as e:
    print(f"Error: {e}")
