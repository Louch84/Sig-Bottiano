"""
Full Multi-Agent Live Scanner
All agents working together with real data
"""

import sys
sys.path.insert(0, '/Users/sigbotti/.openclaw/workspace/agents/options-trading')

import asyncio
import yfinance as yf
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json

# Import all agent components
from core import Agent, AgentRole, Message, MessageType, TradingOrchestrator
from analyst.agents import FundamentalAnalyst, TechnicalAnalyst, SentimentAnalyst, NewsAnalyst
from research.agents import ResearchTeamLead
from trader.agents import TraderLead, StrategyType
from risk.agents import RiskManager
from models.pricing import BlackScholesModel, Greeks

class SignalType(Enum):
    CALL = "CALL"
    PUT = "PUT"

@dataclass
class ComprehensiveSignal:
    """Complete analysis from all agents"""
    symbol: str
    price: float
    
    # Fundamental Analysis
    fundamental_score: float
    pe_ratio: float
    market_cap: str
    sector: str
    
    # Technical Analysis
    technical_score: float
    trend: str
    support: float
    resistance: float
    sma_20: float
    sma_50: float
    
    # Sentiment Analysis
    sentiment_score: float
    short_interest: float
    volume_ratio: float
    iv_rank: float
    put_call_ratio: float
    unusual_flow: bool
    
    # Research Team Debate
    research_recommendation: str
    bull_case: List[str]
    bear_case: List[str]
    conviction: float
    
    # Risk Assessment
    risk_level: str
    max_position_size: int
    portfolio_impact: str
    
    # Final Signal
    direction: str
    strategy: str
    strike: float
    expiration: str
    entry: float
    stop: float
    target_1: float
    target_2: float
    expected_move_pct: float
    risk_reward: float
    confidence: float
    
    # Big Move Potential
    move_potential_score: int  # 0-100
    catalysts: List[str]
    
    timestamp: datetime
    smc_signals: List[str] = field(default_factory=list)
    
    def to_summary(self) -> Dict:
        return {
            "symbol": self.symbol,
            "price": f"${self.price:.2f}",
            "direction": self.direction,
            "move_potential": f"{self.move_potential_score}/100",
            "confidence": f"{self.confidence:.0%}",
            "expected_move": f"{self.expected_move_pct:.1f}%",
            "strategy": self.strategy,
            "entry": f"${self.entry:.2f}",
            "stop": f"${self.stop:.2f}",
            "target": f"${self.target_2:.2f}",
            "r:r": f"1:{self.risk_reward:.1f}",
            "top_catalyst": self.catalysts[0] if self.catalysts else "N/A"
        }

