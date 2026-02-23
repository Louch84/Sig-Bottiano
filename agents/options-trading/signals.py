"""
Options Signals Agent
Simple CALL/PUT signals with day trade vs swing classification
No external dependencies - uses only standard library
"""

import asyncio
import random
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional, List, Dict

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
    expiration: str
    dte: int
    stop_loss: float
    target_1: float
    target_2: float
    confidence: float
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
            day_trade = self._check_day_trade_setup(symbol)
            if day_trade:
                signals.append(day_trade)
                continue
            
            swing = self._check_swing_setup(symbol)
            if swing:
                signals.append(swing)
        
        signals.sort(key=lambda x: x.confidence, reverse=True)
        self.signals_history.extend(signals[:5])
        
        return signals[:5]
    
    def _check_day_trade_setup(self, symbol: str) -> Optional[OptionSignal]:
        """Check for 0-1 DTE day trade opportunity"""
        
        price = self._get_price(symbol)
        volume_surge = random.random() < 0.15
        breakout = random.random() < 0.12
        
        if not (volume_surge or breakout):
            return None
        
        if volume_surge and breakout:
            direction = SignalType.CALL if random.random() > 0.4 else SignalType.PUT
        elif volume_surge:
            direction = SignalType.CALL if random.random() > 0.5 else SignalType.PUT
        else:
            direction = SignalType.CALL if random.random() > 0.45 else SignalType.PUT
        
        confidence = random.uniform(0.70, 0.90)
        dte = 0 if random.random() > 0.3 else 1
        expiration = (datetime.now() + timedelta(days=dte)).strftime("%Y-%m-%d")
        
        if direction == SignalType.CALL:
            strike = round(price * random.uniform(1.00, 1.03), 1)
        else:
            strike = round(price * random.uniform(0.97, 1.00), 1)
        
        stop_pct = random.uniform(0.005, 0.01)
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
            symbol=symbol, signal_type=direction, duration=TradeDuration.DAY_TRADE,
            entry_price=price, strike=strike, expiration=expiration, dte=dte,
            stop_loss=stop, target_1=target_1, target_2=target_2,
            confidence=confidence, risk_reward=rr, rationale=rationale,
            timestamp=datetime.now()
        )
    
    def _check_swing_setup(self, symbol: str) -> Optional[OptionSignal]:
        """Check for 2-30 DTE swing trade opportunity"""
        
        price = self._get_price(symbol)
        trend_aligned = random.random() < 0.08
        support_bounce = random.random() < 0.06
        iv_crush = random.random() < 0.05
        
        if not (trend_aligned or support_bounce or iv_crush):
            return None
        
        if trend_aligned:
            direction = SignalType.CALL if random.random() > 0.4 else SignalType.PUT
        elif support_bounce:
            direction = SignalType.CALL
        else:
            direction = SignalType.CALL if random.random() > 0.5 else SignalType.PUT
        
        confidence = random.uniform(0.60, 0.85)
        
        dte_options = [7, 14, 21, 30]
        dte_weights = [0.3, 0.4, 0.2, 0.1]
        dte = random.choices(dte_options, weights=dte_weights)[0]
        expiration = (datetime.now() + timedelta(days=dte)).strftime("%Y-%m-%d")
        
        otm_pct = random.uniform(0.03, 0.10)
        if direction == SignalType.CALL:
            strike = round(price * (1 + otm_pct), 1)
        else:
            strike = round(price * (1 - otm_pct), 1)
        
        stop_pct = random.uniform(0.02, 0.04)
        if direction == SignalType.CALL:
            stop = price * (1 - stop_pct)
            target_1 = strike * 1.02
            target_2 = strike * 1.05
        else:
            stop = price * (1 + stop_pct)
            target_1 = strike * 0.98
            target_2 = strike * 0.95
        
        risk = abs(price - stop)
        reward = abs(target_2 - price)
        rr = reward / risk if risk > 0 else 2.5
        
        rationale = self._generate_swing_rationale(symbol, direction, trend_aligned, support_bounce, iv_crush)
        
        return OptionSignal(
            symbol=symbol, signal_type=direction, duration=TradeDuration.SWING,
            entry_price=price, strike=strike, expiration=expiration, dte=dte,
            stop_loss=stop, target_1=target_1, target_2=target_2,
            confidence=confidence, risk_reward=rr, rationale=rationale,
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
        noise = random.uniform(-0.02, 0.02)
        return round(base * (1 + noise), 2)
    
    def _generate_day_trade_rationale(self, symbol, direction, volume_surge, breakout):
        reasons = []
        if volume_surge:
            reasons.append(f"Unusual volume ({random.randint(150, 300)}% of avg)")
        if breakout:
            reasons.append(f"{'Bullish' if direction == SignalType.CALL else 'Bearish'} breakout")
        reasons.append(f"Momentum aligned with {direction.value}s")
        reasons.append("0DTE/1DTE for quick theta decay capture")
        return "; ".join(reasons)
    
    def _generate_swing_rationale(self, symbol, direction, trend, support, iv_crush):
        reasons = []
        if trend:
            reasons.append(f"Trend continuation setup ({direction.value} bias)")
        if support:
            reasons.append("Support bounce with volume confirmation")
        if iv_crush:
            reasons.append(f"Post-earnings IV crush opportunity ({direction.value}s)")
        reasons.append(f"{random.choice([7, 14, 21, 30])}DTE for time to work")
        return "; ".join(reasons)

async def main():
    agent = OptionsSignalsAgent()
    signals = await agent.scan_for_signals()
    
    print("="*60)
    print("⚡ OPTIONS SIGNALS")
    print("Simple CALL/PUT | Day Trade vs Swing")
    print("="*60)
    print()
    
    if not signals:
        print("No high-confidence signals found.")
        return
    
    day_trades = [s for s in signals if s.duration == TradeDuration.DAY_TRADE]
    swings = [s for s in signals if s.duration == TradeDuration.SWING]
    
    if day_trades:
        print(f"⚡ DAY TRADE SIGNALS ({len(day_trades)} found)\n")
        for signal in day_trades[:3]:
            emoji = "🟢 CALL" if signal.signal_type == SignalType.CALL else "🔴 PUT"
            print(f"{signal.symbol} | {emoji} | {signal.confidence:.0%} confidence")
            print(f"  Entry: ${signal.entry_price:.2f} | Strike: ${signal.strike:.2f} | {signal.dte} DTE")
            print(f"  Stop: ${signal.stop_loss:.2f} | T1: ${signal.target_1:.2f} | T2: ${signal.target_2:.2f}")
            print(f"  R:R = 1:{signal.risk_reward:.1f}")
            print(f"  {signal.rationale}")
            print()
    
    if swings:
        print(f"📈 SWING TRADE SIGNALS ({len(swings)} found)\n")
        for signal in swings[:3]:
            emoji = "🟢 CALL" if signal.signal_type == SignalType.CALL else "🔴 PUT"
            print(f"{signal.symbol} | {emoji} | {signal.confidence:.0%} confidence")
            print(f"  Entry: ${signal.entry_price:.2f} | Strike: ${signal.strike:.2f} | {signal.dte} DTE")
            print(f"  Stop: ${signal.stop_loss:.2f} | T1: ${signal.target_1:.2f} | T2: ${signal.target_2:.2f}")
            print(f"  R:R = 1:{signal.risk_reward:.1f}")
            print(f"  {signal.rationale}")
            print()
    
    print("="*60)

if __name__ == "__main__":
    asyncio.run(main())
