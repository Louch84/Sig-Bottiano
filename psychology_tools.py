#!/usr/bin/env python3
"""
Psychology Tools Module
Cognitive behavioral tools, bias detection, thinking modes, emotional intelligence
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class ThinkingMode(Enum):
    """Kahneman's System 1 vs System 2"""
    SYSTEM_1 = "fast"  # Automatic, intuitive, emotional
    SYSTEM_2 = "slow"  # Deliberate, analytical, logical

class CognitiveBias(Enum):
    """Common cognitive biases"""
    CONFIRMATION = "confirmation_bias"
    ANCHORING = "anchoring_bias"
    AVAILABILITY = "availability_heuristic"
    SUNK_COST = "sunk_cost_fallacy"
    OVERCONFIDENCE = "overconfidence_bias"
    RECENCY = "recency_bias"
    HINDSIGHT = "hindsight_bias"
    SURVIVORSHIP = "survivorship_bias"
    DUNNING_KRUGER = "dunning_kruger_effect"
    LOSS_AVERSION = "loss_aversion"

@dataclass
class BiasCheck:
    """Result of bias detection"""
    bias_type: CognitiveBias
    confidence: float  # 0-1
    description: str
    mitigation: str
    triggered_keywords: List[str]

@dataclass
class CBTAnalysis:
    """Cognitive Behavioral Therapy analysis result"""
    distorted_thought: str
    distortion_type: str
    evidence_for: List[str]
    evidence_against: List[str]
    balanced_thought: str
    action_step: str