class LiveDataFeed:
    """Central live data provider for all agents - OPTIMIZED"""
    
    def __init__(self):
        self.cache = {}
        self.cache_time = 600  # 10 minute cache
        
    def _get_cached(self, symbol: str) -> Optional[Dict]:
        """Check if valid cache exists"""
        if symbol in self.cache:
            cached_time, data = self.cache[symbol]
            age = (datetime.now() - cached_time).total_seconds()
            if age < self.cache_time:
                return data
        return None
        
    async def fetch_full_data(self, symbol: str, quick_mode: bool = False) -> Optional[Dict]:
        """Fetch comprehensive data for all agents - OPTIMIZED"""
        
        # Check cache first
        cached = self._get_cached(symbol)
        if cached:
            return cached
        
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            hist = ticker.history(period="1mo")  # OPTIMIZED: 1mo instead of 3mo
            
            if hist.empty:
                return None
            
            latest = hist.iloc[-1]
            price = latest["Close"]
            
            # Check under $50
            if price >= 50:
                return None
            
            # Calculate all metrics
            returns = hist["Close"].pct_change().dropna()
            volatility = returns.std() * np.sqrt(252)
            
            # Technical levels
            sma_20 = hist["Close"].rolling(20).mean().iloc[-1]
            sma_50 = hist["Close"].rolling(50).mean().iloc[-1]
            
            # Support/Resistance (simplified)
            recent = hist.tail(20)
            support = recent["Low"].min()
            resistance = recent["High"].max()
            
            # Volume analysis
            avg_volume = hist["Volume"].mean()
            volume_ratio = latest["Volume"] / avg_volume
            
            # Options data - ONLY fetch for candidates (price < 50 and decent volume)
            iv = 0.3
            put_call_ratio = 1.0
            
            # Skip options fetch if quick mode or not a candidate
            # Options data - ONLY fetch for candidates (price < 50 and decent volume)
            iv = 0.3
            put_call_ratio = 1.0
            
            # Only fetch options for stocks under $50 with decent volume
            if price < 50 and volume_ratio > 0.5:
                try:
                    expirations = ticker.options
                    if expirations:
                        chain = ticker.option_chain(expirations[0])
                        calls = chain.calls
                        puts = chain.puts
                        
                        # Calculate put/call ratio from volume
                        call_volume = calls['volume'].sum() if 'volume' in calls.columns else 0
                        put_volume = puts['volume'].sum() if 'volume' in puts.columns else 0
                        
                        if call_volume > 0:
                            put_call_ratio = put_volume / call_volume
                        elif put_volume > 0:
                            put_call_ratio = 999  # Very high if only puts
                        
                        # Get ATM IV
                        atm = calls.iloc[(calls['strike'] - price).abs().argsort()[:1]]
                        if not atm.empty:
                            iv = atm.iloc[0]['impliedVolatility']
                except:
                    pass
            
            # IV rank estimate
            hist_vol = volatility if volatility > 0 else 0.3
            iv_rank = min(100, max(0, (iv / hist_vol - 0.5) * 100))
            
            # Expected move
            days = 7
            expected_move = price * iv * np.sqrt(days / 365)
            expected_move_pct = (expected_move / price) * 100
            
            data = {
                "symbol": symbol,
                "price": price,
                "change_pct": ((price - hist.iloc[-2]["Close"]) / hist.iloc[-2]["Close"]) * 100,
                "volume": latest["Volume"],
                "avg_volume": avg_volume,
                "volume_ratio": volume_ratio,
                "volatility": volatility,
                "iv": iv,
                "iv_rank": iv_rank,
                "put_call_ratio": put_call_ratio,
                "expected_move": expected_move,
                "expected_move_pct": expected_move_pct,
                
                # Technical
                "sma_20": sma_20,
                "sma_50": sma_50,
                "support": support,
                "resistance": resistance,
                "trend": "bullish" if price > sma_20 > sma_50 else "bearish" if price < sma_20 < sma_50 else "mixed",
                "hist_data": hist,  # Full history for SMC analysis
                
                # Fundamental
                "pe_ratio": info.get("trailingPE", 0),
                "forward_pe": info.get("forwardPE", 0),
                "market_cap": info.get("marketCap", 0),
                "sector": info.get("sector", "Unknown"),
                "industry": info.get("industry", "Unknown"),
                "revenue_growth": info.get("revenueGrowth", 0),
                "profit_margins": info.get("profitMargins", 0),
                
                # Sentiment
                "short_float": info.get("shortPercentOfFloat", 0),
                "short_ratio": info.get("shortRatio", 0),
                "analyst_count": info.get("numberOfAnalystOpinions", 0),
                "recommendation": info.get("recommendationKey", "none"),
                "target_price": info.get("targetMeanPrice", price),
                "target_high": info.get("targetHighPrice", price),
                "target_low": info.get("targetLowPrice", price),
                "upside": ((info.get("targetMeanPrice", price) - price) / price) * 100,
                
                # Company info
                "company_name": info.get("longName", symbol),
                "beta": info.get("beta", 1.0),
                "float_shares": info.get("floatShares", 0),
            }
            
            self.cache[symbol] = (datetime.now(), data)
            return data
            
        except Exception as e:
            print(f"  Error fetching {symbol}: {e}")
            return None
    
    async def batch_fetch(self, symbols: List[str]) -> Dict[str, Dict]:
        """Fetch all symbols concurrently"""
        tasks = [self.fetch_full_data(sym) for sym in symbols]
        results = await asyncio.gather(*tasks)
        return {sym: data for sym, data in zip(symbols, results) if data}

