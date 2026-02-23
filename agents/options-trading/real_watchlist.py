#!/usr/bin/env python3
"""
Real Catalyst Watchlist
Uses live market data for accurate earnings, flow, and scoring
"""

import asyncio
import sys
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import List, Dict, Optional

sys.path.insert(0, '/Users/sigbotti/.openclaw/workspace/agents/options-trading')

from data.real_data_connector import RealDataManager

@dataclass
class RealScoredSetup:
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
    catalysts: List[Dict] = field(default_factory=list)
    total_score: int = 0
    data_source: str = ""

class RealCatalystWatchlist:
    """Generates watchlist using real market data"""
    
    def __init__(self):
        self.data_manager = RealDataManager()
        self.universe = [
            "AMC", "GME", "LCID", "NKLA", "RIVN", "SOFI", "MARA", "RIOT",
            "AAL", "F", "SNAP", "NIO", "XPEV", "CHPT", "CLSK", "HOOD",
            "INTC", "KEY", "M", "T", "BAC", "CCL", "FCX", "KMI",
            "NCLH", "PBR", "SLB", "VZ", "WBD", "CPRX", "HAL", "MPW"
        ]
        
    async def build_watchlist(self) -> List[RealScoredSetup]:
        """Build watchlist using real data"""
        
        print("🔌 Connecting to market data...")
        await self.data_manager.connect_all()
        print("✅ Connected\n")
        
        print(f"📊 Analyzing {len(self.universe)} stocks...")
        
        candidates = []
        
        # Batch fetch quotes
        quotes = await self.data_manager.batch_quotes(self.universe)
        
        for symbol in self.universe:
            if symbol not in quotes:
                continue
            
            quote = quotes[symbol]
            price = quote.get('price', 0)
            
            # STRICT: Only under $50
            if price >= 50 or price <= 0:
                continue
            
            # Gather real catalysts
            catalysts = []
            score = 0
            
            # 1. Check earnings (high value catalyst)
            earnings = await self.data_manager.get_earnings_data(symbol)
            if earnings:
                for er in earnings[:1]:  # Next earnings only
                    er_date = er.get('date', '')
                    if er_date:
                        days_until = self._days_until(er_date)
                        if 0 <= days_until <= 5:
                            catalysts.append({
                                "type": "earnings",
                                "description": f"Earnings in {days_until} days",
                                "impact": "high",
                                "direction": "neutral"
                            })
                            score += 40 if days_until <= 2 else 25
            
            # 2. Check short interest
            short = await self.data_manager.get_short_interest(symbol)
            if short:
                spf = short.get('short_percent_float', 0)
                if spf > 0.15:  # 15% or more
                    catalysts.append({
                        "type": "short_squeeze",
                        "description": f"High short interest: {spf*100:.1f}%",
                        "impact": "high" if spf > 0.25 else "medium",
                        "direction": "bullish"
                    })
                    score += 35 if spf > 0.25 else 20
            
            # 3. Check unusual flow
            flow = await self.data_manager.get_unusual_flow(symbol)
            if flow:
                for f in flow[:1]:
                    catalysts.append({
                        "type": "flow",
                        "description": f"Unusual {f['type']} flow ({f['volume_ratio']}x OI)",
                        "impact": "high" if f['volume_ratio'] > 3 else "medium",
                        "direction": f['type']
                    })
                    score += 30 if f['volume_ratio'] > 3 else 15
            
            # 4. Volume spike check
            volume = quote.get('volume', 0)
            avg_volume = quote.get('average_volume', volume)
            if volume > avg_volume * 1.5:
                catalysts.append({
                    "type": "volume",
                    "description": f"Volume spike: {volume/avg_volume:.1f}x average",
                    "impact": "medium",
                    "direction": "neutral"
                })
                score += 10
            
            # 5. Price action catalyst
            change_pct = quote.get('change_percent', 0)
            if abs(change_pct) > 3:
                direction = "bullish" if change_pct > 0 else "bearish"
                catalysts.append({
                    "type": "momentum",
                    "description": f"Strong {direction} move: {change_pct:.1f}%",
                    "impact": "medium",
                    "direction": direction
                })
                score += 15
            
            # Need at least one catalyst and minimum score
            if not catalysts or score < 30:
                continue
            
            # Generate setup
            setup = self._create_setup(symbol, price, catalysts, score, quote)
            if setup:
                candidates.append(setup)
        
        await self.data_manager.close_all()
        
        # Sort by score
        candidates.sort(key=lambda x: x.total_score, reverse=True)
        return candidates[:10]
    
    def _days_until(self, date_str: str) -> int:
        """Calculate days until a date"""
        try:
            target = datetime.strptime(date_str, "%Y-%m-%d")
            return (target - datetime.now()).days
        except:
            return 999
    
    def _create_setup(self, symbol: str, price: float, catalysts: List[Dict], 
                     score: int, quote: Dict) -> Optional[RealScoredSetup]:
        """Create trade setup from catalysts"""
        
        # Determine direction
        bullish = sum(1 for c in catalysts if c.get('direction') == 'bullish')
        bearish = sum(1 for c in catalysts if c.get('direction') == 'bearish')
        
        if bullish > bearish:
            direction = "call"
        elif bearish > bullish:
            direction = "put"
        else:
            # Check price action
            change = quote.get('change_percent', 0)
            direction = "call" if change > 0 else "put"
        
        # Determine setup type
        has_earnings = any(c['type'] == 'earnings' for c in catalysts)
        has_squeeze = any(c['type'] == 'short_squeeze' for c in catalysts)
        has_flow = any(c['type'] == 'flow' for c in catalysts)
        
        if has_earnings:
            setup_type = "Earnings_Play"
            stop_pct = 0.03
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
            key_level = round(price * 1.01, 2)
            stop = round(price * (1 - stop_pct), 2)
            target = round(price * (1 + target_pct), 2)
        else:
            key_level = round(price * 0.99, 2)
            stop = round(price * (1 + stop_pct), 2)
            target = round(price * (1 - target_pct), 2)
        
        risk = abs(price - stop)
        reward = abs(target - price)
        rr = round(reward / risk, 1) if risk > 0 else 2
        
        # Confidence
        if score >= 70:
            confidence = "high"
        elif score >= 50:
            confidence = "medium"
        else:
            confidence = "low"
        
        # Generate trigger
        primary = catalysts[0]
        trigger = f"{primary['description']}. {'Break above' if direction == 'call' else 'Break below'} ${key_level}"
        
        return RealScoredSetup(
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
            total_score=score,
            data_source=quote.get('source', 'unknown')
        )

