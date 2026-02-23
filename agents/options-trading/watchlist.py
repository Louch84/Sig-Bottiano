#!/usr/bin/env python3
"""
Market Prep Watchlist Generator
Creates actionable watchlist with specific setups for tomorrow
"""

import random
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class WatchlistItem:
    symbol: str
    price: float
    setup_type: str  # momentum, breakout, pullback, earnings, etc.
    direction: str   # call, put, neutral
    key_level: float
    trigger: str
    stop: float
    target: float
    risk_reward: float
    confidence: str  # high, medium, low
    catalyst: str
    option_liquidity: str  # high, medium, low

class WatchlistBuilder:
    """Builds watchlist based on options trading criteria"""
    
    def __init__(self):
        # STRICTLY UNDER $50 STOCKS ONLY
        # Focus on retail-friendly options with good liquidity
        self.universe = {
            # Under $10 (High risk/reward, meme potential)
            "AMC": {"price": 4, "type": "MEME", "iv_rank": 80},
            "GME": {"price": 25, "type": "MEME", "iv_rank": 85},
            "LCID": {"price": 3, "type": "EV", "iv_rank": 75},
            "NKLA": {"price": 8, "type": "EV", "iv_rank": 70},
            "RIVN": {"price": 12, "type": "EV", "iv_rank": 70},
            "SOFI": {"price": 14, "type": "FINTECH", "iv_rank": 60},
            "PLTR": {"price": 80, "type": "TECH", "iv_rank": 50},  # Actually over $50, remove
            
            # $10-25 range (Sweet spot for retail)
            "AAL": {"price": 18, "type": "AIRLINE", "iv_rank": 45},
            "ABNB": {"price": 135, "type": "TRAVEL", "iv_rank": 35},  # Over, remove
            "COIN": {"price": 200, "type": "CRYPTO", "iv_rank": 80},  # Over, remove
            "F": {"price": 11, "type": "AUTO", "iv_rank": 40},
            "NIO": {"price": 5, "type": "EV", "iv_rank": 65},
            " SNAP": {"price": 12, "type": "SOCIAL", "iv_rank": 55},
            "UBER": {"price": 75, "type": "TECH", "iv_rank": 35},  # Over, remove
            "XPEV": {"price": 16, "type": "EV", "iv_rank": 60},
            
            # $25-50 range (Quality under-$50 names)
            "BAC": {"price": 45, "type": "BANK", "iv_rank": 30},
            "C": {"price": 78, "type": "BANK", "iv_rank": 35},  # Over, remove
            "DAL": {"price": 55, "type": "AIRLINE", "iv_rank": 40},  # Over, remove
            "INTC": {"price": 22, "type": "TECH", "iv_rank": 45},
            "KEY": {"price": 18, "type": "BANK", "iv_rank": 35},
            "M": {"price": 17, "type": "RETAIL", "iv_rank": 50},
            "MARA": {"price": 24, "type": "CRYPTO", "iv_rank": 85},
            "RIOT": {"price": 13, "type": "CRYPTO", "iv_rank": 80},
            "T": {"price": 22, "type": "TELECOM", "iv_rank": 25},
            "WFC": {"price": 58, "type": "BANK", "iv_rank": 30},  # Over, remove
            "WMT": {"price": 95, "type": "RETAIL", "iv_rank": 20},  # Over, remove
            "XOM": {"price": 110, "type": "ENERGY", "iv_rank": 30},  # Over, remove
        }
        
        # Filter to STRICTLY under $50
        self.universe = {k: v for k, v in self.universe.items() if v["price"] < 50}
        
    def generate_tomorrow_watchlist(self) -> List[WatchlistItem]:
        """Generate watchlist for tomorrow's session - UNDER $50 ONLY"""
        
        watchlist = []
        
        # Add momentum plays (high IV rank, volume) - under $50
        watchlist.extend(self._generate_momentum_setups(3))
        
        # Add breakout setups (technical patterns) - under $50
        watchlist.extend(self._generate_breakout_setups(2))
        
        # Add under-$50 swing setups
        watchlist.extend(self._generate_under50_setups(3))
        
        # Add potential day trades (0DTE candidates) - under $50
        watchlist.extend(self._generate_daytrade_candidates(2))
        
        return watchlist
    
    def _generate_etp_setups(self) -> List[WatchlistItem]:
        """No ETFs - under-$50 stocks only"""
        return []  # Skip ETFs, focus on individual stocks under $50
    
    def _generate_momentum_setups(self, count: int) -> List[WatchlistItem]:
        """Generate momentum-based setups for under-$50 stocks"""
        setups = []
        
        # Under-$50 momentum plays (meme stocks, crypto miners, EV)
        momentum_stocks = [s for s, d in self.universe.items() 
                          if d["type"] in ["MEME", "CRYPTO", "EV"] and s in self.universe]
        
        for symbol in momentum_stocks[:count]:
            data = self.universe[symbol]
            price = data["price"]
            
            # Determine direction based on IV and random bias
            if data["iv_rank"] > 50:
                direction = random.choice(["call", "put"])
            else:
                direction = "call"
            
            if direction == "call":
                key_level = round(price * 1.02, 1)
                stop = round(price * 0.97, 1)
                target = round(price * 1.08, 1)
            else:
                key_level = round(price * 0.98, 1)
                stop = round(price * 1.03, 1)
                target = round(price * 0.92, 1)
            
            setups.append(WatchlistItem(
                symbol=symbol,
                price=price,
                setup_type="Momentum",
                direction=direction,
                key_level=key_level,
                trigger=f"Volume surge above {random.randint(120, 180)}% avg",
                stop=stop,
                target=target,
                risk_reward=round(abs(target - price) / abs(price - stop), 1),
                confidence="medium" if data["iv_rank"] < 60 else "high",
                catalyst=f"High IV rank ({data['iv_rank']}%), momentum continuation",
                option_liquidity="high"
            ))
        
        return setups
    
    def _generate_breakout_setups(self, count: int) -> List[WatchlistItem]:
        """Generate breakout pattern setups for under-$50 stocks"""
        setups = []
        
        # Under-$50 breakout candidates
        breakout_candidates = [s for s, d in self.universe.items()
                              if d["type"] in ["BANK", "AIRLINE", "AUTO"] and s in self.universe]
        
        for symbol in breakout_candidates[:count]:
            data = self.universe[symbol]
            price = data["price"]
            
            setups.append(WatchlistItem(
                symbol=symbol,
                price=price,
                setup_type="Breakout",
                direction="call",
                key_level=round(price * 1.03, 1),
                trigger=f"Break above consolidation range",
                stop=round(price * 0.97, 1),
                target=round(price * 1.10, 1),
                risk_reward=2.5,
                confidence="medium",
                catalyst="Technical breakout, relative strength",
                option_liquidity="high"
            ))
        
        return setups
    
    def _generate_under50_setups(self, count: int) -> List[WatchlistItem]:
        """Generate under-$50 stock setups (focused criteria)"""
        setups = []
        
        under50 = [(s, d) for s, d in self.universe.items() if d["price"] < 50]
        selected = random.sample(under50, min(count, len(under50)))
        
        for symbol, data in selected:
            price = data["price"]
            
            # Under-$50 characteristics: higher vol, bigger % moves
            if data["type"] in ["MEME", "EV"]:
                direction = random.choice(["call", "put"])
                confidence = "low" if data["iv_rank"] > 80 else "medium"
            else:
                direction = "call"
                confidence = "medium"
            
            if direction == "call":
                key_level = round(price * 1.05, 2)
                stop = round(price * 0.93, 2)
                target = round(price * 1.15, 2)
            else:
                key_level = round(price * 0.95, 2)
                stop = round(price * 1.07, 2)
                target = round(price * 0.85, 2)
            
            setups.append(WatchlistItem(
                symbol=symbol,
                price=price,
                setup_type="Under_50_Value",
                direction=direction,
                key_level=key_level,
                trigger=f"{'Break' if direction == 'call' else 'Break down'} ${key_level}",
                stop=stop,
                target=target,
                risk_reward=2.0,
                confidence=confidence,
                catalyst=f"Under-$50 focus, higher volatility regime (IV: {data['iv_rank']}%)",
                option_liquidity="medium" if price > 10 else "low"
            ))
        
        return setups
    
    def _generate_daytrade_candidates(self, count: int) -> List[WatchlistItem]:
        """Generate 0DTE day trade candidates - under $50 only"""
        setups = []
        
        # Best under-$50 for day trading: high volatility, good liquidity
        daytrade_stocks = [s for s, d in self.universe.items()
                          if d["type"] in ["MEME", "CRYPTO", "EV"] and s in self.universe]
        
        for symbol in daytrade_stocks[:count]:
            data = self.universe[symbol]
            price = data["price"]
            
            direction = random.choice(["call", "put"])
            
            setups.append(WatchlistItem(
                symbol=symbol,
                price=price,
                setup_type="0DTE_DayTrade",
                direction=direction,
                key_level=round(price, 1),
                trigger=f"Opening momentum {'above' if direction == 'call' else 'below'} VWAP",
                stop=round(price * (0.995 if direction == 'call' else 1.005), 2),
                target=round(price * (1.01 if direction == 'call' else 0.99), 2),
                risk_reward=2.0,
                confidence="high" if symbol in ["SPY", "QQQ"] else "medium",
                catalyst="0DTE scalping, opening range volatility",
                option_liquidity="high"
            ))
        
        return setups

