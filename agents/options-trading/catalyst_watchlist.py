#!/usr/bin/env python3
"""
Catalyst-Driven Watchlist Generator
Refined under-$50 watchlist with earnings, events, flow, and scoring
"""

import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum

class CatalystType(Enum):
    EARNINGS = "earnings"
    ECONOMIC = "economic"
    FLOW = "unusual_flow"
    SHORT_SQUEEZE = "short_squeeze"
    TECHNICAL = "technical_breakout"
    SECTOR_ROTATION = "sector_rotation"
    NEWS = "news_event"

@dataclass
class Catalyst:
    type: CatalystType
    description: str
    impact: str  # high, medium, low
    timing: str  # today, tomorrow, this_week
    direction: str  # bullish, bearish, neutral

@dataclass
class ScoredWatchlistItem:
    symbol: str
    price: float
    setup_type: str
    direction: str
    key_level: float
    trigger: str
    stop: float
    target: float
    risk_reward: float
    confidence: str
    catalysts: List[Catalyst] = field(default_factory=list)
    option_liquidity: str = "medium"
    
    # Scoring
    catalyst_score: int = 0  # 0-100
    technical_score: int = 0
    flow_score: int = 0
    total_score: int = 0
    
    def to_dict(self):
        return {
            "symbol": self.symbol,
            "price": f"${self.price:.2f}",
            "direction": self.direction.upper(),
            "score": self.total_score,
            "catalysts": [f"{c.type.value}: {c.description}" for c in self.catalysts],
            "trigger": self.trigger
        }