class PsychologyTools:
    """
    Comprehensive psychology and reasoning enhancement toolkit
    """
    
    # Bias detection patterns
    BIAS_PATTERNS = {
        CognitiveBias.CONFIRMATION: {
            'keywords': ['always knew', 'told you so', 'obviously', 'clearly', 'definitely will',
                        'proves me right', 'confirms my', 'as expected', 'just as I thought'],
            'description': 'Seeking information that confirms existing beliefs while ignoring contradictory evidence',
            'mitigation': 'Actively seek disconfirming evidence. Consider the opposite viewpoint.'
        },
        CognitiveBias.ANCHORING: {
            'keywords': ['started at', 'originally', 'first price', 'initially', 'entry was',
                        'bought at', 'original target', 'initially thought'],
            'description': 'Over-relying on first piece of information encountered',
            'mitigation': 'Consider multiple reference points. Re-evaluate based on current data only.'
        },
        CognitiveBias.SUNK_COST: {
            'keywords': ['already invested', 'put so much', 'can\'t give up now', 'too much to lose',
                        'held this long', 'waited this long', 'already down'],
            'description': 'Continuing due to past investment rather than future potential',
            'mitigation': 'Decision should be based on future prospects, not past costs. Ask: "If I didn\'t own this today, would I buy it?"'
        },
        CognitiveBias.OVERCONFIDENCE: {
            'keywords': ['certain', 'guaranteed', 'can\'t lose', 'sure thing', 'absolutely',
                        'without a doubt', '100%', 'impossible to fail', 'easy money'],
            'description': 'Excessive confidence in own knowledge or abilities',
            'mitigation': 'Consider base rates. What percentage of similar situations succeeded? Plan for being wrong.'
        },
        CognitiveBias.LOSS_AVERSION: {
            'keywords': ['can\'t take the loss', 'hate losing', 'afraid to sell', 'don\'t want to realize',
                        'rather hold than lose', 'scared to take the hit'],
            'description': 'Preference for avoiding losses over acquiring gains (losses feel ~2x as painful)',
            'mitigation': 'Set stop losses mechanically. Paper trade to detach emotionally. Remember: small losses are tuition, big losses are disasters.'
        },
        CognitiveBias.RECENCY: {
            'keywords': ['just happened', 'recently', 'last few days', 'trending now',
                        'latest', 'current momentum', 'hot right now'],
            'description': 'Weighting recent events more heavily than historical data',
            'mitigation': 'Look at longer timeframes. Ask: "What does 1-year vs 1-day data show?"'
        },
        CognitiveBias.DUNNING_KRUGER: {
            'keywords': ['it\'s simple', 'easy to predict', 'anyone can see', 'basic analysis',
                        'just buy and hold', 'obvious pattern', 'clear trend'],
            'description': 'Overestimating ability due to lack of knowledge about complexity',
            'mitigation': 'Study failures, not just successes. Recognize market complexity. Stay humble.'
        }
    }
    
    # CBT Cognitive Distortions
    CBT_DISTORTIONS = {
        'all_or_nothing': {
            'patterns': ['always', 'never', 'every time', 'completely', 'totally', 'utter failure'],
            'description': 'Seeing things in black-and-white categories',
            'reframe': 'Look for the gray area. Is it really "always" or just "often"?'
        },
        'catastrophizing': {
            'patterns': ['disaster', 'ruined', 'devastating', 'worst', 'terrible', 'horrific'],
            'description': 'Expecting the worst possible outcome',
            'reframe': 'What\'s the most likely outcome? What could you do if the worst happened?'
        },
        'mind_reading': {
            'patterns': ['they think', 'everyone knows', 'people believe', 'market wants'],
            'description': 'Assuming you know what others think without evidence',
            'reframe': 'What\'s the actual evidence? What else could they be thinking?'
        },
        'should_statements': {
            'patterns': ['should', 'must', 'ought to', 'have to', 'need to', 'supposed to'],
            'description': 'Rigid rules about how things "should" be',
            'reframe': 'Change "should" to "could" or "prefer." Flexible thinking creates better outcomes.'
        },
        'emotional_reasoning': {
            'patterns': ['feels like', 'gut says', 'intuition tells me', 'vibe is'],
            'description': 'Assuming feelings reflect reality',
            'reframe': 'Feelings are data, not facts. What does the objective evidence show?'
        },
        'fortune_telling': {
            'patterns': ['will definitely', 'going to crash', 'sure to pump', 'inevitably',
                        'destined to', 'bound to'],
            'description': 'Predicting negative outcomes as certainties',
            'reframe': 'Predictions are probabilities, not certainties. What\'s the confidence interval?'
        }
    }
    
    def analyze_thinking_mode(self, user_input: str, context: str = "") -> Dict:
        """
        Analyze whether user is using System 1 (fast) or System 2 (slow) thinking
        """
        system_1_indicators = [
            'gut feeling', 'feels right', 'instinct', 'intuition', 'vibe',
            'obviously', 'clearly', 'definitely', 'sure', 'certain',
            'immediately', 'right away', 'quick', 'fast', 'snap decision'
        ]
        
        system_2_indicators = [
            'analyze', 'consider', 'evaluate', 'data shows', 'evidence',
            'research', 'study', 'calculate', 'compare', 'weigh',
            'pros and cons', 'on the other hand', 'alternative view',
            'what if', 'scenario', 'probability', 'statistics'
        ]
        
        input_lower = user_input.lower()
        
        s1_score = sum(1 for indicator in system_1_indicators if indicator in input_lower)
        s2_score = sum(1 for indicator in system_2_indicators if indicator in input_lower)
        
        if s1_score > s2_score:
            mode = ThinkingMode.SYSTEM_1
            recommendation = "🧠 You're using FAST thinking (System 1). Consider slowing down. Ask: What data supports this? What's the opposite view?"
        elif s2_score > s1_score:
            mode = ThinkingMode.SYSTEM_2
            recommendation = "🧠 You're using SLOW thinking (System 2). Good analysis mode. Ensure you're not overthinking or analysis paralysis."
        else:
            mode = None
            recommendation = "🧠 Thinking mode unclear. Consider: Are you reacting emotionally or analyzing objectively?"
        
        return {
            'mode': mode.value if mode else 'unclear',
            'system_1_score': s1_score,
            'system_2_score': s2_score,
            'recommendation': recommendation,
            'triggers_s1': [i for i in system_1_indicators if i in input_lower][:3],
            'triggers_s2': [i for i in system_2_indicators if i in input_lower][:3]
        }
    
    def detect_biases(self, user_input: str, context: str = "") -> List[BiasCheck]:
        """
        Detect cognitive biases in user input
        """
        detected_biases = []
        input_lower = user_input.lower()
        
        for bias_type, data in self.BIAS_PATTERNS.items():
            triggered_keywords = []
            for keyword in data['keywords']:
                if keyword in input_lower:
                    triggered_keywords.append(keyword)
            
            if triggered_keywords:
                # Calculate confidence based on number of triggers
                confidence = min(0.95, len(triggered_keywords) * 0.3 + 0.2)
                
                detected_biases.append(BiasCheck(
                    bias_type=bias_type,
                    confidence=confidence,
                    description=data['description'],
                    mitigation=data['mitigation'],
                    triggered_keywords=triggered_keywords
                ))
        
        # Sort by confidence
        detected_biases.sort(key=lambda x: x.confidence, reverse=True)
        return detected_biases[:3]  # Return top 3
    
    def cbt_reframe(self, negative_thought: str, context: str = "") -> CBTAnalysis:
        """
        Apply CBT techniques to reframe negative/distorted thinking
        """
        thought_lower = negative_thought.lower()
        
        # Identify distortion type
        distortion_type = None
        reframe_strategy = None
        
        for distortion, data in self.CBT_DISTORTIONS.items():
            for pattern in data['patterns']:
                if pattern in thought_lower:
                    distortion_type = distortion
                    reframe_strategy = data['reframe']
                    break
            if distortion_type:
                break
        
        if not distortion_type:
            distortion_type = "general_negative"
            reframe_strategy = "Examine the evidence. Is this thought helpful or accurate?"
        
        # Generate evidence (simplified - would be more sophisticated in production)
        evidence_for = ["Initial assessment suggests concern is valid"]
        evidence_against = ["Past similar situations resolved successfully"]
        
        # Create balanced thought
        balanced_thought = f"While {negative_thought}, it's also true that {reframe_strategy.lower()}"
        
        # Action step
        action_step = f"Next step: {reframe_strategy} Write down 3 pieces of evidence before deciding."
        
        return CBTAnalysis(
            distorted_thought=negative_thought,
            distortion_type=distortion_type,
            evidence_for=evidence_for,
            evidence_against=evidence_against,
            balanced_thought=balanced_thought,
            action_step=action_step
        )
    
    def emotional_check_in(self, text: str) -> Dict:
        """
        Simple emotional state detection
        """
        emotion_keywords = {
            'fear': ['scared', 'afraid', 'terrified', 'worried', 'anxious', 'panic', 'nervous'],
            'anger': ['angry', 'mad', 'furious', 'pissed', 'frustrated', 'annoyed', 'irritated'],
            'sadness': ['sad', 'depressed', 'down', 'disappointed', 'discouraged', 'hopeless'],
            'excitement': ['excited', 'pumped', 'hyped', 'thrilled', 'eager', 'enthusiastic'],
            'greed': ['greedy', 'fomo', 'miss out', 'everyone else', 'get rich quick'],
            'overconfidence': ['invincible', 'can\'t lose', 'genius', 'master', 'unstoppable']
        }
        
        detected_emotions = []
        text_lower = text.lower()
        
        for emotion, keywords in emotion_keywords.items():
            if any(kw in text_lower for kw in keywords):
                detected_emotions.append(emotion)
        
        recommendations = {
            'fear': "⚠️ Fear detected. Consider reducing position size. Fear leads to panic selling.",
            'anger': "⚠️ Anger detected. Step away. Angry decisions are usually bad decisions.",
            'sadness': "💙 Sadness detected. It's okay to take a break. Markets will be here tomorrow.",
            'excitement': "⚡ Excitement detected. Good energy! But watch for overtrading.",
            'greed': "🚨 Greed/FOMO detected. Remember: there's always another trade.",
            'overconfidence': "⚠️ Overconfidence detected. Time to review your risk management."
        }
        
        return {
            'detected_emotions': detected_emotions,
            'recommendations': [recommendations.get(e, "") for e in detected_emotions if e in recommendations],
            'advice': "Strong emotions + trading = poor decisions. Consider waiting until emotions settle."
        }
    
    def generate_psychological_profile(self, trading_history: List[Dict]) -> Dict:
        """
        Generate psychological profile based on trading patterns
        (Simplified - would use actual trade data)
        """
        return {
            'risk_tolerance': 'moderate',  # Would calculate from position sizes
            'emotional_triggers': ['fomo', 'revenge_trading'],  # Would detect from timestamps
            'cognitive_strengths': ['analytical', 'patient'],  # Would identify from winning trades
            'cognitive_weaknesses': ['holding_losers', 'cutting_winners'],  # Would identify from patterns
            'recommended_focus': 'Work on letting winners run and cutting losses quickly'
        }


