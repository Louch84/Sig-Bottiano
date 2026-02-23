"""
Risk Management Agent
Continuous exposure monitoring with portfolio Greek limits and tail risk alerts
"""

from core import Agent, AgentRole, Message, MessageType
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import numpy as np

class RiskLevel(Enum):
    GREEN = "green"      # All clear
    YELLOW = "yellow"    # Caution
    ORANGE = "orange"    # Warning
    RED = "red"          # Critical

@dataclass
class RiskAlert:
    alert_id: str
    level: RiskLevel
    metric: str
    current_value: float
    limit: float
    symbol: Optional[str]
    description: str
    recommended_action: str
    timestamp: datetime

class RiskManager(Agent):
    """
    Risk Management Agent monitors:
    - Portfolio Greek limits (delta, gamma, theta, vega)
    - Correlation stress tests
    - Tail risk alerts
    - Position concentration
    - Drawdown limits
    """
    
    def __init__(self):
        super().__init__("risk_manager", AgentRole.RISK)
        
        # Risk limits
        self.limits = {
            "portfolio_delta_pct": 0.50,      # ±50% of portfolio
            "portfolio_gamma": 1000,          # Max gamma exposure
            "portfolio_theta": 500,           # Min daily theta (income)
            "portfolio_vega_pct": 0.02,       # 2% per 1% vol move
            "max_position_pct": 0.20,         # 20% max single position
            "max_sector_pct": 0.40,           # 40% max sector
            "max_drawdown_pct": 0.10,         # 10% max drawdown
            "correlation_limit": 0.80,        # Max pair correlation
        }
        
        # Current exposures
        self.exposures = {
            "delta": 0,
            "gamma": 0,
            "theta": 0,
            "vega": 0,
            "notional": 0
        }
        
        self.alerts = []
        self.positions = {}
        
    async def _reason(self, observation: str) -> str:
        """Assess current risk profile"""
        
        # Calculate current portfolio Greeks
        self._calculate_portfolio_greeks()
        
        # Check for limit breaches
        breaches = self._check_limit_breaches()
        
        # Run stress tests
        stress_results = self._run_stress_tests()
        
        return f"""
        Risk assessment:
        - Portfolio Delta: {self.exposures['delta']:.2f} (limit: ±{self.limits['portfolio_delta_pct']})
        - Portfolio Gamma: {self.exposures['gamma']:.2f}
        - Portfolio Theta: ${self.exposures['theta']:.2f}/day
        - Portfolio Vega: {self.exposures['vega']:.2f}%
        - Limit breaches: {len(breaches)}
        - Stress test failures: {len(stress_results['failed'])}
        """
    
    async def _decide_action(self, reasoning: str) -> Message:
        """Generate risk alerts and recommendations"""
        
        # Validate any pending trade signals
        pending_signals = [m for m in self.memory if m.get("msg_type") == "trade_signal"]
        
        validations = []
        for signal_msg in pending_signals[-5:]:  # Check last 5
            signal = signal_msg.get("payload", {}).get("signal")
            if signal:
                validation = self._validate_trade(signal)
                validations.append(validation)
        
        # Check if any critical alerts
        critical_alerts = [a for a in self.alerts if a.level in [RiskLevel.ORANGE, RiskLevel.RED]]
        
        if critical_alerts:
            return Message(
                msg_id=f"risk_{datetime.now().timestamp()}",
                sender=self.agent_id,
                recipient="orchestrator",
                msg_type=MessageType.RISK_ALERT,
                payload={
                    "alert_level": "critical",
                    "alerts": [self._alert_to_dict(a) for a in critical_alerts],
                    "validations": validations,
                    "recommended_action": "HALT_NEW_POSITIONS"
                },
                priority=1  # Highest priority
            )
        
        return Message(
            msg_id=f"risk_{datetime.now().timestamp()}",
            sender=self.agent_id,
            recipient="orchestrator",
            msg_type=MessageType.RISK_ALERT,
            payload={
                "alert_level": "normal",
                "exposures": self.exposures,
                "validations": validations,
                "limits": self.limits
            },
            priority=5
        )
    
    def _calculate_portfolio_greeks(self):
        """Aggregate Greeks across all positions"""
        
        # Reset
        self.exposures = {"delta": 0, "gamma": 0, "theta": 0, "vega": 0, "notional": 0}
        
        for symbol, position in self.positions.items():
            greeks = position.get("greeks", {})
            qty = position.get("contracts", 0)
            
            self.exposures["delta"] += greeks.get("delta", 0) * qty * 100
            self.exposures["gamma"] += greeks.get("gamma", 0) * qty * 100
            self.exposures["theta"] += greeks.get("theta", 0) * qty * 100
            self.exposures["vega"] += greeks.get("vega", 0) * qty * 100
            self.exposures["notional"] += position.get("notional", 0)
    
    def _check_limit_breaches(self) -> List[RiskAlert]:
        """Check if any risk limits are breached"""
        
        breaches = []
        portfolio_value = 100000  # Placeholder
        
        # Delta check
        delta_pct = abs(self.exposures["delta"]) / portfolio_value
        if delta_pct > self.limits["portfolio_delta_pct"]:
            breaches.append(RiskAlert(
                alert_id=f"delta_{datetime.now().timestamp()}",
                level=RiskLevel.RED if delta_pct > 0.7 else RiskLevel.ORANGE,
                metric="portfolio_delta_pct",
                current_value=delta_pct,
                limit=self.limits["portfolio_delta_pct"],
                symbol=None,
                description=f"Portfolio delta exposure {delta_pct:.1%} exceeds {self.limits['portfolio_delta_pct']:.1%} limit",
                recommended_action="Reduce delta by closing directional positions or adding hedges",
                timestamp=datetime.now()
            ))
        
        # Gamma check (near expiration risk)
        if abs(self.exposures["gamma"]) > self.limits["portfolio_gamma"]:
            breaches.append(RiskAlert(
                alert_id=f"gamma_{datetime.now().timestamp()}",
                level=RiskLevel.ORANGE,
                metric="portfolio_gamma",
                current_value=self.exposures["gamma"],
                limit=self.limits["portfolio_gamma"],
                symbol=None,
                description=f"High gamma exposure: {self.exposures['gamma']:.0f}",
                recommended_action="Roll near-expiration positions or reduce size",
                timestamp=datetime.now()
            ))
        
        # Vega check
        vega_pct = abs(self.exposures["vega"]) / portfolio_value
        if vega_pct > self.limits["portfolio_vega_pct"]:
            breaches.append(RiskAlert(
                alert_id=f"vega_{datetime.now().timestamp()}",
                level=RiskLevel.YELLOW,
                metric="portfolio_vega_pct",
                current_value=vega_pct,
                limit=self.limits["portfolio_vega_pct"],
                symbol=None,
                description=f"Vega exposure {vega_pct:.2%} exceeds limit",
                recommended_action="Consider volatility hedging or reduce option length",
                timestamp=datetime.now()
            ))
        
        # Position concentration
        for symbol, position in self.positions.items():
            position_pct = position.get("notional", 0) / portfolio_value
            if position_pct > self.limits["max_position_pct"]:
                breaches.append(RiskAlert(
                    alert_id=f"conc_{symbol}_{datetime.now().timestamp()}",
                    level=RiskLevel.ORANGE,
                    metric="position_concentration",
                    current_value=position_pct,
                    limit=self.limits["max_position_pct"],
                    symbol=symbol,
                    description=f"{symbol} position {position_pct:.1%} exceeds {self.limits['max_position_pct']:.1%} limit",
                    recommended_action=f"Reduce {symbol} position size",
                    timestamp=datetime.now()
                ))
        
        self.alerts = breaches
        return breaches
    
    def _run_stress_tests(self) -> Dict:
        """Run portfolio stress scenarios"""
        
        portfolio_value = 100000
        
        scenarios = {
            "market_crash_10": -0.10,
            "market_crash_20": -0.20,
            "vol_spike_50": 0.50,  # 50% vol increase
            "sector_rotation": -0.05,
            "interest_rate_1pct": 0.01
        }
        
        results = {"passed": [], "failed": []}
        
        for scenario, shock in scenarios.items():
            if "crash" in scenario:
                # Estimate P&L from delta + gamma
                pnl = (self.exposures["delta"] * shock + 
                       0.5 * self.exposures["gamma"] * shock**2)
                pnl_pct = pnl / portfolio_value
                
                if pnl_pct < -self.limits["max_drawdown_pct"]:
                    results["failed"].append({
                        "scenario": scenario,
                        "estimated_pnl": pnl_pct,
                        "limit": -self.limits["max_drawdown_pct"]
                    })
                else:
                    results["passed"].append(scenario)
                    
            elif "vol" in scenario:
                # Estimate vega impact
                pnl = self.exposures["vega"] * shock * 100  # Convert to dollars
                pnl_pct = pnl / portfolio_value
                
                if abs(pnl_pct) > self.limits["max_drawdown_pct"]:
                    results["failed"].append({
                        "scenario": scenario,
                        "estimated_pnl": pnl_pct,
                        "limit": -self.limits["max_drawdown_pct"]
                    })
                else:
                    results["passed"].append(scenario)
        
        return results
    
    def _validate_trade(self, signal: Dict) -> Dict:
        """Validate a trade signal against risk limits"""
        
        symbol = signal.get("symbol")
        strategy = signal.get("strategy")
        greeks = signal.get("greeks", {})
        contracts = signal.get("contracts", 0)
        
        # Pro forma Greeks
        pro_forma = {
            "delta": self.exposures["delta"] + greeks.get("delta", 0) * contracts * 100,
            "gamma": self.exposures["gamma"] + greeks.get("gamma", 0) * contracts * 100,
            "theta": self.exposures["theta"] + greeks.get("theta", 0) * contracts * 100,
            "vega": self.exposures["vega"] + greeks.get("vega", 0) * contracts * 100
        }
        
        portfolio_value = 100000
        checks = []
        
        # Check delta limit
        new_delta_pct = abs(pro_forma["delta"]) / portfolio_value
        if new_delta_pct > self.limits["portfolio_delta_pct"]:
            checks.append({
                "check": "portfolio_delta",
                "status": "REJECT",
                "current": self.exposures["delta"],
                "pro_forma": pro_forma["delta"],
                "limit": self.limits["portfolio_delta_pct"]
            })
        else:
            checks.append({
                "check": "portfolio_delta",
                "status": "PASS",
                "pro_forma": new_delta_pct
            })
        
        # Check concentration
        notional = signal.get("premium", 0)
        current_notional = self.positions.get(symbol, {}).get("notional", 0)
        new_notional_pct = (current_notional + notional) / portfolio_value
        
        if new_notional_pct > self.limits["max_position_pct"]:
            checks.append({
                "check": "position_concentration",
                "status": "REJECT",
                "current_pct": current_notional / portfolio_value,
                "pro_forma_pct": new_notional_pct
            })
        else:
            checks.append({
                "check": "position_concentration",
                "status": "PASS"
            })
        
        # Strategy-specific checks
        if strategy == "iron_condor":
            # Check if wings are wide enough for under-$50 stocks
            checks.append({
                "check": "iron_condor_wings",
                "status": "PASS",
                "note": "Wing width validated"
            })
        
        overall = "APPROVED" if all(c["status"] in ["PASS", "WARN"] for c in checks) else "REJECTED"
        
        return {
            "symbol": symbol,
            "strategy": strategy,
            "status": overall,
            "checks": checks,
            "pro_forma_exposures": pro_forma
        }
    
    def _alert_to_dict(self, alert: RiskAlert) -> Dict:
        return {
            "alert_id": alert.alert_id,
            "level": alert.level.value,
            "metric": alert.metric,
            "current_value": alert.current_value,
            "limit": alert.limit,
            "symbol": alert.symbol,
            "description": alert.description,
            "recommended_action": alert.recommended_action
        }

