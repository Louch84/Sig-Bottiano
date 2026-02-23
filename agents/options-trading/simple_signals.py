"""
Options Signals Agent
Simple CALL/PUT signals with day trade vs swing classification
"""

import asyncio
import numpy as np
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional, List, Dict
import json

class SignalType(Enum):
    CALL = "CALL"
    PUT = "PUT"

class TradeDuration(Enum):
    DAY_TRADE = "DAY_TRADE"    # 0-1 DTE, momentum/scalp
    SWING = "SWING"            # 2-30 DTE, directional

@dataclass
class OptionSignal:
    symbol: str
    signal_type: SignalType
    duration: TradeDuration
    entry_price: float
    strike: float
    expiration: str      # Format: YYYY-MM-DD
    dte: int
    stop_loss: float
    target_1: float      # First profit target (50%)
    target_2: float      # Second profit target (100%)
    confidence: float    # 0.0 - 1.0
    risk_reward: float
    rationale: str
    timestamp: datetime
    
    def to_dict(self) -> Dict:
        return {
            "symbol": self.symbol,
            "signal": self.signal_type.value,
            "duration": self.duration.value,
            "entry": f"${self.entry_price:.2f}",
            "strike": f"${self.strike:.2f}",
            "expiration": self.expiration,
            "dte": self.dte,
            "stop_loss": f"${self.stop_loss:.2f}",
            "target_1": f"${self.target_1:.2f}",
            "target_2": f"${self.target_2:.2f}",
            "confidence": f"{self.confidence:.0%}",
            "r:r": f"1:{self.risk_reward:.1f}",
            "rationale": self.rationale,
            "time": self.timestamp.strftime("%H:%M")
        }

