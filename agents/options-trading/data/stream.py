"""
Data Infrastructure
Real-time market data processing, OPRA handling, and stream management
"""

import asyncio
from typing import Dict, List, Any, Callable, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import numpy as np

class DataPriority(Enum):
    CRITICAL = 1    # Options quotes, underlying OHLCV
    HIGH = 2        # Options trades
    MEDIUM = 3      # Order book depth
    LOW = 4         # News, secondary data

@dataclass
class MarketDataEvent:
    symbol: str
    event_type: str  # quote, trade, ohlcv, greeks
    data: Dict[str, Any]
    timestamp: datetime
    priority: DataPriority
    source: str  # OPRA, exchange, etc.

class OptionsDataStream:
    """
    Handles real-time options market data streaming.
    
    OPRA (Options Price Reporting Authority) consolidates quotes and trades
    from major U.S. exchanges. 1.4M active contracts generating 3TB daily.
    """
    
    def __init__(self):
        self.handlers: Dict[str, List[Callable]] = {
            "quote": [],
            "trade": [],
            "ohlcv": [],
            "greeks_update": []
        }
        self.running = False
        self.buffer = []
        self.callbacks_registered = 0
        
    def register_handler(self, event_type: str, handler: Callable):
        """Register callback for specific event type"""
        if event_type in self.handlers:
            self.handlers[event_type].append(handler)
            self.callbacks_registered += 1
    
    async def start_stream(self, symbols: List[str]):
        """Start streaming data for specified symbols"""
        self.running = True
        
        print(f"Starting options data stream for {len(symbols)} symbols")
        print(f"Registered {self.callbacks_registered} callbacks")
        
        # In production, this connects to OPRA or broker API
        # For simulation, generate synthetic data
        while self.running:
            for symbol in symbols:
                # Generate synthetic quote
                quote = self._generate_synthetic_quote(symbol)
                await self._dispatch("quote", quote)
                
                # Occasional trade
                if np.random.random() < 0.1:
                    trade = self._generate_synthetic_trade(symbol)
                    await self._dispatch("trade", trade)
                
                # Greeks update every 5 seconds
                if np.random.random() < 0.02:
                    greeks = self._generate_synthetic_greeks(symbol)
                    await self._dispatch("greeks_update", greeks)
            
            await asyncio.sleep(1)  # 1-second tick
    
    async def _dispatch(self, event_type: str, data: Dict):
        """Dispatch event to registered handlers"""
        event = MarketDataEvent(
            symbol=data.get("symbol", "UNKNOWN"),
            event_type=event_type,
            data=data,
            timestamp=datetime.now(),
            priority=self._get_priority(event_type),
            source="OPRA"
        )
        
        for handler in self.handlers.get(event_type, []):
            try:
                await handler(event)
            except Exception as e:
                print(f"Handler error: {e}")
    
    def _get_priority(self, event_type: str) -> DataPriority:
        """Get data priority level"""
        priorities = {
            "quote": DataPriority.CRITICAL,
            "ohlcv": DataPriority.CRITICAL,
            "trade": DataPriority.HIGH,
            "greeks_update": DataPriority.HIGH,
            "order_book": DataPriority.MEDIUM
        }
        return priorities.get(event_type, DataPriority.LOW)
    
    def _generate_synthetic_quote(self, symbol: str) -> Dict:
        """Generate synthetic options quote"""
        base_price = np.random.uniform(20, 50)
        strike = round(base_price * np.random.uniform(0.9, 1.1), 1)
        
        return {
            "symbol": symbol,
            "option_symbol": f"{symbol}{strike}C",
            "strike": strike,
            "expiration": "2025-03-21",
            "bid": np.random.uniform(0.5, 3.0),
            "ask": np.random.uniform(0.6, 3.5),
            "bid_size": np.random.randint(1, 50),
            "ask_size": np.random.randint(1, 50),
            "underlying_price": base_price,
            "iv": np.random.uniform(0.25, 0.50)
        }
    
    def _generate_synthetic_trade(self, symbol: str) -> Dict:
        """Generate synthetic trade"""
        return {
            "symbol": symbol,
            "option_symbol": f"{symbol}50C",
            "price": np.random.uniform(1.0, 3.0),
            "size": np.random.randint(1, 100),
            "exchange": np.random.choice(["CBOE", "NYSE", "NASDAQ"]),
            "conditions": np.random.choice(["", " Sweep", " Multi"])
        }
    
    def _generate_synthetic_greeks(self, symbol: str) -> Dict:
        """Generate synthetic Greeks update"""
        return {
            "symbol": symbol,
            "option_symbol": f"{symbol}50C",
            "delta": np.random.uniform(0.30, 0.50),
            "gamma": np.random.uniform(0.03, 0.08),
            "theta": np.random.uniform(-0.15, -0.05),
            "vega": np.random.uniform(0.05, 0.12),
            "rho": np.random.uniform(0.01, 0.03),
            "implied_vol": np.random.uniform(0.25, 0.50)
        }
    
    def stop(self):
        """Stop the data stream"""
        self.running = False