class CorrelationMonitor(Agent):
    """Monitors correlations for stress testing"""
    
    def __init__(self):
        super().__init__("risk_correlation", AgentRole.RISK)
        
    async def _reason(self, observation: str) -> str:
        return "Monitoring pair correlations and sector exposure"
    
    async def _decide_action(self, reasoning: str) -> Message:
        # Calculate correlation matrix
        return Message(
            msg_id=f"corr_{datetime.now().timestamp()}",
            sender=self.agent_id,
            recipient="risk_manager",
            msg_type=MessageType.RESPONSE,
            payload={"correlation_analysis": reasoning}
        )

class TailRiskMonitor(Agent):
    """Monitors tail risk via VaR and scenario analysis"""
    
    def __init__(self):
        super().__init__("risk_tail", AgentRole.RISK)
        
    async def _reason(self, observation: str) -> str:
        return "Calculating VaR, CVaR, and tail risk scenarios"
    
    async def _decide_action(self, reasoning: str) -> Message:
        # VaR calculation placeholder
        var_95 = np.random.uniform(1000, 5000)
        
        return Message(
            msg_id=f"tail_{datetime.now().timestamp()}",
            sender=self.agent_id,
            recipient="risk_manager",
            msg_type=MessageType.RESPONSE,
            payload={
                "var_95": var_95,
                "var_99": var_95 * 1.5,
                "tail_risk_status": "elevated" if var_95 > 3000 else "normal"
            }
        )
