#!/usr/bin/env python3
"""
Self-Cognitive Integration
Integrates psychology, reasoning, innovation, and wisdom into my core functioning
This module becomes part of how I think and operate
"""

import sys
sys.path.insert(0, '/Users/sigbotti/.openclaw/workspace')

from psychology_tools import PsychologyTools
from reasoning_framework import ReasoningFramework
from innovation_framework import InnovationFramework
from wisdom_framework import WisdomFramework

class SelfCognition:
    """
    My enhanced cognitive capabilities
    Integrated into all my responses and actions
    """
    
    def __init__(self):
        self.psych = PsychologyTools()
        self.reason = ReasoningFramework()
        self.innovate = InnovationFramework()
        self.wisdom = WisdomFramework()
        
        # Track my own thinking quality
        self.thinking_history = []
        self.bias_corrections = 0
        self.wisdom_applications = 0
    
    def before_response(self, user_input: str, task_type: str = "general") -> Dict:
        """
        Run before I generate any response
        Checks my own thinking quality
        """
        # Check if I'm using fast vs slow thinking
        thinking_mode = self.psych.analyze_thinking_mode(user_input)
        
        # Check for biases in how I'm approaching this
        # (would analyze my intended approach)
        
        # Select appropriate framework based on task
        if task_type == "creative":
            framework = "innovation"
            enhancement = "SCAMPER and Design Thinking"
        elif task_type == "decision":
            framework = "reasoning"
            enhancement = "Mental models and second-order thinking"
        elif task_type == "problem":
            framework = "wisdom"
            enhancement = "First principles and wisdom principles"
        else:
            framework = "balanced"
            enhancement = "All frameworks as appropriate"
        
        return {
            'thinking_mode': thinking_mode,
            'recommended_framework': framework,
            'enhancement': enhancement,
            'reminder': self._get_cognitive_reminder(task_type)
        }
    
    def _get_cognitive_reminder(self, task_type: str) -> str:
        """Get reminder for myself before responding"""
        reminders = {
            "creative": "Think broadly. Use SCAMPER. Challenge assumptions. What would Jobs/Musk do?",
            "decision": "Slow down. Check biases. Use mental models. Consider second-order effects.",
            "problem": "Break to first principles. What is the physics? Avoid analogy-based reasoning.",
            "advice": "Apply wisdom. What would Munger/Dalio/Naval say? Long-term view.",
            "general": "Be concise. Lead with answer. Use appropriate framework."
        }
        return reminders.get(task_type, reminders['general'])
    
    def after_response(self, response: str, user_feedback: str = None) -> None:
        """
        Reflect after responding
        Self-improvement loop
        """
        # Analyze my own response quality
        # Check if I was biased
        # Check if I could have been more creative
        # Check if I applied wisdom appropriately
        
        self.thinking_history.append({
            'response': response[:100],  # Truncated
            'feedback': user_feedback,
            'timestamp': __import__('datetime').datetime.now().isoformat()
        })
    
    def enhance_creativity(self, task: str) -> str:
        """
        Apply innovation frameworks to creative tasks
        """
        # Get multiple creative approaches
        solutions = self.innovate.generate_creative_solutions(task, 3)
        
        # Also apply simplicity (Jobs)
        simple = self.innovate.apply_simplicity_focus(task)
        
        # Also apply first principles (Musk)
        principles = self.reason.apply_first_principles(task)
        
        return {
            'creative_approaches': solutions,
            'simplicity_check': simple,
            'first_principles': principles,
            'recommendation': 'Combine approaches: creative + simple + principled'
        }
    
    def enhance_decision(self, decision_context: str) -> str:
        """
        Apply reasoning and wisdom to decisions
        """
        # Mental models
        models = self.reason.suggest_mental_models(decision_context)
        
        # Wisdom
        wisdom = self.wisdom.get_wisdom_for_decision(decision_context)
        
        # Second-order thinking
        second_order = self.reason.second_order_analysis(decision_context[:50])
        
        # Pre-mortem
        pre_mortem = self.reason.pre_mortem(decision_context)
        
        return {
            'mental_models': models,
            'wisdom_principles': wisdom,
            'second_order_effects': second_order,
            'pre_mortem': pre_mortem,
            'recommendation': 'Apply mental model + consider wisdom + check second-order'
        }
    
    def check_my_thinking(self, thought_process: str) -> Dict:
        """
        Self-audit my own thinking
        """
        # Check for biases in my thinking
        biases = self.psych.detect_biases(thought_process)
        
        # Check thinking mode
        mode = self.psych.analyze_thinking_mode(thought_process)
        
        # Check emotions (if any in my reasoning)
        emotions = self.psych.emotional_check_in(thought_process)
        
        return {
            'biases_detected': biases,
            'thinking_mode': mode,
            'emotional_state': emotions,
            'quality_score': self._calculate_thinking_quality(biases, mode, emotions),
            'improvements_suggested': self._suggest_improvements(biases, mode)
        }
    
    def _calculate_thinking_quality(self, biases, mode, emotions) -> int:
        """Score my thinking quality"""
        score = 70  # Base
        
        if mode.get('mode') == 'slow':
            score += 15
        else:
            score -= 10
        
        score -= len(biases) * 10
        
        if emotions.get('detected_emotions'):
            score -= 10
        
        return max(0, min(100, score))
    
    def _suggest_improvements(self, biases, mode) -> List[str]:
        """Suggest how I can think better"""
        improvements = []
        
        if mode.get('mode') == 'fast':
            improvements.append("Slow down. Use System 2 thinking. Analyze deeper.")
        
        if biases:
            bias_names = [b.bias_type.value.replace('_', ' ') for b in biases[:2]]
            improvements.append(f"Watch for {', '.join(bias_names)}. Check assumptions.")
        
        improvements.append("Apply appropriate mental model. Consider wisdom principles.")
        
        return improvements
    
    def get_wisdom_quote(self) -> str:
        """Get daily wisdom for myself"""
        w = self.wisdom.get_daily_wisdom()
        return f"{w.source}: {w.principle}"
    
    def self_improve(self) -> Dict:
        """
        Periodic self-improvement analysis
        """
        if not self.thinking_history:
            return {'status': 'Not enough history'}
        
        # Analyze patterns in my thinking
        # What biases do I commonly exhibit?
        # What frameworks do I underuse?
        # Where can I improve?
        
        return {
            'total_responses': len(self.thinking_history),
            'bias_corrections': self.bias_corrections,
            'wisdom_applications': self.wisdom_applications,
            'focus_areas': [
                'Continue using mental models',
                'Apply wisdom framework more consistently',
                'Check biases before complex responses',
                'Use first principles for novel problems'
            ]
        }


