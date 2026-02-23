"""
Educational Module
Multi-level explanations from beginner analogies to expert quant analysis
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

class SkillLevel(Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

@dataclass
class EducationalContent:
    concept: str
    level: SkillLevel
    title: str
    explanation: str
    analogy: Optional[str]
    key_takeaways: list
    related_concepts: list

class OptionsEducator:
    """
    Translates quantitative analysis into multiple sophistication levels.
    Same analytical foundation, different presentation.
    """
    
    def __init__(self):
        self.user_level = SkillLevel.INTERMEDIATE  # Default, learns from interactions
        
    def explain_strategy(
        self,
        strategy: str,
        metrics: Dict[str, Any],
        target_level: Optional[SkillLevel] = None
    ) -> Dict[str, EducationalContent]:
        """
        Generate multi-level explanation for a trading strategy.
        
        Returns explanations at all levels from beginner to expert.
        """
        
        level = target_level or self.user_level
        
        explanations = {
            SkillLevel.BEGINNER: self._explain_beginner(strategy, metrics),
            SkillLevel.INTERMEDIATE: self._explain_intermediate(strategy, metrics),
            SkillLevel.ADVANCED: self._explain_advanced(strategy, metrics),
            SkillLevel.EXPERT: self._explain_expert(strategy, metrics)
        }
        
        return explanations
    
    def _explain_beginner(self, strategy: str, metrics: Dict) -> EducationalContent:
        """Beginner-friendly analogies and simple concepts"""
        
        analogies = {
            "covered_call": {
                "title": "Renting Out Stock You Own",
                "explanation": (
                    "You own 100 shares of a stock. Someone pays you upfront for the right to buy "
                    "those shares at a specific price by a certain date. You keep the payment no matter what. "
                    "If the stock stays below that price, you keep your shares AND the payment. "
                    "If it goes above, you sell your shares at the agreed price."
                ),
                "analogy": (
                    "Like renting out a house you own. You get monthly rent (the premium). "
                    "The tenant has the option to buy your house at a set price. If they don't exercise it, "
                    "you keep the rent and the house. If they do, you sell at the agreed price."
                ),
                "key_takeaways": [
                    "You must own 100 shares first",
                    "You collect money immediately (the premium)",
                    "Your upside is capped at the strike price",
                    "Best when you think stock will stay flat or rise slightly"
                ]
            },
            "cash_secured_put": {
                "title": "Getting Paid to Place a Limit Order",
                "explanation": (
                    "You promise to buy 100 shares at a specific price if the stock drops to that level. "
                    "Someone pays you upfront for this promise. If the stock stays above your price, "
                    "you keep the payment and don't buy. If it drops, you buy the shares at your target price."
                ),
                "analogy": (
                    "Like being a car dealer who pays you $500 to have first dibs on buying your car "
                    "for $15,000. If the car value stays above $15k, they don't buy it and you keep the $500. "
                    "If it drops to $14k, they buy it from you for $15k (and you still keep the $500)."
                ),
                "key_takeaways": [
                    "You need cash ready to buy 100 shares",
                    "Only use on stocks you actually want to own",
                    "Pick a strike below current price (discount level)",
                    "You keep the premium either way"
                ]
            },
            "iron_condor": {
                "title": "Betting the Stock Stays in a Range",
                "explanation": (
                    "You set up four options that create a 'zone' where you make money. "
                    "You win if the stock stays between a lower and upper price. "
                    "You collect money upfront. If the stock stays in your zone until expiration, "
                    "you keep all the money. If it breaks out, you could lose money."
                ),
                "analogy": (
                    "Like being a casino that takes bets on a boxing match. You set the over/under lines. "
                    "As long as the fight goes the expected number of rounds (not too short, not too long), "
                    "the house wins. You're the house collecting the vig."
                ),
                "key_takeaways": [
                    "Works best when you expect little movement",
                    "You need to pick a price range",
                    "Higher volatility = more premium but riskier",
                    "Manage early if stock approaches your boundaries"
                ]
            },
            "pmcc": {
                "title": "Covered Call on Steroids (Cheaper Version)",
                "explanation": (
                    "Instead of buying 100 shares (expensive), you buy a long-term option that acts like shares. "
                    "This costs 20-30% as much. Then you sell short-term options against it just like a covered call. "
                    "Same income strategy, way less capital tied up."
                ),
                "analogy": (
                    "Instead of buying a house to rent out, you get a long-term lease with the right to buy. "
                    "Much cheaper upfront. Then you sublease rooms short-term for income. "
                    "If property values rise, you benefit. If they fall, your loss is limited to the lease cost."
                ),
                "key_takeaways": [
                    "Requires 70-80% less capital than regular covered call",
                    "Buy LEAPS (long-term options) with high delta",
                    "Same monthly income potential",
                    "Risk is limited to what you paid for LEAPS"
                ]
            },
            "calendar_spread": {
                "title": "Exploiting Time Differences",
                "explanation": (
                    "You sell an option that expires soon and buy the same strike option that expires later. "
                    "The one you sold loses value faster than the one you bought. "
                    "You profit from this difference in time decay. Works best when the stock stays near your strike."
                ),
                "analogy": (
                    "Like buying a year-long gym membership for $500, then selling 30-day passes for $50 each. "
                    "You sell 12 monthly passes for $600 total, but your cost was only $500. "
                    "The month-to-month people pay more per day than the annual members."
                ),
                "key_takeaways": [
                    "Buy long-dated, sell short-dated (same strike)",
                    "Profits from different decay rates",
                    "Stock needs to stay near your chosen strike",
                    "Vega exposure increases your volatility risk"
                ]
            },
            "debit_spread": {
                "title": "Directional Bet with Training Wheels",
                "explanation": (
                    "You buy an option and sell another option at a different strike to reduce the cost. "
                    "Your profit is capped, but so is your loss. Cheaper than buying a single option outright, "
                    "but you give up some upside. Great for when you have a price target in mind."
                ),
                "analogy": (
                    "Instead of betting $100 that your team wins the championship, you bet $30 that they "
                    "at least make the playoffs. You spend less, and you know exactly how much you can win "
                    "and lose before you even place the bet."
                ),
                "key_takeaways": [
                    "Defined risk and reward",
                    "Cheaper than single option",
                    "Capped upside at the higher strike",
                    "Great for price target scenarios"
                ]
            }
        }
        
        content = analogies.get(strategy, {
            "title": f"{strategy.replace('_', ' ').title()}",
            "explanation": "Advanced strategy - see intermediate level for details",
            "analogy": None,
            "key_takeaways": ["See advanced documentation"]
        })
        
        return EducationalContent(
            concept=strategy,
            level=SkillLevel.BEGINNER,
            title=content["title"],
            explanation=content["explanation"],
            analogy=content["analogy"],
            key_takeaways=content["key_takeaways"],
            related_concepts=["risk_management", "premium", "strike_price"]
        )
    
    def _explain_intermediate(self, strategy: str, metrics: Dict) -> EducationalContent:
        """Intermediate level with some technical detail"""
        
        explanations = {
            "covered_call": {
                "title": "Covered Call Strategy Analysis",
                "explanation": (
                    f"Position: Long 100 shares, Short 1 call option\n"
                    f"Strike: ${metrics.get('strike', 50):.2f} "
                    f"({'%.0f' % ((metrics.get('strike', 50)/metrics.get('stock_price', 45)-1)*100)}% OTM)\n"
                    f"Premium Collected: ${metrics.get('premium', 1.5):.2f} ({metrics.get('premium', 1.5)/metrics.get('stock_price', 45)*100:.1f}% of stock price)\n"
                    f"Max Profit: ${metrics.get('max_profit', 5):.2f} (if assigned)\n"
                    f"Breakeven: ${metrics.get('stock_price', 45) - metrics.get('premium', 1.5):.2f}\n"
                    f"Annualized Return: {metrics.get('annualized_return', 15):.1f}%"
                ),
                "key_takeaways": [
                    f"Delta: {metrics.get('delta', 0.35):.2f} - hedged but still bullish",
                    f"Theta: ${metrics.get('theta', 0.12):.2f}/day time decay working for you",
                    "Assignment risk if stock closes above strike at expiration",
                    "Rolling options available to avoid assignment"
                ]
            },
            "iron_condor": {
                "title": "Iron Condor Risk Profile",
                "explanation": (
                    f"Structure: Short put spread + Short call spread\n"
                    f"Put Wing: ${metrics.get('put_long', 40):.0f}/${metrics.get('put_short', 45):.0f}\n"
                    f"Call Wing: ${metrics.get('call_short', 55):.0f}/${metrics.get('call_long', 60):.0f}\n"
                    f"Credit Received: ${metrics.get('credit', 1.0):.2f}\n"
                    f"Max Risk: ${metrics.get('max_risk', 4):.2f} (width - credit)\n"
                    f"Probability of Profit: {metrics.get('pop', 65):.0f}%"
                ),
                "key_takeaways": [
                    "Short vega position - benefits from volatility crush",
                    f"Delta near zero: {metrics.get('delta', 0.05):.2f}",
                    "Manage at 50% profit or 21 DTE",
                    "Roll untested side if one wing threatened"
                ]
            }
        }
        
        content = explanations.get(strategy, {
            "title": f"{strategy.replace('_', ' ').title()}",
            "explanation": str(metrics),
            "key_takeaways": ["See metrics for details"]
        })
        
        return EducationalContent(
            concept=strategy,
            level=SkillLevel.INTERMEDIATE,
            title=content["title"],
            explanation=content["explanation"],
            analogy=None,
            key_takeaways=content["key_takeaways"],
            related_concepts=["greeks", "probability", "expected_return"]
        )
    
    def _explain_advanced(self, strategy: str, metrics: Dict) -> EducationalContent:
        """Advanced level with Greeks and quantitative details"""
        
        return EducationalContent(
            concept=strategy,
            level=SkillLevel.ADVANCED,
            title=f"{strategy.replace('_', ' ').title()} - Quantitative Analysis",
            explanation=(
                f"Greek Profile:\n"
                f"  Delta: {metrics.get('delta', 0):.3f} | Gamma: {metrics.get('gamma', 0):.4f}\n"
                f"  Theta: ${metrics.get('theta', 0):.3f}/day | Vega: ${metrics.get('vega', 0):.3f}/1%\n\n"
                f"Risk Metrics:\n"
                f"  Max Loss: ${metrics.get('max_loss', 0):.2f}\n"
                f"  Max Profit: ${metrics.get('max_profit', 0):.2f}\n"
                f"  Risk/Reward: 1:{metrics.get('rr_ratio', 1):.1f}\n\n"
                f"Market Conditions:\n"
                f"  IV Rank: {metrics.get('iv_rank', 50):.0f}%\n"
                f"  VIX Environment: {metrics.get('vix_regime', 'normal')}\n"
                f"  Expected Move: ±${metrics.get('expected_move', 2):.2f}"
            ),
            analogy=None,
            key_takeaways=[
                f"Position Greeks suggest {self._interpret_greeks(metrics)}",
                f"IV percentile of {metrics.get('iv_rank', 50):.0f}% implies {'favorable' if metrics.get('iv_rank', 50) > 50 else 'unfavorable'} entry",
                f"VIX at {metrics.get('vix', 20):.1f} indicates {self._interpret_vix(metrics.get('vix', 20))} environment"
            ],
            related_concepts=["volatility_skew", "term_structure", "correlation"]
        )
    
    def _explain_expert(self, strategy: str, metrics: Dict) -> EducationalContent:
        """Expert level with full quant breakdown"""
        
        return EducationalContent(
            concept=strategy,
            level=SkillLevel.EXPERT,
            title=f"{strategy.replace('_', ' ').title()} - Full Quant Framework",
            explanation=(
                f"Black-Scholes Valuation:\n"
                f"  Theoretical Price: ${metrics.get('theo_price', 0):.3f}\n"
                f"  Market Price: ${metrics.get('market_price', 0):.3f}\n"
                f"  Edge: {metrics.get('edge_bps', 0):.0f} bps\n\n"
                f"Greek Sensitivities:\n"
                f"  Charm: {metrics.get('charm', 0):.4f} (delta decay)\n"
                f"  Vanna: {metrics.get('vanna', 0):.4f} (delta-vol)\n"
                f"  Vomma: {metrics.get('vomma', 0):.4f} (vega-vol)\n"
                f"  Speed: {metrics.get('speed', 0):.6f} (gamma spot)\n\n"
                f"Scenario Analysis:\n"
                f"  +10% Move P&L: ${metrics.get('pnl_up10', 0):.2f}\n"
                f"  -10% Move P&L: ${metrics.get('pnl_down10', 0):.2f}\n"
                f"  +10vol P&L: ${metrics.get('pnl_vol_up', 0):.2f}\n"
                f"  7D Theta: ${metrics.get('theta_7d', 0):.2f}"
            ),
            analogy=None,
            key_takeaways=[
                f"Second-order Greeks indicate {self._analyze_second_order(metrics)}",
                f"Scenario matrix shows {self._analyze_scenarios(metrics)}",
                f"Edge analysis suggests {'take' if metrics.get('edge_bps', 0) > 0 else 'pass'}"
            ],
            related_concepts=["stochastic_vol", "local_vol", "jump_diffusion"]
        )
    
    def _interpret_greeks(self, metrics: Dict) -> str:
        """Interpret Greek profile"""
        delta = metrics.get('delta', 0)
        gamma = metrics.get('gamma', 0)
        theta = metrics.get('theta', 0)
        vega = metrics.get('vega', 0)
        
        interpretations = []
        if abs(delta) > 0.3:
            interpretations.append("high directional exposure")
        if abs(gamma) > 0.05:
            interpretations.append("significant convexity risk")
        if theta > 0.1:
            interpretations.append("strong theta harvesting profile")
        if abs(vega) > 0.1:
            interpretations.append("volatility sensitive")
            
        return ", ".join(interpretations) if interpretations else "balanced profile"
    
    def _interpret_vix(self, vix: float) -> str:
        """Interpret VIX level"""
        if vix < 15:
            return "complacent/low volatility"
        elif vix < 20:
            return "normal"
        elif vix < 25:
            return "elevated caution"
        else:
            return "high fear/stress"
    
    def _analyze_second_order(self, metrics: Dict) -> str:
        """Analyze second-order Greeks"""
        vanna = metrics.get('vanna', 0)
        if abs(vanna) > 0.01:
            return "significant delta-vol correlation risk"
        return "stable higher-order profile"
    
    def _analyze_scenarios(self, metrics: Dict) -> str:
        """Analyze scenario results"""
        up = metrics.get('pnl_up10', 0)
        down = metrics.get('pnl_down10', 0)
        
        if up > 0 and down < 0:
            return "asymmetric directional bias"
        elif up < 0 and down < 0:
            return "range-bound profit profile"
        else:
            return "balanced risk distribution"
    
    def format_for_user(
        self,
        strategy: str,
        metrics: Dict,
        target_level: Optional[SkillLevel] = None
    ) -> str:
        """Format explanation for display to user"""
        
        explanations = self.explain_strategy(strategy, metrics, target_level)
        
        # Format based on requested level
        level = target_level or self.user_level
        content = explanations[level]
        
        output = f"\n{'='*60}\n"
        output += f"{content.title}\n"
        output += f"{'='*60}\n\n"
        
        if content.analogy:
            output += f"💡 THE SIMPLE VERSION:\n{content.analogy}\n\n"
            output += f"📊 THE DETAILS:\n{content.explanation}\n\n"
        else:
            output += f"{content.explanation}\n\n"
        
        output += f"🎯 KEY POINTS:\n"
        for takeaway in content.key_takeaways:
            output += f"  • {takeaway}\n"
        
        output += f"\n📚 RELATED: {', '.join(content.related_concepts)}\n"
        
        return output
    
    def detect_user_level(self, interaction_history: list) -> SkillLevel:
        """
        Detect user's sophistication level from interaction patterns.
        
        Signals:
        - Uses terms like 'Greeks', 'IV', 'skew' → Advanced
        - Asks about delta/theta → Intermediate  
        - Needs basic explanations → Beginner
        - Discusses second-order Greeks → Expert
        """
        
        expert_terms = ['charm', 'vanna', 'vomma', 'local vol', 'stochastic vol']
        advanced_terms = ['gamma', 'vega', 'skew', 'term structure', 'vwap']
        intermediate_terms = ['delta', 'theta', 'premium', 'strike', 'expiration']
        
        all_text = ' '.join(interaction_history).lower()
        
        if any(term in all_text for term in expert_terms):
            return SkillLevel.EXPERT
        elif any(term in all_text for term in advanced_terms):
            return SkillLevel.ADVANCED
        elif any(term in all_text for term in intermediate_terms):
            return SkillLevel.INTERMEDIATE
        else:
            return SkillLevel.BEGINNER

class LearningPath:
    """
    Curated learning progression from beginner to expert.
    """
    
    MODULES = [
        {
            "level": SkillLevel.BEGINNER,
            "modules": [
                "What are options?",
                "Calls vs Puts",
                "Premium and expiration",
                "Moneyness (ITM/ATM/OTM)",
                "Basic strategies: Covered calls, Cash-secured puts"
            ]
        },
        {
            "level": SkillLevel.INTERMEDIATE,
            "modules": [
                "Introduction to the Greeks",
                "Implied volatility explained",
                "Vertical spreads",
                "Iron condors and butterflies",
                "Risk management basics"
            ]
        },
        {
            "level": SkillLevel.ADVANCED,
            "modules": [
                "Volatility skew and term structure",
                "Calendar and diagonal spreads",
                "Greek hedging techniques",
                "Probability and expected value",
                "Advanced risk management"
            ]
        },
        {
            "level": SkillLevel.EXPERT,
            "modules": [
                "Stochastic volatility models",
                "Exotic options structures",
                "Volatility arbitrage",
                "Quantitative backtesting",
                "Portfolio optimization"
            ]
        }
    ]
    
    @classmethod
    def get_path(cls, current_level: SkillLevel) -> list:
        """Get recommended next modules for user's level"""
        for i, entry in enumerate(cls.MODULES):
            if entry["level"] == current_level and i < len(cls.MODULES) - 1:
                return cls.MODULES[i + 1]["modules"]
        return []
