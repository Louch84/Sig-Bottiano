#!/usr/bin/env python3
"""
Breakout Entry Alert System
Alerts ONLY when breakout is confirmed (price + volume spike)
Never alerts on setup - only on ENTRY SIGNAL
"""

import sys
sys.path.insert(0, '/Users/sigbotti/.openclaw/workspace')
sys.path.insert(0, '/Users/sigbotti/.openclaw/workspace/agents/options-trading')

import yfinance as yf
import pandas as pd
import time
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class BreakoutSignal:
    symbol: str
    entry_price: float
    resistance_broken: float
    volume_spike: float
    rvol: float
    suggested_strike: float
    option_cost: float
    confidence: str  # STRONG, GOOD, WEAK
    urgency: str  # NOW, SOON, WATCH

class BreakoutEntryAlerts:
    """
    Only alerts when breakout is CONFIRMED
    Criteria:
    1. Price breaks above resistance (+0.5% or more)
    2. Volume spikes to 2x+ average
    3. Both happen together
    """
    
    def __init__(self):
        self.min_volume_spike = 2.0  # 2x average volume
        self.min_price_break = 0.5   # 0.5% above resistance
        self.alerts_sent = []
        
    def check_breakout(self, symbol: str) -> Optional[BreakoutSignal]:
        """
        Check if stock is having a CONFIRMED breakout right now
        Returns signal if YES, None if NO
        """
        try:
            ticker = yf.Ticker(symbol)
            
            # Get intraday data (today's action)
            df = ticker.history(period='1d', interval='5m')
            daily = ticker.history(period='5d')
            info = ticker.info
            
            if len(df) < 10 or len(daily) < 5:
                return None
            
            current_price = info.get('currentPrice', df['Close'].iloc[-1])
            
            # Find resistance (20-day high)
            resistance = daily['High'].tail(20).max()
            
            # Check if price broke resistance
            price_break_pct = ((current_price - resistance) / resistance) * 100
            
            if price_break_pct < self.min_price_break:
                return None  # Price hasn't broken out enough
            
            # Check volume
            avg_volume_20d = daily['Volume'].tail(20).mean()
            today_volume = daily['Volume'].iloc[-1]
            rvol = today_volume / avg_volume_20d if avg_volume_20d > 0 else 1
            
            if rvol < self.min_volume_spike:
                return None  # Volume hasn't spiked enough
            
            # Get option data
            expirations = ticker.options
            if not expirations:
                return None
            
            # Find nearest expiration
            nearest_exp = expirations[0]
            chain = ticker.option_chain(nearest_exp)
            calls = chain.calls
            
            # Find strike just above current price
            otm_calls = calls[calls['strike'] > current_price]
            if otm_calls.empty:
                return None
            
            best_option = otm_calls.nsmallest(1, 'strike').iloc[0]
            
            # Determine confidence
            if price_break_pct > 2.0 and rvol > 3.0:
                confidence = "STRONG"
                urgency = "NOW"
            elif price_break_pct > 1.0 and rvol > 2.5:
                confidence = "GOOD"
                urgency = "NOW"
            else:
                confidence = "WEAK"
                urgency = "SOON"
            
            return BreakoutSignal(
                symbol=symbol,
                entry_price=current_price,
                resistance_broken=resistance,
                volume_spike=today_volume,
                rvol=rvol,
                suggested_strike=best_option['strike'],
                option_cost=best_option['lastPrice'],
                confidence=confidence,
                urgency=urgency
            )
            
        except Exception as e:
            return None
    
    def scan_for_breakouts(self, symbols: List[str]) -> List[BreakoutSignal]:
        """
        Scan multiple stocks for confirmed breakouts
        """
        breakouts = []
        
        print(f"🔍 Scanning {len(symbols)} stocks for CONFIRMED BREAKOUTS...")
        print(f"   Criteria: Price +{self.min_price_break}% above resistance")
        print(f"   AND Volume {self.min_volume_spike}x+ average")
        print()
        
        for symbol in symbols:
            signal = self.check_breakout(symbol)
            if signal:
                breakouts.append(signal)
                self._alert(signal)
        
        return breakouts
    
    def _alert(self, signal: BreakoutSignal):
        """
        Send alert for confirmed breakout
        """
        emoji = "🚀" if signal.confidence == "STRONG" else "⚡" if signal.confidence == "GOOD" else "📊"
        
        print("="*70)
        print(f"{emoji} BREAKOUT CONFIRMED - {signal.symbol} {emoji}")
        print("="*70)
        print()
        print(f"⏰ TIME: {datetime.now().strftime('%H:%M:%S')}")
        print(f"📈 PRICE: ${signal.entry_price:.2f}")
        print(f"🎯 RESISTANCE BROKEN: ${signal.resistance_broken:.2f}")
        print(f"📊 VOLUME SPIKE: {signal.rvol:.1f}x average")
        print(f"💪 CONFIDENCE: {signal.confidence}")
        print(f"⚡ URGENCY: {signal.urgency}")
        print()
        print(f"💰 PLAY: ${signal.suggested_strike:.2f} CALL @ ${signal.option_cost:.2f}")
        print()
        print("🚨 ENTRY SIGNAL CONFIRMED - CONSIDER BUYING NOW")
        print("="*70)
        print()
        
        # Track alert
        self.alerts_sent.append({
            'time': datetime.now().isoformat(),
            'symbol': signal.symbol,
            'signal': signal
        })
    
    def run_continuous_monitoring(self, symbols: List[str], interval_seconds: int = 300):
        """
        Continuously monitor for breakouts
        """
        print("="*70)
        print("🔔 BREAKOUT ENTRY MONITOR - CONTINUOUS MODE")
        print("="*70)
        print(f"Monitoring: {', '.join(symbols)}")
        print(f"Check interval: Every {interval_seconds} seconds")
        print(f"Only alerts on CONFIRMED breakouts")
        print("Press Ctrl+C to stop")
        print("="*70)
        print()
        
        try:
            while True:
                signals = self.scan_for_breakouts(symbols)
                
                if not signals:
                    print(f"{datetime.now().strftime('%H:%M:%S')} - No breakouts yet... watching")
                
                print(f"\nNext check in {interval_seconds} seconds...\n")
                time.sleep(interval_seconds)
                
        except KeyboardInterrupt:
            print("\n\nMonitoring stopped.")
            print(f"Total alerts sent: {len(self.alerts_sent)}")


