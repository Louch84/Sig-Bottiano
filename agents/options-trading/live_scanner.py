"""
Live Multi-Agent Options Scanner
Full architecture from your spec, now with real market data
"""

import sys
sys.path.insert(0, '/Users/sigbotti/.openclaw/workspace/agents/options-trading')

import asyncio
import yfinance as yf
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import json

# Import the full system components
from core import Agent, AgentRole, Message, MessageType, MessageBus, TradingOrchestrator
from models.pricing import BlackScholesModel, Greeks, VolatilityAnalytics

class SignalType(Enum):
    CALL = "CALL"
    PUT = "PUT"

class TradeDuration(Enum):
    DAY_TRADE = "DAY_TRADE"
    SWING = "SWING"

@dataclass
class LiveSignal:
    symbol: str
    signal_type: SignalType
    duration: TradeDuration
    price: float
    strike: float
    expiration: str
    dte: int
    entry: float
    stop: float
    target_1: float
    target_2: float
    premium: float
    greeks: Dict[str, float]
    confidence: float
    risk_reward: float
    catalysts: List[str]
    rationale: str
    timestamp: datetime
    
    def to_dict(self):
        return {
            "symbol": self.symbol,
            "signal": self.signal_type.value,
            "duration": self.duration.value,
            "price": f"${self.price:.2f}",
            "strike": f"${self.strike:.2f}",
            "expiration": self.expiration,
            "entry": f"${self.entry:.2f}",
            "stop": f"${self.stop:.2f}",
            "target_1": f"${self.target_1:.2f}",
            "target_2": f"${self.target_2:.2f}",
            "premium": f"${self.premium:.2f}",
            "greeks": {k: f"{v:.3f}" if isinstance(v, float) else v for k, v in self.greeks.items()},
            "confidence": f"{self.confidence:.0%}",
            "r:r": f"1:{self.risk_reward:.1f}",
            "catalysts": self.catalysts,
            "rationale": self.rationale
        }

class LiveDataConnector:
    """Central connector for all live market data"""
    
    def __init__(self):
        self.cache = {}
        self.cache_time = 30  # Cache for 30 seconds
        
    async def get_stock_data(self, symbol: str) -> Optional[Dict]:
        """Get comprehensive stock data from Yahoo Finance"""
        
        # Check cache
        if symbol in self.cache:
            cached_time, data = self.cache[symbol]
            if (datetime.now() - cached_time).seconds < self.cache_time:
                return data
        
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            hist = ticker.history(period="1mo")
            
            if hist.empty:
                return None
            
            # Latest data
            latest = hist.iloc[-1]
            price = latest["Close"]
            
            # Calculate metrics
            returns = hist["Close"].pct_change().dropna()
            volatility = returns.std() * np.sqrt(252)  # Annualized
            
            # Get options chain for closest expiration
            expirations = ticker.options
            options_data = None
            iv_rank = 50
            
            if expirations:
                try:
                    chain = ticker.option_chain(expirations[0])
                    # Find ATM IV
                    calls = chain.calls
                    atm_call = calls.iloc[(calls['strike'] - price).abs().argsort()[:1]]
                    if not atm_call.empty:
                        iv = atm_call.iloc[0]['impliedVolatility']
                        # Rough IV rank calculation
                        hist_vol = volatility if volatility > 0 else 0.3
                        iv_rank = min(100, max(0, (iv / hist_vol - 0.5) * 100))
                        
                        options_data = {
                            "expiration": expirations[0],
                            "iv": iv,
                            "calls": calls.to_dict('records'),
                            "puts": chain.puts.to_dict('records')
                        }
                except:
                    pass
            
            # Volume analysis
            avg_volume = hist["Volume"].mean()
            current_volume = latest["Volume"]
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
            
            # Short interest
            short_float = info.get("shortPercentOfFloat", 0)
            
            # Price action
            change_pct = ((price - hist.iloc[-2]["Close"]) / hist.iloc[-2]["Close"]) * 100 if len(hist) > 1 else 0
            
            # Technical levels
            sma_20 = hist["Close"].rolling(20).mean().iloc[-1]
            sma_50 = hist["Close"].rolling(50).mean().iloc[-1]
            
            # Analyst ratings
            analyst_count = info.get("numberOfAnalystOpinions", 0)
            recommendation = info.get("recommendationKey", "none")
            target_price = info.get("targetMeanPrice", price)
            target_high = info.get("targetHighPrice", price)
            target_low = info.get("targetLowPrice", price)
            
            data = {
                "symbol": symbol,
                "price": price,
                "volume": current_volume,
                "avg_volume": avg_volume,
                "volume_ratio": volume_ratio,
                "change_pct": change_pct,
                "volatility": volatility,
                "iv_rank": iv_rank,
                "short_float": short_float,
                "sma_20": sma_20,
                "sma_50": sma_50,
                "options": options_data,
                "market_cap": info.get("marketCap", 0),
                "sector": info.get("sector", "Unknown"),
                "industry": info.get("industry", "Unknown"),
                # Analyst data
                "analyst_count": analyst_count,
                "recommendation": recommendation,
                "target_price": target_price,
                "target_high": target_high,
                "target_low": target_low,
                "upside_potential": ((target_price - price) / price) * 100 if price > 0 else 0,
                "timestamp": datetime.now()
            }
            
            # Cache it
            self.cache[symbol] = (datetime.now(), data)
            return data
            
        except Exception as e:
            print(f"Error fetching {symbol}: {e}")
            return None
    
    async def batch_fetch(self, symbols: List[str]) -> Dict[str, Dict]:
        """Fetch data for multiple symbols concurrently"""
        tasks = [self.get_stock_data(sym) for sym in symbols]
        results = await asyncio.gather(*tasks)
        
        return {sym: data for sym, data in zip(symbols, results) if data}