class CatalystEngine:
    """Detects and scores catalysts for under-$50 stocks"""
    
    def __init__(self):
        self.today = datetime.now()
        self.economic_calendar = self._load_economic_calendar()
        self.earnings_calendar = self._load_earnings_calendar()
        
    def _load_economic_calendar(self) -> List[Dict]:
        """Load this week's economic events"""
        return [
            {"date": "2025-02-24", "event": "Fed Speaker", "impact": "medium", "time": "10:00 AM"},
            {"date": "2025-02-25", "event": "Consumer Confidence", "impact": "medium", "time": "10:00 AM"},
            {"date": "2025-02-26", "event": "New Home Sales", "impact": "low", "time": "10:00 AM"},
            {"date": "2025-02-27", "event": "GDP Revision", "impact": "high", "time": "8:30 AM"},
            {"date": "2025-02-28", "event": "PCE Inflation", "impact": "high", "time": "8:30 AM"},
        ]
    
    def _load_earnings_calendar(self) -> Dict[str, Dict]:
        """Load earnings for under-$50 stocks"""
        return {
            # This week's earnings
            "M": {"date": "2025-02-25", "time": "Pre", "expected_move": 8.5},
            "AMC": {"date": "2025-02-27", "time": "Post", "expected_move": 12.0},
            "F": {"date": "2025-02-26", "time": "Post", "expected_move": 4.5},
            "SOFI": {"date": "2025-02-25", "time": "Post", "expected_move": 9.2},
            "LCID": {"date": "2025-02-27", "time": "Post", "expected_move": 11.5},
            "NKLA": {"date": "2025-02-24", "time": "Post", "expected_move": 15.0},
            "RIVN": {"date": "2025-02-26", "time": "Post", "expected_move": 10.8},
            "AAL": {"date": "2025-02-28", "time": "Pre", "expected_move": 6.2},
            "NIO": {"date": "2025-03-01", "time": "Pre", "expected_move": 8.5},
            "INTC": {"date": "2025-02-28", "time": "Post", "expected_move": 5.5},
        }
    
    def detect_catalysts(self, symbol: str, stock_data: Dict) -> List[Catalyst]:
        """Detect all catalysts for a stock"""
        catalysts = []
        
        # Check earnings
        earnings_catalyst = self._check_earnings(symbol)
        if earnings_catalyst:
            catalysts.append(earnings_catalyst)
        
        # Check unusual flow
        flow_catalyst = self._check_options_flow(symbol)
        if flow_catalyst:
            catalysts.append(flow_catalyst)
        
        # Check short squeeze potential
        squeeze_catalyst = self._check_short_squeeze(symbol, stock_data)
        if squeeze_catalyst:
            catalysts.append(squeeze_catalyst)
        
        # Check sector rotation
        sector_catalyst = self._check_sector_rotation(symbol, stock_data)
        if sector_catalyst:
            catalysts.append(sector_catalyst)
        
        # Check technical breakout
        technical_catalyst = self._check_technical_setup(symbol, stock_data)
        if technical_catalyst:
            catalysts.append(technical_catalyst)
        
        return catalysts
    
    def _check_earnings(self, symbol: str) -> Optional[Catalyst]:
        """Check if stock has upcoming earnings"""
        if symbol not in self.earnings_calendar:
            return None
        
        earnings = self.earnings_calendar[symbol]
        earnings_date = datetime.strptime(earnings["date"], "%Y-%m-%d")
        days_until = (earnings_date - self.today).days
        
        if days_until < 0:
            return None  # Already reported
        
        if days_until == 0:
            timing = "today"
            impact = "high"
        elif days_until <= 2:
            timing = "tomorrow"
            impact = "high"
        elif days_until <= 5:
            timing = "this_week"
            impact = "medium"
        else:
            return None
        
        return Catalyst(
            type=CatalystType.EARNINGS,
            description=f"Earnings {earnings['time']} ({earnings['expected_move']}% expected move)",
            impact=impact,
            timing=timing,
            direction="neutral"  # Could go either way
        )
    
    def _check_options_flow(self, symbol: str) -> Optional[Catalyst]:
        """Check for unusual options flow"""
        # Simulate flow detection
        flow_probability = random.random()
        
        if flow_probability < 0.15:  # 15% chance of unusual flow
            volume_ratio = random.randint(200, 500)
            direction = random.choice(["bullish", "bearish"])
            
            return Catalyst(
                type=CatalystType.FLOW,
                description=f"Unusual {direction} flow ({volume_ratio}% of avg volume)",
                impact="high" if volume_ratio > 300 else "medium",
                timing="today",
                direction=direction
            )
        return None
    
    def _check_short_squeeze(self, symbol: str, stock_data: Dict) -> Optional[Catalyst]:
        """Check short squeeze potential"""
        # High short interest stocks under $50
        squeeze_candidates = ["AMC", "GME", "LCID", "NKLA", "RIVN", "MARA", "RIOT"]
        
        if symbol in squeeze_candidates:
            short_interest = random.randint(15, 45)  # 15-45% short interest
            
            return Catalyst(
                type=CatalystType.SHORT_SQUEEZE,
                description=f"High short interest ({short_interest}% of float)",
                impact="high" if short_interest > 25 else "medium",
                timing="this_week",
                direction="bullish"
            )
        return None
    
    def _check_sector_rotation(self, symbol: str, stock_data: Dict) -> Optional[Catalyst]:
        """Check for sector rotation signals"""
        sector_trends = {
            "EV": random.choice(["bullish", "bearish"]),
            "CRYPTO": random.choice(["bullish", "bearish"]),
            "BANK": random.choice(["bullish", "bearish"]),
            "MEME": random.choice(["bullish", "bearish"]),
            "AIRLINE": random.choice(["bullish", "bearish"]),
        }
        
        stock_sector = stock_data.get("type", "")
        if stock_sector in sector_trends:
            trend = sector_trends[stock_sector]
            strength = random.randint(60, 95)
            
            return Catalyst(
                type=CatalystType.SECTOR_ROTATION,
                description=f"{stock_sector} sector showing {trend} momentum ({strength}% strength)",
                impact="medium",
                timing="today",
                direction=trend
            )
        return None
    
    def _check_technical_setup(self, symbol: str, stock_data: Dict) -> Optional[Catalyst]:
        """Check technical patterns"""
        patterns = [
            ("Breakout above 20-day high", "high"),
            ("Support bounce off 50 SMA", "medium"),
            ("Volume shelf building", "medium"),
            ("Consolidation tightening", "low"),
            ("Golden cross forming", "high"),
        ]
        
        if random.random() < 0.3:  # 30% have technical setup
            pattern, impact = random.choice(patterns)
            return Catalyst(
                type=CatalystType.TECHNICAL,
                description=pattern,
                impact=impact,
                timing="today",
                direction="bullish" if "Breakout" in pattern or "bounce" in pattern else "neutral"
            )
        return None
    
    def score_stock(self, symbol: str, catalysts: List[Catalyst], stock_data: Dict) -> Dict:
        """Score stock based on catalysts"""
        
        scores = {
            "catalyst": 0,
            "technical": 0,
            "flow": 0,
            "earnings": 0,
            "total": 0
        }
        
        for catalyst in catalysts:
            base_score = {"high": 30, "medium": 20, "low": 10}[catalyst.impact]
            
            if catalyst.type == CatalystType.EARNINGS:
                # Higher score if earnings very soon
                if catalyst.timing == "today":
                    scores["earnings"] += base_score + 20
                elif catalyst.timing == "tomorrow":
                    scores["earnings"] += base_score + 10
                else:
                    scores["earnings"] += base_score
                    
            elif catalyst.type == CatalystType.FLOW:
                scores["flow"] += base_score
                
            elif catalyst.type == CatalystType.SHORT_SQUEEZE:
                scores["catalyst"] += base_score
                
            elif catalyst.type == CatalystType.TECHNICAL:
                scores["technical"] += base_score
                
            elif catalyst.type == CatalystType.SECTOR_ROTATION:
                scores["catalyst"] += base_score * 0.7
        
        # IV rank bonus (higher IV = better for selling strategies)
        iv_rank = stock_data.get("iv_rank", 50)
        if iv_rank > 70:
            scores["catalyst"] += 15
        elif iv_rank > 50:
            scores["catalyst"] += 10
        
        # Under $10 bonus (higher % moves possible)
        if stock_data["price"] < 10:
            scores["catalyst"] += 10
        
        scores["total"] = sum(scores.values())
        return scores