def quick_breakout_check(symbols: List[str] = None):
    """
    Quick check for breakouts right now
    """
    if symbols is None:
        symbols = ['F', 'KMI', 'NOK', 'T', 'BAC', 'SOFI', 'PLTR', 'AMC', 'GME']
    
    monitor = BreakoutEntryAlerts()
    signals = monitor.scan_for_breakouts(symbols)
    
    if not signals:
        print("\n❌ No confirmed breakouts right now.")
        print("Stocks are still consolidating. Wait for price + volume spike.")
    
    return signals


def start_monitoring(symbols: List[str] = None):
    """
    Start continuous monitoring
    """
    if symbols is None:
        symbols = ['F', 'KMI', 'NOK', 'T', 'BAC', 'SOFI', 'PLTR', 'AMC', 'GME',
                   'RIVN', 'LCID', 'UBER', 'AAL', 'CCL', 'XOM', 'OXY']
    
    monitor = BreakoutEntryAlerts()
    monitor.run_continuous_monitoring(symbols)


# Demo
if __name__ == "__main__":
    import sys
    
    print("="*70)
    print("🚀 BREAKOUT ENTRY ALERT SYSTEM")
    print("Only alerts when breakout is CONFIRMED")
    print("="*70)
    print()
    print("Usage:")
    print("  python3 breakout_alerts.py check     # One-time check")
    print("  python3 breakout_alerts.py monitor   # Continuous monitoring")
    print()
    
    if len(sys.argv) > 1 and sys.argv[1] == 'monitor':
        start_monitoring()
    else:
        quick_breakout_check()