class OptionsSignalsAgent:
    """
    Generates clean CALL/PUT signals with clear day trade vs swing labels.
    
    DAY_TRADE (0-1 DTE):
    - Based on momentum, breakouts, unusual volume
    - Tight stops, quick exits
    - High confidence only (70%+)
    
    SWING (2-30 DTE):
    - Based on trend, support/resistance, IV rank
    - Wider stops, hold for days
    - Directional thesis required
    """
    
    def __init__(self):
        self.watchlist = [
            "SPY", "QQQ", "IWM", "AAPL", "TSLA", "NVDA", "AMD", 
            "MSFT", "AMZN", "META", "GOOGL", "NFLX", "CRM"
        ]
        self.signals_history: List[OptionSignal] = []
        
    async def scan_for_signals(self) -> List[OptionSignal]:
        """Scan watchlist and generate signals"""
        signals = []
        
        for symbol in self.watchlist:
            # Check for day trade setup
            day_trade = self._check_day_trade_setup(symbol)
            if day_trade:
                signals.append(day_trade)
                continue
            
            # Check for swing setup
            swing = self._check_swing_setup(symbol)
            if swing:
                signals.append(swing)
        
        # Sort by confidence
        signals.sort(key=lambda x: x.confidence, reverse=True)
        
        # Store top signals
        self.signals_history.extend(signals[:5])
        
        return signals[:5]  # Return top 5
    
    def _check_day_trade_setup(self, symbol: str) -> Optional[OptionSignal]:
        """Check for 0-1 DTE day trade opportunity"""
        
        # Simulate price action analysis
        price = self._get_price(symbol)
        volume_surge = np.random.random() < 0.15  # 15% chance of volume surge
        breakout = np.random.random() < 0.12      # 12% chance of breakout
        
        if not (volume_surge or breakout):
            return None
        
        # Determine direction
        if volume_surge and breakout:
            direction = SignalType.CALL if np.random.random() > 0.4 else SignalType.PUT
        elif volume_surge:
            direction = SignalType.CALL if np.random.random() > 0.5 else SignalType.PUT
        else:
            direction = SignalType.CALL if np.random.random() > 0.45 else SignalType.PUT
        
        # Day trade needs high confidence
        confidence = np.random.uniform(0.70, 0.90)
        
        # Pick strike (0DTE or 1DTE)
        dte = 0 if np.random.random() > 0.3 else 1
        expiration = (datetime.now() + timedelta(days=dte)).strftime("%Y-%m-%d")
        
        # Strike selection (ATM or slight OTM for day trades)
        if direction == SignalType.CALL:
            strike = round(price * np.random.uniform(1.00, 1.03), 1)
        else:
            strike = round(price * np.random.uniform(0.97, 1.00), 1)
        
        # Tight stops for day trades (0.5-1%)
        stop_pct = np.random.uniform(0.005, 0.01)
        if direction == SignalType.CALL:
            stop = price * (1 - stop_pct)
            target_1 = price * 1.015
            target_2 = price * 1.03
        else:
            stop = price * (1 + stop_pct)
            target_1 = price * 0.985
            target_2 = price * 0.97
        
        risk = abs(price - stop)
        reward = abs(target_2 - price)
        rr = reward / risk if risk > 0 else 2
        
        rationale = self._generate_day_trade_rationale(symbol, direction, volume_surge, breakout)
        
        return OptionSignal(
            symbol=symbol,
            signal_type=direction,
            duration=TradeDuration.DAY_TRADE,
            entry_price=price,
            strike=strike,
            expiration=expiration,
            dte=dte,
            stop_loss=stop,
            target_1=target_1,
            target_2=target_2,
            confidence=confidence,
            risk_reward=rr,
            rationale=rationale,
            timestamp=datetime.now()
        )
    
    def _check_swing_setup(self, symbol: str) -> Optional[OptionSignal]:
        """Check for 2-30 DTE swing trade opportunity"""
        
        price = self._get_price(symbol)
        
        # Swing setups are less frequent
        trend_aligned = np.random.random() < 0.08
        support_bounce = np.random.random() < 0.06
        iv_crush_candidate = np.random.random() < 0.05
        
        if not (trend_aligned or support_bounce or iv_crush_candidate):
            return None
        
        # Determine direction based on setup
        if trend_aligned:
            direction = SignalType.CALL if np.random.random() > 0.4 else SignalType.PUT
        elif support_bounce:
            direction = SignalType.CALL
        else:  # IV crush
            direction = SignalType.CALL if np.random.random() > 0.5 else SignalType.PUT
        
        confidence = np.random.uniform(0.60, 0.85)
        
        # DTE selection (7, 14, 21, or 30)
        dte_options = [7, 14, 21, 30]
        dte_weights = [0.3, 0.4, 0.2, 0.1]
        dte = np.random.choice(dte_options, p=dte_weights)
        expiration = (datetime.now() + timedelta(days=dte)).strftime("%Y-%m-%d")
        
        # Strike selection (5-10% OTM for swings)
        otm_pct = np.random.uniform(0.03, 0.10)
        if direction == SignalType.CALL:
            strike = round(price * (1 + otm_pct), 1)
        else:
            strike = round(price * (1 - otm_pct), 1)
        
        # Wider stops for swings (2-4%)
        stop_pct = np.random.uniform(0.02, 0.04)
        if direction == SignalType.CALL:
            stop = price * (1 - stop_pct)
            target_1 = strike * 1.02  # Strike + 2%
            target_2 = strike * 1.05  # Strike + 5%
        else:
            stop = price * (1 + stop_pct)
            target_1 = strike * 0.98
            target_2 = strike * 0.95
        
        risk = abs(price - stop)
        reward = abs(target_2 - price)
        rr = reward / risk if risk > 0 else 2.5
        
        rationale = self._generate_swing_rationale(symbol, direction, trend_aligned, support_bounce, iv_crush_candidate)
        
        return OptionSignal(
            symbol=symbol,
            signal_type=direction,
            duration=TradeDuration.SWING,
            entry_price=price,
            strike=strike,
            expiration=expiration,
            dte=dte,
            stop_loss=stop,
            target_1=target_1,
            target_2=target_2,
            confidence=confidence,
            risk_reward=rr,
            rationale=rationale,
            timestamp=datetime.now()
        )
    
    def _get_price(self, symbol: str) -> float:
        """Simulate getting current price"""
        base_prices = {
            "SPY": 595, "QQQ": 515, "IWM": 225,
            "AAPL": 225, "TSLA": 250, "NVDA": 140,
            "AMD": 140, "MSFT": 430, "AMZN": 225,
            "META": 590, "GOOGL": 175, "NFLX": 885,
            "CRM": 310
        }
        base = base_prices.get(symbol, 50)
        noise = np.random.uniform(-0.02, 0.02)
        return round(base * (1 + noise), 2)
    
    def _generate_day_trade_rationale(self, symbol: str, direction: SignalType, 
                                      volume_surge: bool, breakout: bool) -> str:
        """Generate day trade rationale"""
        reasons = []
        
        if volume_surge:
            reasons.append(f"Unusual volume ({np.random.randint(150, 300)}% of avg)")
        if breakout:
            reasons.append(f"{'Bullish' if direction == SignalType.CALL else 'Bearish'} breakout")
        
        reasons.append(f"Momentum aligned with {direction.value}s")
        reasons.append("0DTE/1DTE for quick theta decay capture")
        
        return "; ".join(reasons)
    
    def _generate_swing_rationale(self, symbol: str, direction: SignalType,
                                  trend: bool, support: bool, iv_crush: bool) -> str:
        """Generate swing trade rationale"""
        reasons = []
        
        if trend:
            reasons.append(f"Trend continuation setup ({direction.value} bias)")
        if support:
            reasons.append("Support bounce with volume confirmation")
        if iv_crush:
            reasons.append(f"Post-earnings IV crush opportunity ({direction.value}s)")
        
        reasons.append(f"{np.random.choice([7, 14, 21, 30])}DTE for time to work")
        
        return "; ".join(reasons)
    
    def format_signal(self, signal: OptionSignal) -> str:
        """Format signal for display"""
        
        duration_emoji = "⚡" if signal.duration == TradeDuration.DAY_TRADE else "📈"
        signal_emoji = "🟢 CALL" if signal.signal_type == SignalType.CALL else "🔴 PUT"
        
        lines = [
            f"\n{'='*60}",
            f"{duration_emoji} {signal.duration.value.replace('_', ' ')} SIGNAL",
            f"{'='*60}",
            f"",
            f"Symbol:    {signal.symbol}",
            f"Signal:    {signal_emoji}",
            f"Entry:     ${signal.entry_price:.2f}",
            f"Strike:    ${signal.strike:.2f} ({signal.dte} DTE)",
            f"Expires:   {signal.expiration}",
            f"",
            f"Stop Loss: ${signal.stop_loss:.2f}",
            f"Target 1:  ${signal.target_1:.2f} (50% gain)",
            f"Target 2:  ${signal.target_2:.2f} (100% gain)",
            f"",
            f"Confidence: {signal.confidence:.0%}",
            f"Risk:Reward: 1:{signal.risk_reward:.1f}",
            f"",
            f"Rationale: {signal.rationale}",
            f"{'='*60}\n"
        ]
        
        return "\n".join(lines)
    
    async def run_continuous(self, interval_seconds: int = 60):
        """Run continuous signal generation"""
        
        print("="*60)
        print("OPTIONS SIGNALS AGENT")
        print("Simple CALL/PUT signals | Day Trade & Swing")
        print("="*60)
        print(f"\nWatchlist: {', '.join(self.watchlist)}")
        print(f"Scanning every {interval_seconds} seconds...")
        print("Press Ctrl+C to stop\n")
        
        cycle = 0
        try:
            while True:
                cycle += 1
                print(f"--- Scan #{cycle} at {datetime.now().strftime('%H:%M:%S')} ---")
                
                signals = await self.scan_for_signals()
                
                if signals:
                    for signal in signals:
                        print(self.format_signal(signal))
                else:
                    print("No high-confidence signals this scan.\n")
                
                await asyncio.sleep(interval_seconds)
                
        except KeyboardInterrupt:
            print("\n\nStopped. Generating summary...")
            self._print_summary()
    
    def _print_summary(self):
        """Print session summary"""
        if not self.signals_history:
            print("No signals generated.")
            return
        
        day_trades = [s for s in self.signals_history if s.duration == TradeDuration.DAY_TRADE]
        swings = [s for s in self.signals_history if s.duration == TradeDuration.SWING]
        calls = [s for s in self.signals_history if s.signal_type == SignalType.CALL]
        puts = [s for s in self.signals_history if s.signal_type == SignalType.PUT]
        
        print("\n" + "="*60)
        print("SESSION SUMMARY")
        print("="*60)
        print(f"Total Signals: {len(self.signals_history)}")
        print(f"  Day Trades: {len(day_trades)}")
        print(f"  Swings: {len(swings)}")
        print(f"  Calls: {len(calls)}")
        print(f"  Puts: {len(puts)}")
        print(f"Avg Confidence: {np.mean([s.confidence for s in self.signals_history]):.1%}")
        print("="*60)

# Quick run function
async def main():
    agent = OptionsSignalsAgent()
    await agent.run_continuous(interval_seconds=30)

if __name__ == "__main__":
    asyncio.run(main())