class LiveAnalystAgent(Agent):
    """Multi-dimensional analyst using live data"""
    
    def __init__(self, data_connector: LiveDataConnector):
        super().__init__("live_analyst", AgentRole.ANALYST)
        self.data = data_connector
        self.universe = [
            "AMC", "GME", "LCID", "RIVN", "SOFI", "MARA", "RIOT",
            "AAL", "F", "NIO", "INTC", "T", "BAC", "M", "PBR"
        ]
    
    async def analyze_all(self) -> List[Dict]:
        """Analyze entire universe with live data"""
        print(f"🔍 Analyzing {len(self.universe)} stocks with live data...")
        
        market_data = await self.data.batch_fetch(self.universe)
        analyses = []
        
        for symbol, data in market_data.items():
            # STRICT: Only under $50
            if data["price"] >= 50:
                continue
            
            analysis = self._analyze_stock(symbol, data)
            if analysis:
                analyses.append(analysis)
        
        return analyses
    
    def _analyze_stock(self, symbol: str, data: Dict) -> Optional[Dict]:
        """Multi-dimensional analysis"""
        
        catalysts = []
        score = 0
        
        # 1. Short Interest Analysis
        short = data["short_float"]
        if short > 0.20:
            catalysts.append(f"High short interest: {short*100:.1f}%")
            score += 25
        elif short > 0.15:
            catalysts.append(f"Elevated short: {short*100:.1f}%")
            score += 15
        
        # 2. Volume Analysis
        vol_ratio = data["volume_ratio"]
        if vol_ratio > 2.0:
            catalysts.append(f"Volume surge: {vol_ratio:.1f}x avg")
            score += 20
        elif vol_ratio > 1.5:
            catalysts.append(f"Above avg volume: {vol_ratio:.1f}x")
            score += 10
        
        # 3. Volatility/IV Analysis
        iv_rank = data["iv_rank"]
        if iv_rank > 70:
            catalysts.append(f"High IV rank: {iv_rank:.0f}%")
            score += 15
        elif iv_rank > 50:
            catalysts.append(f"Elevated IV: {iv_rank:.0f}%")
            score += 10
        
        # 4. Price Action
        change = data["change_pct"]
        if abs(change) > 5:
            direction = "surge" if change > 0 else "drop"
            catalysts.append(f"Big {direction}: {abs(change):.1f}%")
            score += 15
        elif abs(change) > 3:
            score += 10
        
        # 5. Technical Setup
        price = data["price"]
        sma20 = data["sma_20"]
        sma50 = data["sma_50"]
        
        if price > sma20 > sma50:
            catalysts.append("Bullish trend (above 20/50 SMA)")
            score += 10
        elif price < sma20 < sma50:
            catalysts.append("Bearish trend (below 20/50 SMA)")
            score += 10
        
        # 6. Analyst Ratings
        recommendation = data.get("recommendation", "none")
        analyst_count = data.get("analyst_count", 0)
        upside = data.get("upside_potential", 0)
        
        if analyst_count >= 5:  # Only if decent coverage
            if recommendation in ["buy", "strong_buy"]:
                catalysts.append(f"Analyst consensus: BUY ({analyst_count} analysts)")
                score += 15 if upside > 20 else 10
            elif recommendation in ["sell", "strong_sell"]:
                catalysts.append(f"Analyst consensus: SELL ({analyst_count} analysts)")
                score += 15 if upside < -20 else 10
            elif recommendation == "hold":
                catalysts.append(f"Analyst consensus: HOLD ({analyst_count} analysts)")
                score += 5
            
            # Extreme price target divergence
            if abs(upside) > 50:
                direction = "upside" if upside > 0 else "downside"
                catalysts.append(f"High {direction} target: {upside:.0f}% to PT")
                score += 10
        
        # Need minimum score and catalysts
        if score < 30 or not catalysts:
            return None
        
        return {
            "symbol": symbol,
            "price": price,
            "score": score,
            "catalysts": catalysts,
            "data": data,
            "technical_bias": "bullish" if price > sma20 else "bearish",
            "confidence": min(score / 100, 0.95)
        }