def print_real_watchlist(watchlist: List[RealScoredSetup]):
    """Print formatted watchlist"""
    
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%A, %B %d")
    
    print("="*75)
    print(f"📊 REAL CATALYST WATCHLIST - {tomorrow}")
    print("LIVE DATA | UNDER $50 ONLY")
    print("="*75)
    print()
    
    if not watchlist:
        print("❌ No high-confidence setups found with current data.")
        print("   Try again later or check API connections.")
        return
    
    # Group by setup type
    by_type = {}
    for item in watchlist:
        if item.setup_type not in by_type:
            by_type[item.setup_type] = []
        by_type[item.setup_type].append(item)
    
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
            print(f"   Data Source: {item.data_source}")
            print(f"   Direction: {item.direction.upper()} | Confidence: {item.confidence.upper()}")
            print(f"   Trigger: {item.trigger}")
            print(f"   Stop: ${item.stop:.2f} | Target: ${item.target:.2f} | R:R = 1:{item.risk_reward}")
            
            print(f"   Live Catalysts:")
            for c in item.catalysts:
                impact = "🔥" if c['impact'] == 'high' else "⚡" if c['impact'] == 'medium' else "•"
                print(f"      {impact} {c['description']}")
        
        print()
    
    # Summary
    print("="*75)
    print("SUMMARY")
    print("="*75)
    print(f"Total Setups: {len(watchlist)}")
    print(f"  🟢 Calls: {len([w for w in watchlist if w.direction == 'call'])}")
    print(f"  🔴 Puts: {len([w for w in watchlist if w.direction == 'put'])}")
    print(f"  Avg Score: {sum(w.total_score for w in watchlist) // len(watchlist)}/100")
    print()
    
    # Top pick
    if watchlist:
        top = watchlist[0]
        print(f"🏆 TOP PICK: {top.symbol} ({top.direction.upper()}) - Score: {top.total_score}")
        print(f"   {top.catalysts[0]['description']}")
    
    print()
    print("="*75)

async def main():
    print("Real Catalyst Watchlist Generator\n")
    
    # Check if APIs are configured
    builder = RealCatalystWatchlist()
    
    if not builder.data_manager.config.is_configured():
        print("⚠️  No API keys configured. Using Yahoo Finance fallback (15min delayed).\n")
        print("For real-time data, get a free Finnhub API key:")
        print("https://finnhub.io → Sign up → Copy key → Add to .env file\n")
    
    watchlist = await builder.build_watchlist()
    print_real_watchlist(watchlist)

if __name__ == "__main__":
    asyncio.run(main())