class FullAnalystTeam:
    """All analyst agents working on live data"""
    
    def __init__(self, data_feed: LiveDataFeed):
        self.data = data_feed
        
    async def analyze(self, symbol: str, data: Dict) -> Dict:
        """Run all analyst agents on one stock"""
        
        # 1. FUNDAMENTAL ANALYSIS
        fundamental = self._fundamental_analysis(data)
        
        # 2. TECHNICAL ANALYSIS  
        technical = self._technical_analysis(data)
        
        # 3. SENTIMENT ANALYSIS
        sentiment = self._sentiment_analysis(data)
        
        # 4. RESEARCH DEBATE (Bull/Bear cases)
        research = self._research_debate(data, fundamental, technical, sentiment)
        
        # 5. RISK ASSESSMENT
        risk = self._risk_assessment(data)
        
        return {
            "symbol": symbol,
            "price": data["price"],
            "fundamental": fundamental,
            "technical": technical,
            "sentiment": sentiment,
            "research": research,
            "risk": risk,
            "data": data
        }
    
    def _fundamental_analysis(self, data: Dict) -> Dict:
        """Fundamental Analyst Agent"""
        score = 0
        notes = []
        
        pe = data.get("pe_ratio", 0)
        if 0 < pe < 20:
            score += 20
            notes.append("Reasonable P/E valuation")
        elif pe > 50 or pe < 0:
            score += 5
            notes.append("High P/E or unprofitable")
        
        growth = data.get("revenue_growth", 0)
        if growth > 0.20:
            score += 15
            notes.append("Strong revenue growth")
        elif growth < -0.10:
            score -= 10
            notes.append("Declining revenue")
        
        margins = data.get("profit_margins", 0)
        if margins > 0.15:
            score += 10
            notes.append("Healthy margins")
        
        return {
            "score": max(0, score),
            "pe_ratio": pe,
            "notes": notes,
            "quality": "strong" if score > 30 else "average" if score > 15 else "weak"
        }
    
    def _technical_analysis(self, data: Dict) -> Dict:
        """Technical Analyst Agent with Smart Money Concepts"""
        score = 0
        notes = []
        smc_signals = []
        
        price = data["price"]
        sma20 = data["sma_20"]
        sma50 = data["sma_50"]
        support = data["support"]
        resistance = data["resistance"]
        
        # Get historical data for SMC patterns
        hist = data.get("hist_data", None)
        
        # === SMC ANALYSIS ===
        if hist is not None and len(hist) >= 20:
            # 1. ORDER BLOCK DETECTION
            recent = hist.tail(10)
            highs = recent['High'].values
            lows = recent['Low'].values
            closes = recent['Close'].values
            opens = recent['Open'].values
            
            # Bullish Order Block: Down candle before strong up move
            bullish_ob = None
            for i in range(len(closes)-3, max(0, len(closes)-8), -1):
                if closes[i] < opens[i] and closes[i+1] > opens[i+1] and closes[i+2] > opens[i+2]:
                    if closes[i+2] > highs[i]:  # Strong follow-through
                        bullish_ob = lows[i]
                        smc_signals.append(f"🟢 Bullish Order Block @ ${bullish_ob:.2f}")
                        score += 15
                        break
            
            # Bearish Order Block: Up candle before strong down move
            bearish_ob = None
            for i in range(len(closes)-3, max(0, len(closes)-8), -1):
                if closes[i] > opens[i] and closes[i+1] < opens[i+1] and closes[i+2] < opens[i+2]:
                    if closes[i+2] < lows[i]:  # Strong follow-through
                        bearish_ob = highs[i]
                        smc_signals.append(f"🔴 Bearish Order Block @ ${bearish_ob:.2f}")
                        score += 15
                        break
            
            # 2. FAIR VALUE GAP (FVG) DETECTION
            # Gap between previous high and current low (bullish FVG)
            # or previous low and current high (bearish FVG)
            fvg_bullish = []
            fvg_bearish = []
            
            for i in range(1, min(5, len(closes))):
                prev_high = highs[-(i+1)]
                prev_low = lows[-(i+1)]
                curr_low = lows[-i]
                curr_high = highs[-i]
                
                # Bullish FVG: Current low > Previous high (gap up)
                if curr_low > prev_high:
                    gap_size = ((curr_low - prev_high) / prev_high) * 100
                    if gap_size > 1:  # Significant gap
                        fvg_bullish.append((prev_high, curr_low, gap_size))
                
                # Bearish FVG: Current high < Previous low (gap down)
                if curr_high < prev_low:
                    gap_size = ((prev_low - curr_high) / prev_low) * 100
                    if gap_size > 1:
                        fvg_bearish.append((curr_high, prev_low, gap_size))
            
            if fvg_bullish:
                biggest = max(fvg_bullish, key=lambda x: x[2])
                smc_signals.append(f"📈 Bullish FVG: ${biggest[0]:.2f}-${biggest[1]:.2f} ({biggest[2]:.1f}%)")
                score += 10
            
            if fvg_bearish:
                biggest = max(fvg_bearish, key=lambda x: x[2])
                smc_signals.append(f"📉 Bearish FVG: ${biggest[0]:.2f}-${biggest[1]:.2f} ({biggest[2]:.1f}%)")
                score += 10
            
            # 3. MARKET STRUCTURE BREAK (MSB)
            # Break of previous swing high/low
            swing_high = max(highs[-10:-3])
            swing_low = min(lows[-10:-3])
            
            msb_bullish = price > swing_high
            msb_bearish = price < swing_low
            
            if msb_bullish:
                smc_signals.append(f"🔨 Bullish MSB: Broke ${swing_high:.2f} swing high")
                score += 20
                notes.append("Bullish market structure break")
            elif msb_bearish:
                smc_signals.append(f"🔨 Bearish MSB: Broke ${swing_low:.2f} swing low")
                score += 20
                notes.append("Bearish market structure break")
            
            # 4. LIQUIDITY SWEEP DETECTION
            # Wick below support or above resistance
            last_candle = hist.iloc[-1]
            wick_low = last_candle['Low']
            wick_high = last_candle['High']
            
            if wick_low < swing_low * 0.99 and price > swing_low:
                smc_signals.append(f"💨 Liquidity sweep below ${swing_low:.2f} (reclaimed)")
                score += 15
                notes.append("Bullish liquidity sweep - possible reversal")
            elif wick_high > swing_high * 1.01 and price < swing_high:
                smc_signals.append(f"💨 Liquidity sweep above ${swing_high:.2f} (reclaimed)")
                score += 15
                notes.append("Bearish liquidity sweep - possible reversal")
        
        # === TRADITIONAL TREND ANALYSIS ===
        if price > sma20 > sma50:
            trend = "bullish"
            score += 15
            notes.append("Bullish trend alignment")
        elif price < sma20 < sma50:
            trend = "bearish"
            score += 15
            notes.append("Bearish trend alignment")
        else:
            trend = "mixed"
            score += 5
            notes.append("Mixed trend signals")
        
        # Distance to support/resistance
        dist_to_support = ((price - support) / price) * 100
        dist_to_resistance = ((resistance - price) / price) * 100
        
        if dist_to_support < 5:
            notes.append("Near support - bounce potential")
            score += 10
        if dist_to_resistance < 5:
            notes.append("Near resistance - breakout watch")
            score += 10
        
        return {
            "score": score,
            "trend": trend,
            "support": support,
            "resistance": resistance,
            "dist_support": dist_to_support,
            "dist_resistance": dist_to_resistance,
            "notes": notes,
            "smc_signals": smc_signals,
            "has_smc": len(smc_signals) > 0
        }
    
    def _sentiment_analysis(self, data: Dict) -> Dict:
        """Sentiment Analyst Agent"""
        score = 0
        notes = []
        catalysts = []
        
        # Short interest
        short = data.get("short_float", 0)
        if short > 0.30:
            score += 30
            catalysts.append(f"🚀 Squeeze potential: {short*100:.0f}% short")
            notes.append("Extreme short interest - squeeze watch")
        elif short > 0.20:
            score += 20
            catalysts.append(f"🔥 High short: {short*100:.0f}%")
            notes.append("Elevated short interest")
        
        # Volume
        vol_ratio = data.get("volume_ratio", 1)
        if vol_ratio > 3:
            score += 20
            catalysts.append(f"📊 Volume spike: {vol_ratio:.1f}x")
        elif vol_ratio > 2:
            score += 10
            catalysts.append(f"📈 Above avg volume: {vol_ratio:.1f}x")
        
        # IV
        iv_rank = data.get("iv_rank", 50)
        if iv_rank > 80:
            score += 15
            catalysts.append(f"⚡ High IV: {iv_rank:.0f}%")
            notes.append("Expensive options - event expected")
        
        # Analyst consensus divergence
        rec = data.get("recommendation", "none")
        upside = data.get("upside", 0)
        
        if rec in ["buy", "strong_buy"] and upside > 30:
            catalysts.append(f"🎯 Analysts see {upside:.0f}% upside")
        elif rec in ["sell", "strong_sell"]:
            catalysts.append(f"⚠️ Analysts bearish")
        
        return {
            "score": score,
            "short_interest": short,
            "volume_ratio": vol_ratio,
            "iv_rank": iv_rank,
            "unusual_flow": vol_ratio > 2 or short > 0.20,
            "catalysts": catalysts,
            "notes": notes
        }
    
    def _research_debate(self, data: Dict, fund: Dict, tech: Dict, sent: Dict) -> Dict:
        """Research Team - Bull vs Bear debate"""
        
        price = data["price"]
        target = data.get("target_price", price)
        upside = ((target - price) / price) * 100
        
        # Build bull case
        bull_case = []
        if tech["trend"] == "bullish":
            bull_case.append("Technical trend is bullish")
        if sent["short_interest"] > 0.20:
            bull_case.append(f"Short squeeze potential ({sent['short_interest']*100:.0f}% short)")
        if upside > 20:
            bull_case.append(f"Analysts see {upside:.0f}% upside to ${target:.2f}")
        if fund["score"] > 25:
            bull_case.append("Strong fundamental metrics")
        
        # Build bear case
        bear_case = []
        if tech["trend"] == "bearish":
            bear_case.append("Technical trend is bearish")
        if data.get("change_pct", 0) < -5:
            bear_case.append(f"Down {abs(data['change_pct']):.1f}% today - momentum negative")
        if data.get("pe_ratio", 0) > 100 or data.get("pe_ratio", 0) < 0:
            bear_case.append("Unfavorable valuation metrics")
        if sent["iv_rank"] > 80:
            bear_case.append("High IV suggests event risk")
        
        # Determine recommendation
        bull_score = len(bull_case) * 10 + fund["score"] * 0.3
        bear_score = len(bear_case) * 10 + (100 - sent["score"]) * 0.3
        
        if bull_score > bear_score + 15:
            recommendation = "BULLISH"
            conviction = min(0.9, 0.5 + (bull_score - bear_score) / 100)
        elif bear_score > bull_score + 15:
            recommendation = "BEARISH"
            conviction = min(0.9, 0.5 + (bear_score - bull_score) / 100)
        else:
            recommendation = "NEUTRAL"
            conviction = 0.5
        
        return {
            "recommendation": recommendation,
            "conviction": conviction,
            "bull_case": bull_case,
            "bear_case": bear_case,
            "upside_potential": upside,
            "debate_score": bull_score - bear_score
        }
    
    def _risk_assessment(self, data: Dict) -> Dict:
        """Risk Manager Agent"""
        
        vol = data.get("volatility", 0.3)
        iv_rank = data.get("iv_rank", 50)
        price = data["price"]
        
        # Determine risk level
        if vol > 0.6 or iv_rank > 80:
            risk_level = "HIGH"
            max_position = 2  # Contracts
        elif vol > 0.4 or iv_rank > 60:
            risk_level = "MEDIUM"
            max_position = 3
        else:
            risk_level = "LOW"
            max_position = 5
        
        # Expected move for position sizing
        expected_move = data.get("expected_move_pct", 5)
        
        return {
            "level": risk_level,
            "max_position": max_position,
            "volatility": vol,
            "expected_move_pct": expected_move,
            "portfolio_impact": "Small" if max_position <= 2 else "Medium"
        }