class GreeksAggregator:
    """
    Real-time portfolio Greeks aggregation and monitoring.
    
    Monitors:
    - Net Delta (±50% portfolio limit)
    - Portfolio Gamma (near expiration risk)
    - Theta Income (daily time decay)
    - Vega Exposure (2% per 1% vol move)
    """
    
    def __init__(self):
        self.positions: Dict[str, Dict] = {}
        self.portfolio_greeks = {
            "delta": 0,
            "gamma": 0,
            "theta": 0,
            "vega": 0
        }
        self.risk_limits = {
            "delta_pct": 0.50,
            "gamma_max": 1000,
            "vega_pct": 0.02
        }
        
    async def update_position(self, symbol: str, greeks: Dict, contracts: int):
        """Update position Greeks and recalculate portfolio"""
        
        self.positions[symbol] = {
            "greeks": greeks,
            "contracts": contracts,
            "last_update": datetime.now()
        }
        
        self._recalculate_portfolio()
    
    def _recalculate_portfolio(self):
        """Recalculate portfolio-level Greeks"""
        
        self.portfolio_greeks = {"delta": 0, "gamma": 0, "theta": 0, "vega": 0}
        
        for symbol, position in self.positions.items():
            greeks = position["greeks"]
            qty = position["contracts"]
            multiplier = 100  # Options contracts = 100 shares
            
            self.portfolio_greeks["delta"] += greeks.get("delta", 0) * qty * multiplier
            self.portfolio_greeks["gamma"] += greeks.get("gamma", 0) * qty * multiplier
            self.portfolio_greeks["theta"] += greeks.get("theta", 0) * qty * multiplier
            self.portfolio_greeks["vega"] += greeks.get("vega", 0) * qty * multiplier
    
    def check_limits(self, portfolio_value: float) -> List[Dict]:
        """Check if any risk limits are breached"""
        
        breaches = []
        
        # Delta limit
        delta_pct = abs(self.portfolio_greeks["delta"]) / portfolio_value
        if delta_pct > self.risk_limits["delta_pct"]:
            breaches.append({
                "metric": "portfolio_delta",
                "current": delta_pct,
                "limit": self.risk_limits["delta_pct"],
                "severity": "high" if delta_pct > 0.7 else "medium"
            })
        
        # Gamma warning
        if abs(self.portfolio_greeks["gamma"]) > self.risk_limits["gamma_max"]:
            breaches.append({
                "metric": "portfolio_gamma",
                "current": self.portfolio_greeks["gamma"],
                "limit": self.risk_limits["gamma_max"],
                "severity": "medium"
            })
        
        return breaches
    
    def get_aggregated_view(self) -> Dict:
        """Get aggregated portfolio view"""
        return {
            "portfolio_greeks": self.portfolio_greeks,
            "position_count": len(self.positions),
            "last_update": datetime.now().isoformat()
        }

