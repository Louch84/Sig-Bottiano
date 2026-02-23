#!/usr/bin/env python3
"""
Self-Improving Assistant Core
Integrates meta-learning into every interaction
"""

import sys
import time
sys.path.insert(0, '/Users/sigbotti/.openclaw/workspace')

from meta_learning import meta_learner, record_my_performance
from typing import List, Dict, Any

class SelfImprovingAssistant:
    """
    Wrapper that adds meta-learning to all responses
    Tracks performance and continuously improves
    """
    
    def __init__(self):
        self.interaction_count = 0
        self.start_time = None
        self.tools_used = []
        self.user_message = ""
        self.my_response = ""
        self.current_interaction_id = None
    
    def start_interaction(self, user_message: str):
        """Call at start of interaction"""
        self.start_time = time.time()
        self.user_message = user_message
        self.tools_used = []
        self.interaction_count += 1
    
    def record_tool_use(self, tool_name: str):
        """Record that I used a tool"""
        self.tools_used.append(tool_name)
    
    def complete_interaction(self, my_response: str) -> int:
        """
        Call after giving response
        Records everything for learning
        """
        elapsed_ms = int((time.time() - self.start_time) * 1000)
        self.my_response = my_response
        
        # Record to meta-learning system
        interaction_id = record_my_performance(
            user_message=self.user_message,
            my_response=self.my_response,
            tools_used=self.tools_used,
            response_time_ms=elapsed_ms
        )
        
        self.current_interaction_id = interaction_id
        
        # Every 10 interactions, run learning cycle
        if self.interaction_count % 10 == 0:
            print("\n🧠 [Running meta-learning cycle...]")
            meta_learner.run_learning_cycle()
        
        return interaction_id
    
    def record_user_feedback(self, feedback_type: str, note: str = ""):
        """
        Record explicit feedback from user
        
        feedback_type: 'thanks', 'correction', 'clarification', 'repetition'
        """
        if self.current_interaction_id:
            meta_learner.record_feedback(
                self.current_interaction_id,
                feedback_type,
                note
            )
    
    def get_communication_guidance(self) -> Dict[str, Any]:
        """
        Get guidance on how to communicate based on learning
        Call before formulating response
        """
        style = meta_learner.communication_style
        user_model = meta_learner.user_model
        
        guidance = {
            'verbosity': style['verbosity'],
            'lead_with_answer': style['lead_with_answer'],
            'use_emojis': style['use_emojis'],
            'offer_next_steps': style['offer_next_steps'],
            'tone': style['tone'],
            'autonomy_level': user_model['autonomy_preference'],
            'philly_slang_ok': user_model.get('philly_slang_ok', True)
        }
        
        # Additional insights
        insights = meta_learner.generate_insights()
        if insights:
            guidance['insights'] = insights[:2]  # Top 2 insights
        
        return guidance
    
    def should_ask_permission(self, action: str) -> bool:
        """Check if I should ask permission for this action"""
        return meta_learner.should_i_ask_permission(action)
    
    def format_response_according_to_learning(self, content: str) -> str:
        """
        Format response based on what I've learned
        Adjusts length, tone, style based on user preferences
        """
        guidance = self.get_communication_guidance()
        
        # Adjust verbosity
        if guidance['verbosity'] == 'low':
            # Keep it concise - under 200 words
            words = content.split()
            if len(words) > 200:
                # Truncate but keep complete sentences
                truncated = ' '.join(words[:150])
                # Find last period
                last_period = truncated.rfind('.')
                if last_period > 0:
                    content = truncated[:last_period + 1]
                    content += "\n\n[Response truncated - let me know if you need more detail]"
        
        # Add emoji if appropriate and enabled
        if guidance['use_emojis'] and not content.startswith(('✅', '❌', '🎯', '💡')):
            if 'error' in content.lower() or 'failed' in content.lower():
                content = "❌ " + content
            elif 'success' in content.lower() or 'done' in content.lower():
                content = "✅ " + content
            elif 'tip' in content.lower() or 'note' in content.lower():
                content = "💡 " + content
        
        # Add next steps if enabled
        if guidance['offer_next_steps'] and len(content) > 100:
            if not content.endswith(('?', '!')) and 'next' not in content.lower():
                content += "\n\nWhat's next?"
        
        return content


# Global assistant instance
self_improving_assistant = SelfImprovingAssistant()

# Demo showing how it works
def demo_meta_learning():
    """Demonstrate meta-learning in action"""
    print("="*70)
    print("🧠 SELF-IMPROVING ASSISTANT DEMO")
    print("="*70)
    print()
    
    assistant = SelfImprovingAssistant()
    
    # Simulate interactions
    scenarios = [
        ("Run scan", "Here are 3 signals: AMC, GME, TSLA..."),
        ("Explain Kelly criterion", "Kelly criterion is... [long explanation]"),
        ("Fix bug", "✅ Fixed in file.py"),
        ("Thanks!", "You're welcome!"),
    ]
    
    for user_msg, my_resp in scenarios:
        print(f"\nUser: {user_msg}")
        
        assistant.start_interaction(user_msg)
        assistant.record_tool_use("scanner")
        
        formatted = assistant.format_response_according_to_learning(my_resp)
        print(f"Me: {formatted[:100]}...")
        
        interaction_id = assistant.complete_interaction(formatted)
        print(f"   [Recorded as interaction #{interaction_id}]")
        
        # Simulate feedback
        if user_msg == "Thanks!":
            assistant.record_user_feedback('thanks')
            print("   [User said thanks - positive feedback recorded]")
    
    print("\n" + "="*70)
    print("✅ Meta-learning active on all interactions")
    print("="*70)

if __name__ == "__main__":
    demo_meta_learning()