class SignalConstructor:
    """Constructs final trade signals from all analysis"""
    
    def construct_signal(self, analysis: Dict) -> Optional[ComprehensiveSignal]:
        """Build complete signal from all agent outputs"""
        
        data = analysis["data"]
        fund = analysis["fundamental"]
        tech = analysis["technical"]
        sent = analysis["sentiment"]
        research = analysis["research"]
        risk = analysis["risk"]
        
        price = data["price"]
        
        # Determine direction from research + technical
        if research["recommendation"] == "BULLISH" and tech["trend"] != "bearish":
            direction = "CALL"
        elif research["recommendation"] == "BEARISH" and tech["trend"] != "bullish":
            direction = "PUT"
        else:
            # Mixed signals - skip
            return None
        
        # Determine strategy based on IV and risk
        iv_rank = sent["iv_rank"]
        if iv_rank > 75 or risk["level"] == "HIGH":
            strategy = "Day_Trade"
            dte = 0
            stop_pct = 0.015
        else:
            strategy = "Swing"
            dte = 7
            stop_pct = 0.03
        
        # Calculate levels
        if direction == "CALL":
            strike = round(price * 1.02, 1)
            stop = price * (1 - stop_pct)
            target_1 = price * 1.03
            target_2 = price * 1.06
        else:
            strike = round(price * 0.98, 1)
            stop = price * (1 + stop_pct)
            target_1 = price * 0.97
            target_2 = price * 0.94
        
        # Calculate Greeks
        try:
            t = max(1, dte) / 365
            premium = price * 0.05
            greeks_dict = {
                "delta": 0.5 if direction == "CALL" else -0.5,
                "gamma": 0.05,
                "theta": -premium / 30,
                "vega": premium * 0.1,
                "iv": f"{data['iv']*100:.0f}%"
            }
        except:
            greeks_dict = {"delta": 0, "gamma": 0, "theta": 0, "vega": 0, "iv": "N/A"}
        
        risk_amt = abs(price - stop)
        reward_amt = abs(target_2 - price)
        rr = round(reward_amt / risk_amt, 1) if risk_amt > 0 else 2
        
        # Calculate BIG MOVE POTENTIAL
        move_score = 0
        move_catalysts = []
        
        # Short squeeze potential
        if sent["short_interest"] > 0.25:
            move_score += 30
            move_catalysts.append(f"🔥 Squeeze potential: {sent['short_interest']*100:.0f}% short")
        elif sent["short_interest"] > 0.15:
            move_score += 15
            move_catalysts.append(f"⚡ Elevated short: {sent['short_interest']*100:.0f}%")
        
        # High IV = expected big move
        if sent["iv_rank"] > 80:
            move_score += 25
            move_catalysts.append(f"💥 High IV: {sent['iv_rank']:.0f}% rank")
        
        # Volume surge
        if sent["volume_ratio"] > 2:
            move_score += 20
            move_catalysts.append(f"📈 Volume: {sent['volume_ratio']:.1f}x avg")
        
        # Analyst divergence
        if abs(data.get("upside", 0)) > 30:
            move_score += 15
            move_catalysts.append(f"🎯 Big analyst target: {data['upside']:+.0f}%")
        
        # Technical breakout potential
        if tech["dist_resistance"] < 5 and direction == "CALL":
            move_score += 10
            move_catalysts.append("🔨 Near resistance breakout")
        elif tech["dist_support"] < 5 and direction == "PUT":
            move_score += 10
            move_catalysts.append("🔨 Near support breakdown")
        
        # Research conviction
        if research["conviction"] > 0.7:
            move_score += 10
        
        # Cap at 100
        move_score = min(100, move_score)
        
        # Final confidence
        confidence = (research["conviction"] * 0.4 + 
                     (sent["score"] / 100) * 0.3 + 
                     (tech["score"] / 100) * 0.2 +
                     (fund["score"] / 100) * 0.1)
        
        return ComprehensiveSignal(
            symbol=analysis["symbol"],
            price=price,
            
            fundamental_score=fund["score"],
            pe_ratio=fund["pe_ratio"],
            market_cap=f"${data['market_cap']/1e9:.1f}B" if data['market_cap'] else "N/A",
            sector=data.get("sector", "Unknown"),
            
            technical_score=tech["score"],
            trend=tech["trend"],
            support=tech["support"],
            resistance=tech["resistance"],
            sma_20=data["sma_20"],
            sma_50=data["sma_50"],
            smc_signals=tech.get("smc_signals", []),
            
            sentiment_score=sent["score"],
            short_interest=sent["short_interest"],
            volume_ratio=sent["volume_ratio"],
            iv_rank=sent["iv_rank"],
            put_call_ratio=data.get("put_call_ratio", 1.0),
            unusual_flow=sent["unusual_flow"],
            
            research_recommendation=research["recommendation"],
            bull_case=research["bull_case"],
            bear_case=research["bear_case"],
            conviction=research["conviction"],
            
            risk_level=risk["level"],
            max_position_size=risk["max_position"],
            portfolio_impact=risk["portfolio_impact"],
            
            direction=direction,
            strategy=strategy,
            strike=strike,
            expiration=(datetime.now() + timedelta(days=max(1, dte))).strftime("%Y-%m-%d"),
            entry=price,
            stop=round(stop, 2),
            target_1=round(target_1, 2),
            target_2=round(target_2, 2),
            expected_move_pct=data.get("expected_move_pct", 5),
            risk_reward=rr,
            confidence=confidence,
            move_potential_score=move_score,
            catalysts=move_catalysts,
            timestamp=datetime.now()
        )

