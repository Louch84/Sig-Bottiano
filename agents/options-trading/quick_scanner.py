#!/usr/bin/env python3
"""
Quick Scanner - Ultra-Fast, Low-Cost Mode
For when you need signals NOW with minimal cost
"""

import sys
sys.path.insert(0, '/Users/sigbotti/.openclaw/workspace/agents/options-trading')

import asyncio
import yfinance as yf
from datetime import datetime

class QuickScanner:
    """Minimal scanner - 5 stocks, basic signals only"""
    
    def __init__(self):
        self.watchlist = ["AMC", "GME", "MARA", "SOFI", "TSLA"]
    
    async def scan(self):
        """Ultra-fast scan"""
        print("⚡ QUICK SCAN MODE")
        print("5 stocks | Basic signals | 5-10 seconds")
        print()
        
        signals = []
        
        for symbol in self.watchlist:
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.info
                hist = ticker.history(period="5d")
                
                if hist.empty:
                    continue
                
                price = hist['Close'].iloc[-1]
                
                # Skip if over $50
                if price >= 50:
                    continue
                
                # Quick metrics
                change = ((price - hist['Close'].iloc[-2]) / hist['Close'].iloc[-2]) * 100
                volume_ratio = hist['Volume'].iloc[-1] / hist['Volume'].mean()
                short_pct = info.get('shortPercentOfFloat', 0) * 100
                
                # Simple scoring
                score = 0
                direction = "CALL" if change > 0 else "PUT"
                
                if short_pct > 20:
                    score += 30
                if volume_ratio > 2:
                    score += 20
                if abs(change) > 3:
                    score += 20
                
                if score >= 30:
                    signals.append({
                        'symbol': symbol,
                        'price': price,
                        'direction': direction,
                        'score': score,
                        'change': change,
                        'short': short_pct,
                        'volume': volume_ratio
                    })
                    
            except Exception as e:
                continue
        
        # Sort by score
        signals.sort(key=lambda x: x['score'], reverse=True)
        return signals
    
    def print_signals(self, signals):
        """Minimal output"""
        if not signals:
            print("No signals")
            return
        
        print(f"Found {len(signals)} signals:\n")
        
        for s in signals:
            emoji = "🟢" if s['direction'] == "CALL" else "🔴"
            print(f"{emoji} {s['symbol']} {s['direction']} @ ${s['price']:.2f}")
            print(f"   Score: {s['score']} | Change: {s['change']:+.1f}%")
            print(f"   Short: {s['short']:.0f}% | Vol: {s['volume']:.1f}x")
            print()

async def main():
    scanner = QuickScanner()
    signals = await scanner.scan()
    scanner.print_signals(signals)

if __name__ == "__main__":
    asyncio.run(main())