class RefinedWatchlistBuilder:
    """Builds refined watchlist with full catalyst analysis"""
    
    def __init__(self):
        self.catalyst_engine = CatalystEngine()
        
        # STRICTLY UNDER $50 - Expanded universe
        self.universe = {
            # Under $5 (Penny stocks, high risk/reward)
            "AMC": {"price": 4.25, "type": "MEME", "iv_rank": 82, "avg_volume": 45},
            "LCID": {"price": 2.85, "type": "EV", "iv_rank": 78, "avg_volume": 28},
            "NKLA": {"price": 7.80, "type": "EV", "iv_rank": 72, "avg_volume": 12},
            "NIO": {"price": 4.75, "type": "EV", "iv_rank": 68, "avg_volume": 35},
            "OPEN": {"price": 1.95, "type": "TECH", "iv_rank": 75, "avg_volume": 22},
            
            # $5-15 (High beta, retail favorites)
            "AAL": {"price": 17.80, "type": "AIRLINE", "iv_rank": 48, "avg_volume": 32},
            "BB": {"price": 3.45, "type": "TECH", "iv_rank": 65, "avg_volume": 8},
            "CHPT": {"price": 2.15, "type": "EV", "iv_rank": 70, "avg_volume": 15},
            "CLSK": {"price": 9.80, "type": "CRYPTO", "iv_rank": 88, "avg_volume": 18},
            "F": {"price": 11.20, "type": "AUTO", "iv_rank": 42, "avg_volume": 55},
            "FSR": {"price": 0.65, "type": "EV", "iv_rank": 92, "avg_volume": 25},
            "HOOD": {"price": 18.50, "type": "FINTECH", "iv_rank": 58, "avg_volume": 20},
            "MARA": {"price": 24.30, "type": "CRYPTO", "iv_rank": 85, "avg_volume": 42},
            "MULN": {"price": 0.55, "type": "EV", "iv_rank": 95, "avg_volume": 85},
            "RIOT": {"price": 13.40, "type": "CRYPTO", "iv_rank": 82, "avg_volume": 28},
            "SNAP": {"price": 11.75, "type": "SOCIAL", "iv_rank": 62, "avg_volume": 25},
            "SOFI": {"price": 14.20, "type": "FINTECH", "iv_rank": 65, "avg_volume": 30},
            "XPEV": {"price": 15.80, "type": "EV", "iv_rank": 70, "avg_volume": 12},
            
            # $15-30 (Quality mid-caps)
            "ABNB": {"price": 135, "type": "TRAVEL", "iv_rank": 35},  # REMOVE - over $50
            "CPRX": {"price": 16.80, "type": "BIOTECH", "iv_rank": 55, "avg_volume": 5},
            "CVE": {"price": 14.50, "type": "ENERGY", "iv_rank": 48, "avg_volume": 8},
            "GME": {"price": 25.40, "type": "MEME", "iv_rank": 88, "avg_volume": 12},
            "INTC": {"price": 22.15, "type": "TECH", "iv_rank": 52, "avg_volume": 48},
            "KEY": {"price": 17.95, "type": "BANK", "iv_rank": 38, "avg_volume": 15},
            "M": {"price": 17.20, "type": "RETAIL", "iv_rank": 58, "avg_volume": 12},
            "NYCB": {"price": 13.40, "type": "BANK", "iv_rank": 72, "avg_volume": 25},
            "PARA": {"price": 12.80, "type": "MEDIA", "iv_rank": 45, "avg_volume": 10},
            "PLTR": {"price": 80, "type": "TECH", "iv_rank": 50},  # REMOVE - over $50
            "RIVN": {"price": 11.60, "type": "EV", "iv_rank": 75, "avg_volume": 35},
            "T": {"price": 22.80, "type": "TELECOM", "iv_rank": 28, "avg_volume": 32},
            "UAL": {"price": 78, "type": "AIRLINE", "iv_rank": 42},  # REMOVE - over $50
            
            # $30-50 (Stable under-$50 names)
            "AA": {"price": 35.40, "type": "MATERIALS", "iv_rank": 52, "avg_volume": 8},
            "BAC": {"price": 46.20, "type": "BANK", "iv_rank": 32, "avg_volume": 38},
            "CCL": {"price": 28.50, "type": "TRAVEL", "iv_rank": 48, "avg_volume": 28},
            "DAL": {"price": 55, "type": "AIRLINE", "iv_rank": 40},  # REMOVE - over $50
            "FCX": {"price": 45.80, "type": "MATERIALS", "iv_rank": 45, "avg_volume": 18},
            "HAL": {"price": 32.40, "type": "ENERGY", "iv_rank": 42, "avg_volume": 12},
            "HPQ": {"price": 36.20, "type": "TECH", "iv_rank": 35, "avg_volume": 15},
            "KMI": {"price": 28.90, "type": "ENERGY", "iv_rank": 32, "avg_volume": 18},
            "MPW": {"price": 4.80, "type": "REIT", "iv_rank": 68, "avg_volume": 22},
            "NCLH": {"price": 26.40, "type": "TRAVEL", "iv_rank": 52, "avg_volume": 15},
            "OXY": {"price": 52, "type": "ENERGY", "iv_rank": 38},  # REMOVE - over $50
            "PBR": {"price": 14.80, "type": "ENERGY", "iv_rank": 48, "avg_volume": 25},
            "SLB": {"price": 48.50, "type": "ENERGY", "iv_rank": 40, "avg_volume": 12},
            "VZ": {"price": 42.80, "type": "TELECOM", "iv_rank": 25, "avg_volume": 22},
            "WBD": {"price": 13.60, "type": "MEDIA", "iv_rank": 55, "avg_volume": 18},
            "WFC": {"price": 58, "type": "BANK", "iv_rank": 30},  # REMOVE - over $50
            "WYNN": {"price": 98, "type": "TRAVEL", "iv_rank": 45},  # REMOVE - over $50
            "XLE": {"price": 95, "type": "ETF", "iv_rank": 35},  # REMOVE - over $50
        }
        
        # Filter STRICTLY under $50
        self.universe = {k: v for k, v in self.universe.items() if v["price"] < 50}
        
    def build_watchlist(self, min_score: int = 40) -> List[ScoredWatchlistItem]:
        """Build scored and ranked watchlist"""
        
        candidates = []
        
        for symbol, data in self.universe.items():
            # Detect all catalysts
            catalysts = self.catalyst_engine.detect_catalysts(symbol, data)
            
            if not catalysts:
                continue  # Skip stocks with no catalysts
            
            # Score the stock
            scores = self.catalyst_engine.score_stock(symbol, catalysts, data)
            
            if scores["total"] < min_score:
                continue  # Skip low-scoring stocks
            
            # Generate setup based on top catalyst
            setup = self._generate_setup(symbol, data, catalysts, scores)
            
            if setup:
                candidates.append(setup)
        
        # Sort by total score descending
        candidates.sort(key=lambda x: x.total_score, reverse=True)
        
        return candidates[:12]  # Top 12 setups
    
    def _generate_setup(self, symbol: str, data: Dict, catalysts: List[Catalyst], scores: Dict) -> Optional[ScoredWatchlistItem]:
        """Generate trade setup based on catalysts"""
        
        price = data["price"]
        
        # Determine direction from catalysts
        bullish_signals = sum(1 for c in catalysts if c.direction == "bullish")
        bearish_signals = sum(1 for c in catalysts if c.direction == "bearish")
        
        if bullish_signals > bearish_signals:
            direction = "call"
        elif bearish_signals > bullish_signals:
            direction = "put"
        else:
            direction = random.choice(["call", "put"])
        
        # Determine setup type
        has_earnings = any(c.type == CatalystType.EARNINGS for c in catalysts)
        has_flow = any(c.type == CatalystType.FLOW for c in catalysts)
        has_squeeze = any(c.type == CatalystType.SHORT_SQUEEZE for c in catalysts)
        
        if has_earnings:
            setup_type = "Earnings_Play"
            # Tighter stop for earnings
            stop_pct = 0.03 if direction == "call" else 0.03
            target_pct = 0.08
        elif has_squeeze:
            setup_type = "Short_Squeeze"
            stop_pct = 0.04
            target_pct = 0.12
        elif has_flow:
            setup_type = "Flow_Follow"
            stop_pct = 0.025
            target_pct = 0.06
        else:
            setup_type = "Catalyst_Driven"
            stop_pct = 0.03
            target_pct = 0.08
        
        # Calculate levels
        if direction == "call":
            key_level = round(price * 1.02, 2)
            stop = round(price * (1 - stop_pct), 2)
            target = round(price * (1 + target_pct), 2)
        else:
            key_level = round(price * 0.98, 2)
            stop = round(price * (1 + stop_pct), 2)
            target = round(price * (1 - target_pct), 2)
        
        risk = abs(price - stop)
        reward = abs(target - price)
        rr = round(reward / risk, 1) if risk > 0 else 2
        
        # Determine confidence
        if scores["total"] >= 80:
            confidence = "high"
        elif scores["total"] >= 60:
            confidence = "medium"
        else:
            confidence = "low"
        
        # Liquidity based on avg volume
        avg_vol = data.get("avg_volume", 10)
        if avg_vol > 30:
            liquidity = "high"
        elif avg_vol > 10:
            liquidity = "medium"
        else:
            liquidity = "low"
        
        # Generate trigger description
        trigger = self._generate_trigger(catalysts, direction, key_level)
        
        return ScoredWatchlistItem(
            symbol=symbol,
            price=price,
            setup_type=setup_type,
            direction=direction,
            key_level=key_level,
            trigger=trigger,
            stop=stop,
            target=target,
            risk_reward=rr,
            confidence=confidence,
            catalysts=catalysts,
            option_liquidity=liquidity,
            catalyst_score=scores["catalyst"],
            technical_score=scores["technical"],
            flow_score=scores["flow"],
            total_score=scores["total"]
        )
    
    def _generate_trigger(self, catalysts: List[Catalyst], direction: str, key_level: float) -> str:
        """Generate trigger description"""
        
        # Priority: Earnings > Flow > Squeeze > Technical > Sector
        priority = [
            CatalystType.EARNINGS,
            CatalystType.FLOW,
            CatalystType.SHORT_SQUEEZE,
            CatalystType.TECHNICAL,
            CatalystType.SECTOR_ROTATION
        ]
        
        top_catalyst = None
        for cat_type in priority:
            for c in catalysts:
                if c.type == cat_type:
                    top_catalyst = c
                    break
            if top_catalyst:
                break
        
        if not top_catalyst:
            return f"{'Break above' if direction == 'call' else 'Break below'} ${key_level}"
        
        if top_catalyst.type == CatalystType.EARNINGS:
            return f"Pre-earnings momentum. {top_catalyst.description}"
        elif top_catalyst.type == CatalystType.FLOW:
            return f"Follow {top_catalyst.description.split()[1]} flow. {'Break above' if direction == 'call' else 'Break below'} ${key_level}"
        elif top_catalyst.type == CatalystType.SHORT_SQUEEZE:
            return f"Short squeeze setup. {top_catalyst.description}. Volume spike entry"
        else:
            return f"{top_catalyst.description}. {'Break above' if direction == 'call' else 'Break below'} ${key_level}"

