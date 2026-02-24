#!/usr/bin/env python3
"""
Cognitive Enhancement Integration
Combines psychology tools and reasoning framework into main system
"""

import sys
sys.path.insert(0, '/Users/sigbotti/.openclaw/workspace')

from psychology_tools import PsychologyTools, check_thinking, check_bias, reframe_thought
from reasoning_framework import ReasoningFramework, first_principles, mental_model_advice, pre_mortem_quick

class CognitiveEnhancement:
    """
    Main interface for psychology and reasoning enhancements
    Integrates with trading, decision-making, and general problem-solving
    """
    
    def __init__(self):
        self.psych_tools = PsychologyTools()
        self.reasoning = ReasoningFramework()
    
    def enhance_decision(self, decision_text: str, context: str = "general") -> Dict:
        """
        Full cognitive enhancement on a decision
        Returns psychology + reasoning analysis
        """
        # Psychology analysis
        thinking_mode = self.psych_tools.analyze_thinking_mode(decision_text)
        biases = self.psych_tools.detect_biases(decision_text)
        emotions = self.psych_tools.emotional_check_in(decision_text)
        
        # Reasoning analysis
        mental_models = self.reasoning.suggest_mental_models(decision_text)
        second_order = self.reasoning.second_order_analysis(decision_text[:50])
        
        # Build recommendations
        recommendations = []
        
        if thinking_mode['mode'] == 'fast':
            recommendations.append("⚠️ You're using fast thinking. Consider slowing down.")
        
        if biases:
            recommendations.append(f"⚠️ Detected {len(biases)} potential bias(es). Review carefully.")
        
        if emotions['detected_emotions']:
            recommendations.append(f"💭 Strong emotions detected ({', '.join(emotions['detected_emotions'])}). Consider waiting.")
        
        recommendations.append("🧠 Try applying mental models to this decision.")
        recommendations.append("🎯 Consider second and third-order effects.")
        
        return {
            'thinking_mode': thinking_mode,
            'biases_detected': biases,
            'emotional_state': emotions,
            'mental_models_suggested': mental_models,
            'second_order_effects': second_order,
            'recommendations': recommendations,
            'cognitive_risk_score': self._calculate_risk_score(thinking_mode, biases, emotions)
        }
    
    def _calculate_risk_score(self, thinking_mode, biases, emotions) -> int:
        """Calculate cognitive risk score (0-100)"""
        score = 0
        
        # Fast thinking adds risk
        if thinking_mode['mode'] == 'fast':
            score += 20
        
        # Each bias adds risk
        score += len(biases) * 15
        
        # Emotions add risk
        if emotions['detected_emotions']:
            score += len(emotions['detected_emotions']) * 10
        
        return min(100, score)
    
    def analyze_trade_decision(self, symbol: str, action: str, reasoning: str) -> Dict:
        """
        Specialized analysis for trading decisions
        """
        full_text = f"{action} {symbol}: {reasoning}"
        
        analysis = self.enhance_decision(full_text, "trading")
        
        # Add trading-specific insights
        trade_warnings = []
        
        if analysis['cognitive_risk_score'] > 60:
            trade_warnings.append("🚨 HIGH COGNITIVE RISK: Consider stepping away from this trade.")
        
        if any(b.bias_type.value == 'sunk_cost_fallacy' for b in analysis['biases_detected']):
            trade_warnings.append("⚠️ SUNK COST: Don't hold because of past losses. Evaluate current merits only.")
        
        if any(b.bias_type.value == 'fear' for b in analysis['biases_detected']) or 'fear' in analysis['emotional_state']['detected_emotions']:
            trade_warnings.append("⚠️ FEAR DETECTED: Fear leads to panic selling. Set mechanical stops instead.")
        
        if any(b.bias_type.value == 'greed' for b in analysis['biases_detected']) or 'greed' in analysis['emotional_state']['detected_emotions']:
            trade_warnings.append("⚠️ GREED/FOMO: Fear of missing out leads to bad entries. Wait for pullback.")
        
        analysis['trade_warnings'] = trade_warnings
        analysis['trade_recommendation'] = self._generate_trade_recommendation(analysis)
        
        return analysis
    
    def _generate_trade_recommendation(self, analysis: Dict) -> str:
        """Generate specific trade recommendation"""
        risk = analysis['cognitive_risk_score']
        
        if risk >= 70:
            return "🛑 DO NOT TRADE: Cognitive risk too high. Step away and reassess later."
        elif risk >= 50:
            return "⚠️ HIGH RISK: If you proceed, use half normal position size and tight stops."
        elif risk >= 30:
            return "⚡ MODERATE RISK: Proceed with caution. Document your reasoning."
        else:
            return "✅ LOW COGNITIVE RISK: Your thinking appears clear. Execute your plan."
    
    def reframe_negative(self, negative_thought: str) -> str:
        """Quick CBT reframe"""
        result = self.psych_tools.cbt_reframe(negative_thought)
        return f"💭 REFRAME:\nOriginal: {result.distorted_thought}\nType: {result.distortion_type}\nBalanced: {result.balanced_thought}\n\n🎯 ACTION: {result.action_step}"
    
    def apply_mental_model(self, situation: str, model_name: str = None) -> str:
        """Apply specific or suggested mental model"""
        if model_name:
            from reasoning_framework import MentalModel
            model = MentalModel(model_name)
            result = self.reasoning.apply_mental_model(model, situation)
            return f"🧠 {result['model']}\n{result['application']}"
        else:
            return mental_model_advice(situation)
    
    def thinking_audit(self, text: str) -> str:
        """
        Quick audit of thinking quality
        """
        thinking = self.psych_tools.analyze_thinking_mode(text)
        biases = self.psych_tools.detect_biases(text)
        emotions = self.psych_tools.emotional_check_in(text)
        
        output = f"🧠 THINKING AUDIT\n{'='*50}\n"
        output += f"Mode: {thinking['mode'].upper()}\n"
        output += f"Recommendation: {thinking['recommendation']}\n\n"
        
        if biases:
            output += f"⚠️ BIASES ({len(biases)}):\n"
            for b in biases[:2]:
                output += f"  • {b.bias_type.value.replace('_', ' ').title()}\n"
                output += f"    Fix: {b.mitigation[:80]}...\n\n"
        else:
            output += "✅ No major biases detected\n\n"
        
        if emotions['detected_emotions']:
            output += f"💭 EMOTIONS: {', '.join(emotions['detected_emotions'])}\n"
            for rec in emotions['recommendations'][:2]:
                output += f"  {rec}\n"
        
        return output