class FullLiveScanner:
    """Complete orchestration of all agents"""
    
    def __init__(self):
        self.data_feed = LiveDataFeed()
        self.analyst_team = FullAnalystTeam(self.data_feed)
        self.signal_constructor = SignalConstructor()
        
        self.universe = [
            "AMC", "GME", "LCID", "SOFI", "MARA", "RIOT",  # High volatility/meme
            "AAL", "F", "NIO", "CHPT", "CLSK",              # EV/Airlines/Auto
            "INTC", "T", "VZ"                                 # Value/Tech
        ]  # OPTIMIZED: 15 stocks instead of 28
    
    async def scan(self) -> List[ComprehensiveSignal]:
        """Run complete multi-agent scan"""
        
        print("="*80)
        print("🔴 FULL MULTI-AGENT LIVE SCANNER")
        print("All Agents Working Together | Real Data | Big Move Focus")
        print("="*80)
        print(f"\nScanning {len(self.universe)} stocks through full agent pipeline...\n")
        
        # Step 1: Fetch all data
        print("📊 AGENT 1: LiveDataConnector - Fetching market data...")
        all_data = await self.data_feed.batch_fetch(self.universe)
        print(f"   ✓ Retrieved data for {len(all_data)} stocks\n")
        
        # Step 2: Run full analysis
        print("🔍 AGENT TEAM: Running all analyst agents...")
        analyses = []
        for symbol, data in all_data.items():
            analysis = await self.analyst_team.analyze(symbol, data)
            analyses.append(analysis)
        print(f"   ✓ Completed analysis for {len(analyses)} stocks")
        print(f"   ✓ Fundamental, Technical, Sentiment, Research, Risk\n")
        
        # Step 3: Construct signals
        print("🎯 AGENT: SignalConstructor - Building trade signals...")
        signals = []
        for analysis in analyses:
            signal = self.signal_constructor.construct_signal(analysis)
            if signal:
                signals.append(signal)
        print(f"   ✓ Generated {len(signals)} actionable signals\n")
        
        # Sort by move potential
        signals.sort(key=lambda x: x.move_potential_score, reverse=True)
        
        return signals