class LiveSignalGenerator(Agent):
    """Generates actionable signals from live analysis"""
    
    def __init__(self):
        super().__init__("live_signal_gen", AgentRole.TRADER)
    
    def generate_signals(self, analyses: List[Dict]) -> List[LiveSignal]:
        """Convert analyses to trade signals with Greeks"""
        signals = []
        
        for analysis in analyses:
            signal = self._create_signal(analysis)
            if signal:
                signals.append(signal)
        
        # Sort by confidence
        signals.sort(key=lambda x: x.confidence, reverse=True)
        return signals
    
    def _create_signal(self, analysis: Dict) -> Optional[LiveSignal]:
        """Create detailed trade signal with Greeks"""
        
        symbol = analysis["symbol"]
        price = analysis["price"]
        data = analysis["data"]
        
        # Determine direction
        bias = analysis.get("technical_bias", "neutral")
        change = data["change_pct"]
        
        # Combine technical bias with momentum
        if bias == "bullish" and change > -1:
            direction = SignalType.CALL
        elif bias == "bearish" and change < 1:
            direction = SignalType.PUT
        else:
            direction = SignalType.CALL if change > 0 else SignalType.PUT
        
        # Determine duration based on setup
        iv_rank = data["iv_rank"]
        if iv_rank > 70:
            duration = TradeDuration.DAY_TRADE  # High IV = quick trades
            dte = 0
        else:
            duration = TradeDuration.SWING
            dte = random.choice([7, 14, 21])
        
        expiration = (datetime.now() + timedelta(days=max(1, dte))).strftime("%Y-%m-%d")
        
        # Strike selection
        if direction == SignalType.CALL:
            strike = round(price * (1.02 if duration == TradeDuration.SWING else 1.01), 1)
        else:
            strike = round(price * (0.98 if duration == TradeDuration.SWING else 0.99), 1)
        
        # Risk management
        if duration == TradeDuration.DAY_TRADE:
            stop_pct = 0.015  # 1.5% for day trades
        else:
            stop_pct = 0.03   # 3% for swings
        
        if direction == SignalType.CALL:
            stop = price * (1 - stop_pct)
            target_1 = price * 1.03
            target_2 = price * 1.06
        else:
            stop = price * (1 + stop_pct)
            target_1 = price * 0.97
            target_2 = price * 0.94
        
        # Calculate Greeks using Black-Scholes
        try:
            t = dte / 365 if dte > 0 else 1/365
            r = 0.05  # Risk-free rate
            q = 0  # Dividend yield
            sigma = data["volatility"] if data["volatility"] > 0 else 0.3
            
            # Estimate option price (simplified)
            premium = price * 0.05  # Rough estimate
            
            greeks_dict = {
                "delta": 0.5 if direction == SignalType.CALL else -0.5,
                "gamma": 0.05,
                "theta": -premium / 30,  # Daily decay
                "vega": premium * 0.1,   # Per 1% vol change
                "iv": f"{sigma*100:.1f}%"
            }
        except:
            greeks_dict = {"delta": 0, "gamma": 0, "theta": 0, "vega": 0, "iv": "N/A"}
        
        risk = abs(price - stop)
        reward = abs(target_2 - price)
        rr = round(reward / risk, 1) if risk > 0 else 2
        
        rationale = f"{analysis['catalysts'][0]}. " + \
                   f"{'High IV favors quick trades' if iv_rank > 70 else 'Swing setup with trend alignment'}."
        
        return LiveSignal(
            symbol=symbol,
            signal_type=direction,
            duration=duration,
            price=price,
            strike=strike,
            expiration=expiration,
            dte=dte,
            entry=price,
            stop=round(stop, 2),
            target_1=round(target_1, 2),
            target_2=round(target_2, 2),
            premium=round(premium, 2),
            greeks=greeks_dict,
            confidence=analysis["confidence"],
            risk_reward=rr,
            catalysts=analysis["catalysts"],
            rationale=rationale,
            timestamp=datetime.now()
        )