# Convenience functions for quick use
def check_thinking(text: str) -> str:
    """Quick check of thinking mode"""
    tools = PsychologyTools()
    result = tools.analyze_thinking_mode(text)
    return result['recommendation']

def check_bias(text: str) -> List[str]:
    """Quick bias check"""
    tools = PsychologyTools()
    biases = tools.detect_biases(text)
    if not biases:
        return ["✅ No major biases detected in this thinking."]
    return [f"⚠️ {b.bias_type.value.replace('_', ' ').title()}: {b.mitigation}" for b in biases]

def reframe_thought(thought: str) -> str:
    """Quick CBT reframe"""
    tools = PsychologyTools()
    result = tools.cbt_reframe(thought)
    return f"💭 Reframe: {result.balanced_thought}\n🎯 Action: {result.action_step}"


# Demo
if __name__ == "__main__":
    tools = PsychologyTools()
    
    print("="*70)
    print("🧠 PSYCHOLOGY TOOLS DEMO")
    print("="*70)
    print()
    
    # Test thinking mode analysis
    test_thought = "My gut feeling says this will definitely pump. I'm certain."
    print(f"Input: '{test_thought}'")
    result = tools.analyze_thinking_mode(test_thought)
    print(f"Thinking Mode: {result['mode']}")
    print(f"Recommendation: {result['recommendation']}")
    print()
    
    # Test bias detection
    test_bias = "I've already invested so much, I can't give up now. It should go up."
    print(f"Input: '{test_bias}'")
    biases = tools.detect_biases(test_bias)
    for bias in biases:
        print(f"⚠️ Detected: {bias.bias_type.value}")
        print(f"   Confidence: {bias.confidence:.0%}")
        print(f"   Mitigation: {bias.mitigation}")
    print()
    
    # Test CBT reframe
    test_negative = "This trade is a complete disaster. I'll never win."
    print(f"Input: '{test_negative}'")
    cbt_result = tools.cbt_reframe(test_negative)
    print(f"Distortion: {cbt_result.distortion_type}")
    print(f"Balanced Thought: {cbt_result.balanced_thought}")
    print(f"Action: {cbt_result.action_step}")
    print()
    
    print("="*70)
    print("✅ Psychology tools operational")
    print("="*70)