def print_comprehensive_report(signals: List[ComprehensiveSignal]):
    """Print full multi-agent report"""
    
    if not signals:
        print("\n❌ No high-confidence signals found.")
        return
    
    print("="*80)
    print("📋 COMPREHENSIVE ANALYSIS REPORT")
    print("="*80)
    
    # TOP 5 BIGGEST MOVE POTENTIAL
    print("\n" + "🏆"*40)
    print("🏆 TOP 5 STOCKS - BIGGEST MOVE POTENTIAL")
    print("🏆"*40 + "\n")
    
    for i, sig in enumerate(signals[:5], 1):
        emoji = "🟢" if sig.direction == "CALL" else "🔴"
        
        print(f"{i}. {emoji} {sig.symbol} | {sig.direction} | MOVE POTENTIAL: {sig.move_potential_score}/100")
        print(f"   Price: ${sig.price:.2f} | Sector: {sig.sector}")
        print(f"   Market Cap: {sig.market_cap} | P/E: {sig.pe_ratio:.1f}" if sig.pe_ratio > 0 else f"   Market Cap: {sig.market_cap}")
        
        # Volume info
        vol_emoji = "🔥" if sig.volume_ratio > 2 else "📈" if sig.volume_ratio > 1.5 else "📊"
        print(f"   {vol_emoji} Relative Volume: {sig.volume_ratio:.1f}x average")
        
        # Put/Call Ratio
        pcr = sig.put_call_ratio
        if pcr > 2:
            pcr_emoji = "🔴🔴🔴"
            pcr_text = "Extreme Bearish"
        elif pcr > 1.5:
            pcr_emoji = "🔴🔴"
            pcr_text = "Very Bearish"
        elif pcr > 1:
            pcr_emoji = "🔴"
            pcr_text = "Bearish"
        elif pcr > 0.7:
            pcr_emoji = "⚪"
            pcr_text = "Neutral"
        elif pcr > 0.5:
            pcr_emoji = "🟢"
            pcr_text = "Bullish"
        else:
            pcr_emoji = "🟢🟢"
            pcr_text = "Very Bullish"
        print(f"   {pcr_emoji} Put/Call Ratio: {pcr:.2f} ({pcr_text})")
        
        # Show what each agent found
        print(f"\n   📊 AGENT ANALYSIS:")
        print(f"      Fundamental Score: {sig.fundamental_score}/100")
        print(f"      Technical Score: {sig.technical_score}/100 (Trend: {sig.trend})")
        if sig.smc_signals:
            print(f"      📈 SMC Signals:")
            for smc in sig.smc_signals[:3]:
                print(f"         {smc}")
        print(f"      Sentiment Score: {sig.sentiment_score}/100")
        print(f"      Research: {sig.research_recommendation} ({sig.conviction:.0%} conviction)")
        print(f"      Risk Level: {sig.risk_level} | Max Position: {sig.max_position_size} contracts")
        
        # Big move catalysts
        print(f"\n   🚀 BIG MOVE CATALYSTS:")
        for cat in sig.catalysts[:4]:
            print(f"      {cat}")
        
        # Trade setup
        print(f"\n   💰 TRADE SETUP:")
        print(f"      Strategy: {sig.strategy}")
        print(f"      Entry: ${sig.entry:.2f} | Stop: ${sig.stop:.2f}")
        print(f"      Target 1: ${sig.target_1:.2f} | Target 2: ${sig.target_2:.2f}")
        print(f"      Strike: ${sig.strike:.2f} | Exp: {sig.expiration}")
        print(f"      Expected Move: {sig.expected_move_pct:.1f}%")
        print(f"      R:R = 1:{sig.risk_reward} | Confidence: {sig.confidence:.0%}")
        
        # Bull/Bear cases
        print(f"\n   📈 BULL CASE:")
        for point in sig.bull_case[:2]:
            print(f"      + {point}")
        print(f"   📉 BEAR CASE:")
        for point in sig.bear_case[:2]:
            print(f"      - {point}")
        
        print("\n" + "-"*80 + "\n")
    
    # SUMMARY TABLE
    print("="*80)
    print("📊 QUICK REFERENCE TABLE")
    print("="*80)
    print(f"{'Rank':<5} {'Symbol':<8} {'Dir':<6} {'Move':<6} {'Vol':<6} {'P/C':<6} {'Conf':<6} {'Risk':<8}")
    print("-"*80)
    
    for i, sig in enumerate(signals[:10], 1):
        print(f"{i:<5} {sig.symbol:<8} {sig.direction:<6} {sig.move_potential_score:<6} "
              f"{sig.volume_ratio:.1f}x   {sig.put_call_ratio:.2f}  {sig.confidence:.0%}    {sig.risk_level:<8}")
    
    print("="*80)
    print(f"\nTotal Signals: {len(signals)}")
    print(f"Day Trades: {len([s for s in signals if s.strategy == 'Day_Trade'])}")
    print(f"Swings: {len([s for s in signals if s.strategy == 'Swing'])}")
    print(f"Avg Move Potential: {sum(s.move_potential_score for s in signals) // len(signals)}/100")
    print("="*80)
    
    # Save to file
    output = {
        "timestamp": datetime.now().isoformat(),
        "signals": [{
            "symbol": s.symbol,
            "price": s.price,
            "direction": s.direction,
            "move_potential": s.move_potential_score,
            "confidence": s.confidence,
            "expected_move_pct": s.expected_move_pct,
            "catalysts": s.catalysts,
            "trade": {
                "entry": s.entry,
                "stop": s.stop,
                "target": s.target_2,
                "strike": s.strike,
                "expiration": s.expiration
            }
        } for s in signals]
    }
    
    with open('/tmp/full_scan_report.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\n📁 Full report saved to: /tmp/full_scan_report.json")

async def main():
    scanner = FullLiveScanner()
    signals = await scanner.scan()
    print_comprehensive_report(signals)

if __name__ == "__main__":
    asyncio.run(main())