def print_refined_watchlist(watchlist: List[ScoredWatchlistItem]):
    """Print formatted watchlist with catalyst details"""
    
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%A, %B %d")
    
    print("="*75)
    print(f"📊 CATALYST-DRIVEN WATCHLIST - {tomorrow}")
    print("STRICTLY UNDER $50 | SCORED & RANKED")
    print("="*75)
    print()
    
    # Economic events banner
    print("📅 THIS WEEK'S ECONOMIC EVENTS:")
    print("   • Mon: Fed Speaker (10:00 AM)")
    print("   • Tue: Consumer Confidence (10:00 AM)")
    print("   • Thu: GDP Revision (8:30 AM) ⚠️ HIGH IMPACT")
    print("   • Fri: PCE Inflation (8:30 AM) ⚠️ HIGH IMPACT")
    print()
    
    # Group by setup type
    by_type = {}
    for item in watchlist:
        if item.setup_type not in by_type:
            by_type[item.setup_type] = []
        by_type[item.setup_type].append(item)
    
    # Print each group
    setup_emojis = {
        "Earnings_Play": "📈",
        "Short_Squeeze": "🚀",
        "Flow_Follow": "💰",
        "Catalyst_Driven": "⚡"
    }
    
    for setup_type, items in sorted(by_type.items()):
        emoji = setup_emojis.get(setup_type, "•")
        print(f"{emoji} {setup_type.replace('_', ' ').upper()} SETUPS")
        print("-"*75)
        
        for item in items:
            direction_emoji = "🟢" if item.direction == "call" else "🔴"
            
            print(f"\n{direction_emoji} {item.symbol} @ ${item.price:.2f} | Score: {item.total_score}/100")
            print(f"   Direction: {item.direction.upper()} | Confidence: {item.confidence.upper()}")
            print(f"   Trigger: {item.trigger}")
            print(f"   Stop: ${item.stop:.2f} | Target: ${item.target:.2f} | R:R = 1:{item.risk_reward}")
            
            # Show catalysts
            print(f"   Catalysts:")
            for c in item.catalysts:
                impact_emoji = "🔥" if c.impact == "high" else "⚡" if c.impact == "medium" else "•"
                timing_emoji = "⏰" if c.timing == "today" else "📅" if c.timing == "tomorrow" else "📆"
                print(f"      {impact_emoji} {timing_emoji} {c.description}")
            
            print(f"   Option Liquidity: {item.option_liquidity}")
        
        print()
    
    # Summary
    print("="*75)
    print("SUMMARY")
    print("="*75)
    
    total = len(watchlist)
    calls = len([w for w in watchlist if w.direction == "call"])
    puts = len([w for w in watchlist if w.direction == "put"])
    earnings_plays = len([w for w in watchlist if w.setup_type == "Earnings_Play"])
    squeeze_plays = len([w for w in watchlist if w.setup_type == "Short_Squeeze"])
    
    print(f"Total Setups: {total}")
    print(f"  🟢 Calls: {calls} | 🔴 Puts: {puts}")
    print(f"  📈 Earnings Plays: {earnings_plays}")
    print(f"  🚀 Short Squeeze: {squeeze_plays}")
    print(f"  Avg Score: {sum(w.total_score for w in watchlist) // total}/100")
    print()
    
    # Top 3 by score
    top_3 = sorted(watchlist, key=lambda x: x.total_score, reverse=True)[:3]
    print("🏆 TOP 3 SETUPS:")
    for i, item in enumerate(top_3, 1):
        print(f"   {i}. {item.symbol} ({item.direction.upper()}) - Score: {item.total_score}")
    print()
    
    print("="*75)
    print("⚠️  RISK MANAGEMENT:")
    print("   • Earnings plays = higher risk, size down 50%")
    print("   • Short squeezes = volatile, use mental stops")
    print("   • Flow followers = jump in quick, don't chase")
    print("   • Never risk more than 2% of account per trade")
    print("="*75)
    print()

def main():
    builder = RefinedWatchlistBuilder()
    watchlist = builder.build_watchlist(min_score=35)
    
    if not watchlist:
        print("No high-scoring setups found today.")
        print("Try lowering min_score threshold.")
        return
    
    print_refined_watchlist(watchlist)

if __name__ == "__main__":
    main()