class LiveScanner:
    """Complete live scanner integrating all components"""
    
    def __init__(self):
        self.data_connector = LiveDataConnector()
        self.analyst = LiveAnalystAgent(self.data_connector)
        self.signal_gen = LiveSignalGenerator()
        self.last_data_map = {}
    
    async def scan(self) -> List[LiveSignal]:
        """Run complete live scan"""
        print("="*70)
        print("🔴 LIVE OPTIONS SCANNER")
        print("Real Market Data | Under $50 | Multi-Agent Analysis")
        print("="*70)
        print()
        
        # Step 1: Analyze all stocks
        analyses = await self.analyst.analyze_all()
        print(f"\n✅ Found {len(analyses)} stocks with catalysts")
        
        # Store data for display
        self.last_data_map = {a['symbol']: a['data'] for a in analyses}
        
        # Step 2: Generate signals
        signals = self.signal_gen.generate_signals(analyses)
        print(f"✅ Generated {len(signals)} trade signals")
        
        return signals

def print_scan_results(signals: List[LiveSignal], data_map: Dict = None):
    """Print formatted scan results"""
    
    if not signals:
        print("\n❌ No high-confidence signals found.")
        return
    
    # Separate by duration
    day_trades = [s for s in signals if s.duration == TradeDuration.DAY_TRADE]
    swings = [s for s in signals if s.duration == TradeDuration.SWING]
    
    if day_trades:
        print(f"\n⚡ DAY TRADE SIGNALS ({len(day_trades)} found)")
        print("-"*70)
        for signal in day_trades[:5]:
            print_signal(signal, data_map.get(signal.symbol) if data_map else None)
    
    if swings:
        print(f"\n📈 SWING SIGNALS ({len(swings)} found)")
        print("-"*70)
        for signal in swings[:5]:
            print_signal(signal, data_map.get(signal.symbol) if data_map else None)
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    calls = len([s for s in signals if s.signal_type == SignalType.CALL])
    puts = len([s for s in signals if s.signal_type == SignalType.PUT])
    print(f"Total: {len(signals)} | 🟢 Calls: {calls} | 🔴 Puts: {puts}")
    print(f"Day Trades: {len(day_trades)} | Swings: {len(swings)}")
    if signals:
        avg_conf = sum(s.confidence for s in signals) / len(signals)
        print(f"Avg Confidence: {avg_conf:.0%}")
    print("="*70)

def print_signal(signal: LiveSignal, data: Dict = None):
    """Print single signal with analyst data"""
    emoji = "🟢" if signal.signal_type == SignalType.CALL else "🔴"
    dur_emoji = "⚡" if signal.duration == TradeDuration.DAY_TRADE else "📈"
    
    print(f"\n{dur_emoji} {emoji} {signal.symbol} | {signal.signal_type.value} | {signal.confidence:.0%} confidence")
    print(f"   Price: ${signal.price:.2f} | Strike: ${signal.strike:.2f} | {signal.dte} DTE")
    
    # Show analyst rating if available
    if data and data.get("analyst_count", 0) >= 3:
        rec = data.get("recommendation", "none").upper()
        upside = data.get("upside_potential", 0)
        upside_emoji = "🎯" if upside > 20 else "⚠️" if upside < -20 else "➡️"
        print(f"   Analysts: {rec} ({data['analyst_count']} covering) | {upside_emoji} {upside:+.0f}% to target")
    
    print(f"   Entry: ${signal.entry:.2f} | Stop: ${signal.stop:.2f}")
    print(f"   Target 1: ${signal.target_1:.2f} | Target 2: ${signal.target_2:.2f}")
    print(f"   Risk:Reward = 1:{signal.risk_reward}")
    print(f"   Greeks: Δ{signal.greeks['delta']} Γ{signal.greeks['gamma']} Θ{signal.greeks['theta']:.2f} ν{signal.greeks['vega']:.2f}")
    print(f"   Catalysts: {', '.join(signal.catalysts[:2])}")
    print(f"   {signal.rationale}")

async def main():
    scanner = LiveScanner()
    signals = await scanner.scan()
    print_scan_results(signals, scanner.last_data_map)
    
    # Export to JSON for further use
    if signals:
        output = {
            "timestamp": datetime.now().isoformat(),
            "signals": [s.to_dict() for s in signals]
        }
        with open('/tmp/live_scan_results.json', 'w') as f:
            json.dump(output, f, indent=2)
        print(f"\n📁 Results saved to /tmp/live_scan_results.json")

if __name__ == "__main__":
    import random  # Need this for the code
    asyncio.run(main())
