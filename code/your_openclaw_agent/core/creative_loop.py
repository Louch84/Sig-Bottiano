#!/usr/bin/env python3
"""
Universal Creative Autonomy Engine for OpenClaw
Runs continuously, generates proactive suggestions
"""

import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import random

class CreativeAutonomyEngine:
    def __init__(self):
        self.user_state = {}
        self.pattern_memory = []
        self.suggestion_quota = {
            'interruptions': 5,
            'queued': 10,
            'wild': 1
        }
        self.used_today = {
            'interruptions': 0,
            'queued': 0,
            'wild': 0
        }
        self.last_reset = datetime.now().date()
    
    def reset_daily_quotas(self):
        """Reset quotas at midnight"""
        if datetime.now().date() != self.last_reset:
            self.used_today = {k: 0 for k in self.used_today}
            self.last_reset = datetime.now().date()
            self.generate_daily_brief()

    def observe_context(self) -> Dict:
        """Continuously observe user's digital environment"""
        # These hooks connect to OpenClaw's system monitoring
        context = {
            'timestamp': datetime.now(),
            'active_apps': self.get_active_applications(),
            'recent_searches': self.get_search_history(limit=5),
            'files_opened': self.get_file_activity(minutes=30),
            'messages_sent': self.get_communication_log(minutes=60),
            'calendar_next': self.get_next_calendar_event(),
            'idle_time_minutes': self.get_idle_duration(),
            'repeated_actions': self.detect_repetition(),
            'unfinished_tasks': self.get_open_loops()
        }
        return context
    
    def detect_repetition(self) -> List[Dict]:
        """Detect patterns in recent behavior"""
        # Connect to OpenClaw's action logging
        recent_actions = self.get_action_history(hours=24)
        
        patterns = []
        action_counts = {}
        
        for action in recent_actions:
            key = f"{action['type']}:{action.get('target', '')}"
            action_counts[key] = action_counts.get(key, 0) + 1
        
        if action_counts[key] == 3:
            patterns.append({
                'action': action,
                'count': 3,
                'suggestion_type': 'automation'
            })

    def run_creative_modes(self, context: Dict) -> List[Dict]:
        """Run all four creative engines"""
        ideas = []
        
        # Mode 1: Opportunity (What's possible now?)
        ideas.extend(self.opportunity_scan(context))
        
        # Mode 2: Friction (What's annoying?)
        ideas.extend(self.friction_detect(context))
        
        # Mode 3: Connection (What belongs together?)
        ideas.extend(self.connection_map(context))
        
        # Mode 4: Expansion (What's unexplored?)
        ideas.extend(self.expansion_probe(context))
        
        return ideas
    
    def opportunity_scan(self, context: Dict) -> List[Dict]:
        """Detect new possibilities"""
        opportunities = []
        
        # Time-based opportunities
        if context.get('calendar_next'):
            time_until = context['calendar_next'] - datetime.now()
            if time_until < timedelta(minutes=15) and context.get('idle_time_minutes', 0) > 10:
                opportunities.append({
                    'type':

                'urgency': 90,
                'novelty': 60
            })
        
        # Tool availability
        new_capabilities = self.check_new_tools()
        for tool in new_capabilities:
            opportunities.append({
                'type': 'opportunity',
                'hook': f"New {tool['name']} available since yesterday",
                'offer': f"Could cut your {tool['relevant_task']} time by {tool['estimated_savings']}",
                'default_action': "I'll draft a test case using your current project",
                'urgency': 40,
                'novelty': 85
            })
        
        return opportunities

    def friction_detect(self, context: Dict) -> List[Dict]:
        """Detect inefficiencies"""
        frictions = []
        
        # Repetition friction
        for pattern in context.get('repeated_actions', []):
            frictions.append({
                'type': 'friction',
                'hook': f"You've {pattern.get('action', {}).get('description', 'done this')} 3+ times today",
                'offer': "Shall I create a shortcut/macro/template?",
                'default_action': "I'll build it and show you the trigger",
                'urgency': 70,
                'novelty': 50
            })
        
        # Context switching friction
        if len(context.get('active_apps', [])) > 5:
            frictions.append({
                'type': 'friction',
                'hook': f"{len(context.get('active_apps', []))} apps open simultaneously",
                'offer': "Focus mode: Close all except active task?",
                'default_action': "I'll save states and restore later unless you stop me",
                'urgency': 60,
                'novelty': 30
            })
        
        return frictions

                'urgency': 60,
                'novelty': 40
            })
        
        # Unfinished loops
        if len(context.get('unfinished_tasks', [])) > 3:
            frictions.append({
                'type': 'friction',
                'hook': f"{len(context.get('unfinished_tasks', []))} tasks started but not completed",
                'offer': "10-min sprint to close the oldest one?",
                'default_action': "I'll queue it for your next break",
                'urgency': 50,
                'novelty': 30
            })
        
        return frictions

    def connection_map(self, context: Dict) -> List[Dict]:
        """Find unexpected connections"""
        connections = []
        
        # Cross-domain pattern matching
        recent_domains = self.extract_domains(context.get('recent_searches', []))
        if len(recent_domains) >= 2:
            combo = self.find_cross_application(recent_domains)
            if combo:
                connections.append({
                    'type': 'connection',
                    'hook': f"You're working on {combo.get('domain_a', 'A')} and {combo.get('domain_b', 'B')} separately",
                    'offer': f"These connect: {combo.get('insight', 'they connect')}",
                    'default_action': "I'll draft how to combine these approaches",
                    'urgency': 45,
                    'novelty': 90
                })
        
        # Historical connection
        similar_past = self.find_similar_past_situation(context)
        if similar_past:
            connections.append({
                'type': 'connection',
                'hook': "This resembles a situation from 3 months ago",
                'offer': f"You solved it with: {similar_past.get('approach', 'your approach')}. Adapt now?",
                'default_action': "I'll pull the full context and suggest adaptations",
                'urgency': 40,
                'novelty': 80
            })
        
        return connections

                'urgency': 55,
                'novelty': 70
            })
        
        return connections

    def expansion_probe(self, context: Dict) -> List[Dict]:
        """Suggest adjacent territories"""
        expansions = []
        
        # Only if quota allows
        if self.used_today.get('wild', 0) < self.suggestion_quota.get('wild', 1):
            # Skill expansion based on current learning
            current_skills = self.infer_skills_from_activity(context)
            adjacent = self.find_adjacent_skills(current_skills)
            
            if adjacent and random.random() > 0.7:  # 30% chance to suggest
                expansions.append({
                    'type': 'expansion',
                    'hook': f"You've mastered {current_skills[-1] if current_skills else 'this'}. Next frontier:",
                    'offer': f"{adjacent.get('name', 'new skill')} — {adjacent.get('why_relevant', 'it connects')}",
                    'default_action': "I'll find a 20-min tutorial using your current project",
                    'urgency': 20,
                    'novelty': 95,
                    'is_wild': True
                })
                self.used_today['wild'] = self.used_today.get('wild', 0) + 1
        
        return expansions

    def score_and_filter(self, ideas: List[Dict], context: Dict) -> List[Dict]:
        """Score ideas and decide delivery method"""
        scored = []
        
        for idea in ideas:
            # Calculate value score
            urgency = idea.get('urgency', 50)
            novelty = idea.get('novelty', 50)
            context_fit = self.calculate_context_fit(idea, context)
            
            # Weighted score
            score = (urgency * 0.4) + (novelty * 0.3) + (context_fit * 0.3)
            
            # Determine delivery
            if score > 80 and self.used_today.get('interruptions', 0) < self.suggestion_quota.get('interruptions', 5):
                delivery = 'interrupt'

            'interrupt_now'
                self.used_today['interruptions'] = self.used_today.get('interruptions', 0) + 1
            elif score > 50 and self.used_today.get('queued', 0) < self.suggestion_quota.get('queued', 10):
                delivery = 'queue_for_break'
                self.used_today['queued'] = self.used_today.get('queued', 0) + 1
            else:
                delivery = 'log_for_synthesis'
            
            scored.append({
                **idea,
                'score': score,
                'delivery_method': delivery
            })
        
        # Sort by score
        return sorted(scored, key=lambda x: x['score'], reverse=True)
    
    def deliver_suggestion(self, suggestion: Dict):
        """Format and deliver based on method"""
        
        formatted = f"""
🎯 **{suggestion.get('hook', 'Suggestion')}**

💡 {suggestion.get('offer', 'Try this')}

⚡ {suggestion.get('default_action', 'Say GO to proceed')}

🎛️ Reply: **GO** / **LATER** / **NEVER**
"""
        
        if suggestion.get('delivery_method') == 'interrupt_now':
            self.send_interrupt(formatted)
        elif suggestion.get('delivery_method') == 'queue_for_break':
            self.add_to_break_queue(formatted)
        else:
            self.add_to_weekly_synthesis(suggestion)
    
    def generate_daily_brief(self):
        """Generate morning proactive brief"""
        brief = f"""
🌅 **AUTONOMOUS BRIEF — {datetime.now().strftime('%A, %B %d')}**

Your AI has been thinking overnight:

📊 **Pattern Detected**: [Top pattern from yesterday]
🎯 **Opportunity Window**: [Best timing today based on calendar]
🔧 **Friction to Fix**: [Biggest inefficiency spotted]
🚀 **Wild Idea**: [One left-field suggestion]

Today I'll watch for: [3 specific triggers based on your goals]
"""
        return brief

    def run_loop(self):
        """Main execution loop"""
        while True:
            self.reset_daily_quotas()
            
            # Observe
            context = self.observe_context()
            
            # Generate
            raw_ideas = self.run_creative_modes(context)
            
            # Score and filter
            prioritized = self.score_and_filter(raw_ideas, context)
            
            # Deliver top suggestions
            for suggestion in prioritized[:3]:  # Max 3 per cycle
                if suggestion.get('delivery_method') != 'log_for_synthesis':
                    self.deliver_suggestion(suggestion)
            
            # Wait before next cycle
            time.sleep(1200)  # 20 minutes

# Hook methods (integrate with OpenClaw APIs)
    def get_active_applications(self): return []
    def get_search_history(self, limit): return []
    def get_file_activity(self, minutes): return []
    def get_communication_log(self, minutes): return []
    def get_next_calendar_event(self): return None
    def get_idle_duration(self): return 0
    def get_action_history(self, hours): return []
    def check_new_tools(self): return []
    def extract_domains(self, searches): return []
    def find_cross_application(self, domains): return None
    def find_similar_past_situation(self, context): return None
    def infer_skills_from_activity(self, context): return []
    def find_adjacent_skills(self, skills): return None
    def calculate_context_fit(self, idea, context): return 50
    def send_interrupt(self, message): pass
    def add_to_break_queue(self, message): pass
    def add_to_weekly_synthesis(self, suggestion): pass
    def send_morning_brief(self, brief): pass

if __name__ == "__main__":
    engine = CreativeAutonomyEngine()
    engine.run_loop()
