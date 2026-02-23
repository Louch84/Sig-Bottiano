"""
Trader Agents
Execution-focused decision making with entry/exit timing and strategy selection
"""

from core import Agent, AgentRole, Message, MessageType
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import numpy as np

class StrategyType(Enum):
    COVERED_CALL = "covered_call"
    CASH_SECURED_PUT = "cash_secured_put"
    IRON_CONDOR = "iron_condor"
    CALENDAR_SPREAD = "calendar_spread"
    DEBIT_SPREAD = "debit_spread"
    PMCC = "pmcc"  # Poor Man's Covered Call
    WHEEL = "wheel"

class MarketRegime(Enum):
    HIGH_VOL = "high_volatility"  # VIX > 25
    LOW_VOL = "low_volatility"    # VIX < 15
    NORMAL = "normal"             # VIX 15-25
    EVENT_RISK = "event_risk"

@dataclass
class TradeSignal:
    symbol: str
    strategy: StrategyType
    direction: str  # "bullish", "bearish", "neutral"
    entry_price: float
    strike: float
    expiration: datetime
    contracts: int
    premium: float
    greeks: Dict[str, float]
    stop_loss: Optional[float]
    take_profit: Optional[float]
    rationale: str
    confidence: float
    timestamp: datetime

class TraderLead(Agent):
    """
    Lead trader agent responsible for:
    - Strategy selection based on market regime
    - Entry/exit timing
    - Position sizing
    - Execution coordination
    """
    
    def __init__(self):
        super().__init__("trader_lead", AgentRole.TRADER)
        self.positions = {}
        self.pending_signals = []
        self.market_regime = MarketRegime.NORMAL
        self.account_value = 100000  # Starting capital
        
    async def _reason(self, observation: str) -> str:
        """Evaluate signals and determine execution"""
        
        # Get research reports
        reports = [m for m in self.memory if m.get("msg_type") == "research_report"]
        
        # Get risk status
        risk_status = [m for m in self.memory if m.get("msg_type") == "risk_alert"]
        
        return f"""
        Trader reasoning:
        - {len(reports)} research reports available
        - Market regime: {self.market_regime.value}
        - Account value: ${self.account_value:,.2f}
        - Open positions: {len(self.positions)}
        - Risk alerts: {len(risk_status)}
        
        Next: Evaluate top signals, select strategies, calculate position sizes
        """
    
    async def _decide_action(self, reasoning: str) -> Message:
        """Generate trade signals"""
        
        # Get top research picks
        reports = [m for m in self.memory if m.get("msg_type") == "research_report"]
        if not reports:
            return None
            
        latest_report = reports[-1]
        top_pick = latest_report.get("payload", {}).get("top_pick")
        
        if not top_pick:
            return None
        
        # Generate trade signal
        signal = await self._generate_signal(top_pick)
        
        if signal:
            self.pending_signals.append(signal)
            
            return Message(
                msg_id=f"trade_{datetime.now().timestamp()}",
                sender=self.agent_id,
                recipient="risk_manager",
                msg_type=MessageType.TRADE_SIGNAL,
                payload={
                    "signal": self._signal_to_dict(signal),
                    "requires_approval": True,
                    "urgency": "normal"
                },
                priority=2
            )
        return None
    
    async def _generate_signal(self, symbol: str) -> Optional[TradeSignal]:
        """Generate trade signal for symbol"""
        
        # Determine strategy based on regime and conviction
        strategy = self._select_strategy(symbol)
        
        if not strategy:
            return None
        
        # Calculate position size
        position_size = self._calculate_position_size(strategy)
        
        # Get current price (placeholder)
        current_price = np.random.uniform(20, 50)
        
        # Strategy-specific parameters
        if strategy == StrategyType.COVERED_CALL:
            return self._build_covered_call(symbol, current_price, position_size)
        elif strategy == StrategyType.PMCC:
            return self._build_pmcc(symbol, current_price, position_size)
        elif strategy == StrategyType.IRON_CONDOR:
            return self._build_iron_condor(symbol, current_price, position_size)
        elif strategy == StrategyType.CALENDAR_SPREAD:
            return self._build_calendar_spread(symbol, current_price, position_size)
        else:
            return self._build_debit_spread(symbol, current_price, position_size)
    
    def _select_strategy(self, symbol: str) -> Optional[StrategyType]:
        """Select appropriate strategy for market regime"""
        
        if self.market_regime == MarketRegime.HIGH_VOL:
            # Favor premium buying and wide iron condors
            return np.random.choice([
                StrategyType.IRON_CONDOR,
                StrategyType.CALENDAR_SPREAD,
                StrategyType.DEBIT_SPREAD
            ], p=[0.4, 0.3, 0.3])
            
        elif self.market_regime == MarketRegime.LOW_VOL:
            # Favor calendar spreads and tight condors
            return np.random.choice([
                StrategyType.CALENDAR_SPREAD,
                StrategyType.IRON_CONDOR,
                StrategyType.COVERED_CALL
            ], p=[0.4, 0.35, 0.25])
            
        else:  # Normal regime
            # Balanced approach
            return np.random.choice([
                StrategyType.COVERED_CALL,
                StrategyType.PMCC,
                StrategyType.CASH_SECURED_PUT,
                StrategyType.IRON_CONDOR
            ], p=[0.3, 0.25, 0.25, 0.2])
    
    def _calculate_position_size(self, strategy: StrategyType) -> int:
        """Calculate number of contracts based on risk"""
        
        # Risk-based position sizing
        max_risk_per_trade = self.account_value * 0.02  # 2% max risk
        
        if strategy in [StrategyType.COVERED_CALL, StrategyType.PMCC]:
            # 100 shares per contract equivalent
            return max(1, int(max_risk_per_trade / 2000))
        else:
            # Defined risk strategies
            return max(1, int(max_risk_per_trade / 500))
    
    def _build_covered_call(self, symbol: str, price: float, size: int) -> TradeSignal:
        """Build covered call signal"""
        
        # Select strike 5-10% OTM
        otm_pct = np.random.uniform(0.05, 0.10)
        strike = round(price * (1 + otm_pct), 1)
        
        # 20-45 DTE
        days = np.random.randint(20, 46)
        expiration = datetime.now() + timedelta(days=days)
        
        # Calculate premium
        premium = price * otm_pct * 0.3  # Simplified
        
        return TradeSignal(
            symbol=symbol,
            strategy=StrategyType.COVERED_CALL,
            direction="neutral_bullish",
            entry_price=price,
            strike=strike,
            expiration=expiration,
            contracts=size,
            premium=premium * 100 * size,
            greeks={
                "delta": 0.35,
                "gamma": 0.05,
                "theta": -0.12,
                "vega": 0.08
            },
            stop_loss=price * 0.93,
            take_profit=strike,
            rationale=f"Covered call {days}DTE at ${strike} strike, collecting ${premium:.2f} premium",
            confidence=0.75,
            timestamp=datetime.now()
        )
    
    def _build_pmcc(self, symbol: str, price: float, size: int) -> TradeSignal:
        """Build Poor Man's Covered Call signal"""
        
        # Buy 70-80 delta LEAPS
        leaps_strike = round(price * 0.8, 1)
        leaps_expiration = datetime.now() + timedelta(days=365)
        
        # Sell short-dated call
        short_strike = round(price * 1.05, 1)
        short_expiration = datetime.now() + timedelta(days=30)
        
        # Net premium
        net_premium = np.random.uniform(0.5, 2.0) * 100 * size
        
        return TradeSignal(
            symbol=symbol,
            strategy=StrategyType.PMCC,
            direction="bullish",
            entry_price=price,
            strike=short_strike,
            expiration=short_expiration,
            contracts=size,
            premium=net_premium,
            greeks={
                "delta": 0.65,
                "gamma": 0.03,
                "theta": 0.08,
                "vega": 0.15
            },
            stop_loss=leaps_strike * 0.85,
            take_profit=short_strike,
            rationale=f"PMCC: LEAPS ${leaps_strike} + Short ${short_strike} call, 20-30% capital vs stock",
            confidence=0.70,
            timestamp=datetime.now()
        )
    
    def _build_iron_condor(self, symbol: str, price: float, size: int) -> TradeSignal:
        """Build iron condor signal"""
        
        # 10-20% wing widths
        wing_width = np.random.uniform(0.10, 0.20)
        
        put_short = round(price * (1 - wing_width/2), 1)
        put_long = round(put_short - price * 0.05, 1)
        call_short = round(price * (1 + wing_width/2), 1)
        call_long = round(call_short + price * 0.05, 1)
        
        expiration = datetime.now() + timedelta(days=np.random.randint(20, 45))
        
        # Credit received
        credit = np.random.uniform(0.3, 0.6) * 100 * size
        
        return TradeSignal(
            symbol=symbol,
            strategy=StrategyType.IRON_CONDOR,
            direction="neutral",
            entry_price=price,
            strike=(put_short + call_short) / 2,  # Midpoint
            expiration=expiration,
            contracts=size,
            premium=credit,
            greeks={
                "delta": 0.05,
                "gamma": -0.02,
                "theta": 0.15,
                "vega": -0.10
            },
            stop_loss=credit * 2,  # 2x credit received
            take_profit=credit * 0.5,  # 50% profit target
            rationale=f"Iron Condor: ${put_long}/${put_short} puts, ${call_short}/${call_long} calls, {wing_width*100:.0f}% wings",
            confidence=0.65,
            timestamp=datetime.now()
        )
    
    def _build_calendar_spread(self, symbol: str, price: float, size: int) -> TradeSignal:
        """Build calendar spread signal"""
        
        strike = round(price, 1)
        short_exp = datetime.now() + timedelta(days=30)
        long_exp = datetime.now() + timedelta(days=90)
        
        return TradeSignal(
            symbol=symbol,
            strategy=StrategyType.CALENDAR_SPREAD,
            direction="neutral",
            entry_price=price,
            strike=strike,
            expiration=short_exp,
            contracts=size,
            premium=np.random.uniform(0.5, 1.5) * 100 * size,
            greeks={
                "delta": 0.10,
                "gamma": 0.02,
                "theta": 0.12,
                "vega": 0.20
            },
            stop_loss=None,
            take_profit=None,
            rationale=f"Calendar spread at ${strike}: Short 30DTE, Long 90DTE, exploiting steep contango",
            confidence=0.60,
            timestamp=datetime.now()
        )
    
    def _build_debit_spread(self, symbol: str, price: float, size: int) -> TradeSignal:
        """Build debit spread signal"""
        
        direction = np.random.choice(["bullish", "bearish"])
        
        if direction == "bullish":
            long_strike = round(price, 1)
            short_strike = round(price * 1.10, 1)
        else:
            long_strike = round(price, 1)
            short_strike = round(price * 0.90, 1)
        
        expiration = datetime.now() + timedelta(days=np.random.randint(30, 60))
        
        return TradeSignal(
            symbol=symbol,
            strategy=StrategyType.DEBIT_SPREAD,
            direction=direction,
            entry_price=price,
            strike=long_strike,
            expiration=expiration,
            contracts=size,
            premium=np.random.uniform(1.0, 3.0) * 100 * size,
            greeks={
                "delta": 0.40 if direction == "bullish" else -0.40,
                "gamma": 0.04,
                "theta": -0.08,
                "vega": 0.10
            },
            stop_loss=premium * 0.5,
            take_profit=short_strike,
            rationale=f"{direction.title()} debit spread: ${long_strike}/${short_strike}, defined risk/reward",
            confidence=0.68,
            timestamp=datetime.now()
        )
    
    def _signal_to_dict(self, signal: TradeSignal) -> Dict:
        return {
            "symbol": signal.symbol,
            "strategy": signal.strategy.value,
            "direction": signal.direction,
            "entry_price": signal.entry_price,
            "strike": signal.strike,
            "expiration": signal.expiration.strftime("%Y-%m-%d"),
            "contracts": signal.contracts,
            "premium": signal.premium,
            "greeks": signal.greeks,
            "stop_loss": signal.stop_loss,
            "take_profit": signal.take_profit,
            "rationale": signal.rationale,
            "confidence": signal.confidence
        }

class ExecutionAgent(Agent):
    """Handles order execution and fills"""
    
    def __init__(self):
        super().__init__("trader_execution", AgentRole.TRADER)
        
    async def _reason(self, observation: str) -> str:
        return "Evaluating execution strategy: limit vs market, timing, liquidity"
    
    async def _decide_action(self, reasoning: str) -> Message:
        return Message(
            msg_id=f"exec_{datetime.now().timestamp()}",
            sender=self.agent_id,
            recipient="trader_lead",
            msg_type=MessageType.RESPONSE,
            payload={"status": "execution_pending", "analysis": reasoning}
        )