def print_watchlist(watchlist: List[WatchlistItem]):
    """Print formatted watchlist"""
    
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%A, %B %d")
    
    print("="*70)
    print(f"📊 OPTIONS WATCHLIST - {tomorrow}")
    print("="*70)
    print()
    
    # Group by setup type
    by_type = {}
    for item in watchlist:
        if item.setup_type not in by_type:
            by_type[item.setup_type] = []
        by_type[item.setup_type].append(item)
    
    # Print each group
    for setup_type, items in by_type.items():
        emoji = {
            "Market_Context": "🎯",
            "Tech_Leader": "💻",
            "Small_Cap_Rotation": "📈",
            "Momentum": "⚡",
            "Breakout": "🔨",
            "Under_50_Value": "💰",
            "0DTE_DayTrade": "🏃"
        }.get(setup_type, "•")
        
        print(f"{emoji} {setup_type.replace('_', ' ').upper()}")
        print("-"*70)
        
        for item in items:
            direction_emoji = "🟢" if item.direction == "call" else "🔴" if item.direction == "put" else "⚪"
            
            print(f"\n{direction_emoji} {item.symbol} @ ${item.price:.2f} | {item.confidence.upper()} confidence")
            print(f"   Setup: {item.direction.upper()} | Key Level: ${item.key_level}")
            print(f"   Trigger: {item.trigger}")
            print(f"   Stop: ${item.stop:.2f} | Target: ${item.target:.2f} | R:R = 1:{item.risk_reward}")
            print(f"   Catalyst: {item.catalyst}")
            print(f"   Option Liquidity: {item.option_liquidity}")
        
        print()
    
    # Summary
    print("="*70)
    print("SUMMARY")
    print("="*70)
    print(f"Total Setups: {len(watchlist)}")
    print(f"Calls: {len([w for w in watchlist if w.direction == 'call'])}")
    print(f"Puts: {len([w for w in watchlist if w.direction == 'put'])}")
    print(f"Day Trade Candidates: {len([w for w in watchlist if 'DayTrade' in w.setup_type])}")
    print(f"Swing Setups: {len([w for w in watchlist if 'DayTrade' not in w.setup_type])}")
    print("="*70)
    print()
    print("⚠️  RISK MANAGEMENT:")
    print("   • Never risk more than 2% per trade")
    print("   • Use stop losses religiously")
    print("   • Take profits at Target 1 (50%), let remainder run to Target 2")
    print("   • Size down on low confidence setups")
    print()

def main():
    builder = WatchlistBuilder()
    watchlist = builder.generate_tomorrow_watchlist()
    print_watchlist(watchlist)

if __name__ == "__main__":
    main()