# Quick access functions
def audit(text: str) -> str:
    """Quick thinking audit"""
    enhancer = CognitiveEnhancement()
    return enhancer.thinking_audit(text)

def trade_check(symbol: str, action: str, reasoning: str) -> str:
    """Quick trade decision check"""
    enhancer = CognitiveEnhancement()
    analysis = enhancer.analyze_trade_decision(symbol, action, reasoning)
    
    output = f"🎯 TRADE ANALYSIS: {action} {symbol}\n{'='*60}\n"
    output += f"Cognitive Risk Score: {analysis['cognitive_risk_score']}/100\n\n"
    output += f"{analysis['trade_recommendation']}\n\n"
    
    if analysis['trade_warnings']:
        output += "⚠️ WARNINGS:\n"
        for w in analysis['trade_warnings']:
            output += f"  {w}\n"
    
    return output

def reframe(thought: str) -> str:
    """Quick reframe"""
    return reframe_thought(thought)


# Demo
if __name__ == "__main__":
    print("="*70)
    print("🧠 COGNITIVE ENHANCEMENT SYSTEM")
    print("="*70)
    print()
    
    enhancer = CognitiveEnhancement()
    
    # Test thinking audit
    test_thought = "I have to buy this stock right now. It's definitely going to moon. I've already lost so much on other trades, I need to make it back."
    print(audit(test_thought))
    print()
    
    # Test trade check
    print(trade_check("GME", "BUY", "My gut says this is the bottom. I'm certain it will pump. Everyone on Reddit is buying."))
    print()
    
    # Test reframe
    print(reframe("This trade is a disaster. I'm a terrible trader. I'll never succeed."))
    print()
    
    print("="*70)
    print("✅ Cognitive enhancement system ready")
    print("="*70)