class OrderFlowClassifier:
    """
    Classify options trades as buyer or seller initiated.
    
    Methods:
    - Lee-Ready: Tick test (trade at/above mid = buy)
    - Bulk Volume: Weight by distance from mid
    - Quote-based: Compare to prevailing bid/ask
    """
    
    @staticmethod
    def lee_ready(trade_price: float, bid: float, ask: float) -> str:
        """Lee-Ready tick test"""
        mid = (bid + ask) / 2
        
        if trade_price >= mid:
            return "buy"
        else:
            return "sell"
    
    @staticmethod
    def bulk_volume(
        trade_price: float,
        trade_size: int,
        bid: float,
        ask: float
    ) -> Dict[str, float]:
        """
        Bulk Volume Classification.
        Weight by distance from mid.
        """
        mid = (bid + ask) / 2
        spread = ask - bid
        
        if spread == 0:
            return {"buy": trade_size / 2, "sell": trade_size / 2}
        
        # Distance from mid normalized by spread
        distance = (trade_price - mid) / (spread / 2)
        distance = max(-1, min(1, distance))  # Clamp to [-1, 1]
        
        buy_weight = (distance + 1) / 2
        sell_weight = 1 - buy_weight
        
        return {
            "buy": trade_size * buy_weight,
            "sell": trade_size * sell_weight,
            "buy_pct": buy_weight * 100
        }
    
    @staticmethod
    def quote_based(
        trade_price: float,
        bid: float,
        ask: float
    ) -> str:
        """Quote-based classification"""
        if trade_price >= ask:
            return "aggressive_buy"
        elif trade_price <= bid:
            return "aggressive_sell"
        else:
            return "mid_market"
    
    def detect_sweep(self, trades: List[Dict]) -> Optional[Dict]:
        """
        Detect sweep trades (rapid execution across multiple exchanges).
        Indicates institutional urgency and conviction.
        """
        if len(trades) < 3:
            return None
        
        # Check for rapid multi-exchange execution
        timespan = (trades[-1]["timestamp"] - trades[0]["timestamp"]).total_seconds()
        exchanges = set(t["exchange"] for t in trades)
        
        if timespan < 1.0 and len(exchanges) >= 2:
            total_contracts = sum(t["size"] for t in trades)
            
            return {
                "is_sweep": True,
                "sweep_count": len(trades),
                "exchanges": list(exchanges),
                "total_contracts": total_contracts,
                "urgency_score": min(1.0, total_contracts / 1000),
                "direction": self.lee_ready(
                    trades[0]["price"],
                    trades[0]["bid"],
                    trades[0]["ask"]
                )
            }
        
        return None
    
    def calculate_imbalance(
        self,
        trades: List[Dict],
        method: str = "lee_ready"
    ) -> Dict:
        """Calculate buy/sell imbalance"""
        
        buy_volume = 0
        sell_volume = 0
        
        for trade in trades:
            if method == "lee_ready":
                side = self.lee_ready(trade["price"], trade["bid"], trade["ask"])
            else:
                side = self.quote_based(trade["price"], trade["bid"], trade["ask"])
            
            if side in ["buy", "aggressive_buy"]:
                buy_volume += trade["size"]
            else:
                sell_volume += trade["size"]
        
        total = buy_volume + sell_volume
        
        return {
            "buy_volume": buy_volume,
            "sell_volume": sell_volume,
            "buy_pct": (buy_volume / total * 100) if total > 0 else 50,
            "imbalance_ratio": buy_volume / sell_volume if sell_volume > 0 else float('inf'),
            "net_delta_adjusted": (buy_volume - sell_volume)  # Simplified
        }

class UnusualVolumeDetector:
    """Detect unusual options volume vs historical average"""
    
    def __init__(self, lookback_days: int = 20):
        self.lookback = lookback_days
        self.volume_history: Dict[str, List[float]] = {}
        
    def update_volume(self, symbol: str, volume: float):
        """Update volume history"""
        if symbol not in self.volume_history:
            self.volume_history[symbol] = []
        
        self.volume_history[symbol].append(volume)
        
        # Keep only lookback period
        if len(self.volume_history[symbol]) > self.lookback:
            self.volume_history[symbol].pop(0)
    
    def check_unusual(self, symbol: str, current_volume: float) -> Optional[Dict]:
        """Check if current volume is unusual (>2x average)"""
        
        history = self.volume_history.get(symbol, [])
        if len(history) < 5:  # Need minimum history
            return None
        
        avg_volume = np.mean(history)
        ratio = current_volume / avg_volume if avg_volume > 0 else 0
        
        if ratio > 2.0:
            return {
                "symbol": symbol,
                "current_volume": current_volume,
                "avg_volume": avg_volume,
                "ratio": ratio,
                "severity": "high" if ratio > 3 else "medium",
                "call_put_bias": self._determine_bias(symbol)
            }
        
        return None
    
    def _determine_bias(self, symbol: str) -> str:
        """Determine call/put bias (placeholder)"""
        return np.random.choice(["calls", "puts", "neutral"])
