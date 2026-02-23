"""
Research Teams Agent
Structured debate and hypothesis testing with confidence-weighted recommendations
"""

from core import Agent, AgentRole, Message, MessageType
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
import numpy as np

@dataclass
class ResearchReport:
    symbol: str
    bullish_case: Dict[str, Any]
    bearish_case: Dict[str, Any]
    neutral_case: Dict[str, Any]
    recommendation: str  # "bullish", "bearish", "neutral"
    confidence: float
    conviction_score: float  # -1 to 1
    catalysts: List[str]
    risks: List[str]
    price_target: Tuple[float, float]  # (bear, bull)
    timestamp: datetime

class ResearchTeamLead(Agent):
    """
    Coordinates structured debate between bullish and bearish research agents.
    Implements conviction scoring and confidence-weighted recommendations.
    """
    
    def __init__(self):
        super().__init__("research_lead", AgentRole.RESEARCH)
        self.candidates = []
        self.reports = {}
        
    async def _reason(self, observation: str) -> str:
        """Synthesize analysis into research framework"""
        recent_analyses = [m for m in self.memory if m.get("msg_type") == "analysis"]
        
        # Extract unique symbols from recent analyses
        symbols = set()
        for analysis in recent_analyses:
            payload = analysis.get("payload", {})
            if "analyses" in payload:
                for a in payload["analyses"]:
                    symbols.add(a.get("symbol"))
        
        self.candidates = list(symbols)[:5]  # Top 5 candidates
        
        return f"""
        Research team reasoning:
        - {len(self.candidates)} candidates identified from analyst reports
        - Initiating structured debate: bullish vs bearish cases
        - Will develop confidence-weighted recommendations
        - Candidates: {self.candidates}
        """
    
    async def _decide_action(self, reasoning: str) -> Message:
        """Coordinate research debate"""
        reports = []
        
        for symbol in self.candidates:
            report = await self._conduct_debate(symbol)
            reports.append(report)
            self.reports[symbol] = report
        
        # Rank by conviction score
        ranked = sorted(reports, key=lambda r: abs(r.conviction_score), reverse=True)
        
        return Message(
            msg_id=f"research_{datetime.now().timestamp()}",
            sender=self.agent_id,
            recipient="all",
            msg_type=MessageType.RESEARCH_REPORT,
            payload={
                "reports": [self._report_to_dict(r) for r in ranked],
                "top_pick": ranked[0].symbol if ranked else None,
                "total_candidates": len(reports)
            },
            priority=3
        )
    
    async def _conduct_debate(self, symbol: str) -> ResearchReport:
        """Conduct structured debate for a symbol"""
        
        # Bullish case generation
        bullish = await self._generate_bullish_case(symbol)
        
        # Bearish case generation
        bearish = await self._generate_bearish_case(symbol)
        
        # Neutral/base case
        neutral = await self._generate_neutral_case(symbol)
        
        # Synthesize and score
        conviction, confidence = self._calculate_conviction(bullish, bearish, neutral)
        
        recommendation = "neutral"
        if conviction > 0.3:
            recommendation = "bullish"
        elif conviction < -0.3:
            recommendation = "bearish"
        
        return ResearchReport(
            symbol=symbol,
            bullish_case=bullish,
            bearish_case=bearish,
            neutral_case=neutral,
            recommendation=recommendation,
            confidence=confidence,
            conviction_score=conviction,
            catalysts=bullish.get("catalysts", []) + bearish.get("risks", []),
            risks=bearish.get("risks", []),
            price_target=(bearish.get("price_target", 0), bullish.get("price_target", 0)),
            timestamp=datetime.now()
        )
    
    async def _generate_bullish_case(self, symbol: str) -> Dict:
        """Generate bullish investment thesis"""
        catalysts = [
            "Strong earnings growth trajectory",
            "Expanding market share in growing sector",
            "Technical breakout with volume confirmation",
            "Options flow showing institutional accumulation",
            "Undervalued relative to peers"
        ]
        
        base_price = np.random.uniform(20, 45)
        
        return {
            "thesis": f"{symbol} positioned for upside due to operational momentum",
            "catalysts": np.random.choice(catalysts, size=np.random.randint(2, 4), replace=False).tolist(),
            "probability": np.random.uniform(0.35, 0.65),
            "price_target": base_price * (1 + np.random.uniform(0.15, 0.40)),
            "timeframe": f"{np.random.randint(1, 6)} months",
            "key_levels": {
                "support": base_price * 0.95,
                "resistance": base_price * 1.15,
                "breakout": base_price * 1.08
            }
        }
    
    async def _generate_bearish_case(self, symbol: str) -> Dict:
        """Generate bearish risk case"""
        risks = [
            "Margin compression from competition",
            "Cyclical downturn exposure",
            "High debt load in rising rate environment",
            "Technical breakdown below key support",
            "Insider selling and bearish options flow"
        ]
        
        base_price = np.random.uniform(20, 45)
        
        return {
            "thesis": f"{symbol} faces headwinds that could pressure valuation",
            "risks": np.random.choice(risks, size=np.random.randint(2, 4), replace=False).tolist(),
            "probability": np.random.uniform(0.25, 0.55),
            "price_target": base_price * (1 - np.random.uniform(0.10, 0.30)),
            "timeframe": f"{np.random.randint(1, 6)} months",
            "key_levels": {
                "support": base_price * 0.90,
                "stop_loss": base_price * 0.93,
                "breakdown": base_price * 0.95
            }
        }
    
    async def _generate_neutral_case(self, symbol: str) -> Dict:
        """Generate base case scenario"""
        base_price = np.random.uniform(20, 45)
        
        return {
            "thesis": f"{symbol} fairly valued with balanced risk/reward",
            "expected_return": np.random.uniform(-0.05, 0.10),
            "fair_value": base_price,
            "range": (base_price * 0.90, base_price * 1.10),
            "catalysts_needed": ["Earnings beat", "Guidance raise", "Sector rotation"]
        }
    
    def _calculate_conviction(self, bullish: Dict, bearish: Dict, neutral: Dict) -> Tuple[float, float]:
        """Calculate conviction score and confidence"""
        bull_prob = bullish.get("probability", 0.5)
        bear_prob = bearish.get("probability", 0.5)
        
        # Conviction: weighted difference between bull and bear
        conviction = (bull_prob - bear_prob) * 2  # Scale to -1 to 1
        
        # Confidence: based on clarity of thesis
        bull_strength = len(bullish.get("catalysts", [])) / 5
        bear_strength = len(bearish.get("risks", [])) / 5
        confidence = (bull_strength + bear_strength) / 2
        confidence = min(confidence * 1.5, 0.95)  # Cap at 0.95
        
        return conviction, confidence
    
    def _report_to_dict(self, report: ResearchReport) -> Dict:
        return {
            "symbol": report.symbol,
            "recommendation": report.recommendation,
            "confidence": report.confidence,
            "conviction_score": report.conviction_score,
            "bullish_case": report.bullish_case,
            "bearish_case": report.bearish_case,
            "price_target": report.price_target,
            "catalysts": report.catalysts,
            "risks": report.risks,
            "timestamp": report.timestamp.isoformat()
        }

class BullishResearcher(Agent):
    """Specialized bullish case researcher"""
    
    def __init__(self):
        super().__init__("research_bull", AgentRole.RESEARCH)
        
    async def _reason(self, observation: str) -> str:
        return "Building bullish thesis with catalyst identification and price target derivation"
    
    async def _decide_action(self, reasoning: str) -> Message:
        return Message(
            msg_id=f"bull_{datetime.now().timestamp()}",
            sender=self.agent_id,
            recipient="research_lead",
            msg_type=MessageType.RESPONSE,
            payload={"side": "bullish", "analysis": reasoning}
        )

class BearishResearcher(Agent):
    """Specialized bearish case researcher"""
    
    def __init__(self):
        super().__init__("research_bear", AgentRole.RESEARCH)
        
    async def _reason(self, observation: str) -> str:
        return "Building bearish thesis with risk identification and downside scenarios"
    
    async def _decide_action(self, reasoning: str) -> Message:
        return Message(
            msg_id=f"bear_{datetime.now().timestamp()}",
            sender=self.agent_id,
            recipient="research_lead",
            msg_type=MessageType.RESPONSE,
            payload={"side": "bearish", "analysis": reasoning}
        )