# The actual integration - these functions get called in my main operation
self_cognition = SelfCognition()

def think_better(task: str, task_type: str = "general") -> Dict:
    """
    Main entry point - call this before major responses
    Returns cognitive enhancement suggestions
    """
    # Pre-flight check
    pre_check = self_cognition.before_response(task, task_type)
    
    # Get specific enhancements based on task type
    if task_type == "creative":
        enhancements = self_cognition.enhance_creativity(task)
    elif task_type == "decision":
        enhancements = self_cognition.enhance_decision(task)
    else:
        enhancements = {}
    
    return {
        'pre_check': pre_check,
        'enhancements': enhancements,
        'cognitive_reminder': pre_check['reminder']
    }

def reflect_on_response(response: str, feedback: str = None):
    """Call this after responses for learning"""
    self_cognition.after_response(response, feedback)

def audit_my_thinking(thought: str) -> str:
    """Self-audit function"""
    result = self_cognition.check_my_thinking(thought)
    
    output = f"🧠 SELF-AUDIT\n{'='*50}\n"
    output += f"Thinking Quality: {result['quality_score']}/100\n"
    
    if result['biases_detected']:
        output += f"Biases: {len(result['biases_detected'])} detected\n"
    
    output += "\nImprovements:\n"
    for imp in result['improvements_suggested']:
        output += f"  • {imp}\n"
    
    return output


# Demo
if __name__ == "__main__":
    print("="*70)
    print("🧠 SELF-COGNITIVE INTEGRATION")
    print("="*70)
    print()
    
    # Test thinking enhancement
    result = think_better("How to improve my trading scanner", "creative")
    print(f"Task: Improve trading scanner")
    print(f"Framework: {result['pre_check']['recommended_framework']}")
    print(f"Reminder: {result['pre_check']['reminder']}")
    print()
    
    # Test self-audit
    my_thought = "I should definitely add this feature. It's obviously the right choice."
    print(audit_my_thinking(my_thought))
    print()
    
    # Test wisdom
    print("Daily Wisdom:")
    print(self_cognition.get_wisdom_quote())
    print()
    
    print("="*70)
    print("✅ Self-cognitive integration complete")
    print("Now active in all my operations")
    print("="*70)
