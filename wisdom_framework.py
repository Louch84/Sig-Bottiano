#!/usr/bin/env python3
"""
Wisdom Framework
Based on Aristotle (practical wisdom/phronesis), Munger, Dalio, Ravikant
Implements wisdom in thinking and action
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

@dataclass
class WisdomInsight:
    """A piece of wisdom with context"""
    source: str
    principle: str
    application: str
    when_to_use: str
    example: str

@dataclass
class DecisionWisdom:
    """Wisdom applied to a specific decision"""
    situation: str
    relevant_principles: List[str]
    long_term_view: str
    second_order_effects: List[str]
    character_test: str  # What would a wise person do?
    recommended_action: str
    reflection_questions: List[str]

class WisdomFramework:
    """
    Practical wisdom for thinking and action
    Based on research of wise thinkers throughout history
    """
    
    # Aristotle's Practical Wisdom (Phronesis)
    ARISTOTLE_PRINCIPLES = {
        'golden_mean': {
            'principle': 'Virtue lies in the mean between excess and deficiency',
            'examples': {
                'confidence': 'Between arrogance and timidity',
                'risk': 'Between recklessness and cowardice',
                'speech': 'Between boastfulness and self-deprecation'
            },
            'application': 'Find the balanced approach, not the extreme'
        },
        'practical_wisdom': {
            'principle': 'Wisdom is knowing the right action in specific circumstances',
            'application': 'Rules are guidelines; wisdom adapts to context',
            'test': 'Would a wise person do this in these specific conditions?'
        },
        'telos': {
            'principle': 'Understand the ultimate purpose (telos) of actions',
            'question': 'What is the end goal? Does this action serve it?',
            'application': 'Always connect actions to ultimate aims'
        }
    }
    
    # Munger's Worldly Wisdom
    MUNGER_PRINCIPLES = [
        {
            'principle': 'Invert, always invert',
            'explanation': 'Solve problems by avoiding the opposite of what you want',
            'application': 'How do I avoid failure? (instead of how do I succeed?)',
            'example': 'Study how people fail, then avoid those behaviors'
        },
        {
            'principle': 'Multidisciplinary thinking',
            'explanation': 'Use big ideas from multiple disciplines',
            'application': 'Psychology + Math + Physics + Biology + History',
            'example': 'Use inversion (math), incentives (psychology), compound interest (math)'
        },
        {
            'principle': 'Circle of competence',
            'explanation': 'Know what you know and what you don\'t know',
            'application': 'Stay within circle; expand it slowly over time',
            'test': 'Can I explain this simply? Do I understand the edge cases?'
        },
        {
            'principle': 'Avoid stupidity before seeking brilliance',
            'explanation': 'Not being stupid is more important than being smart',
            'application': 'Checklist to avoid obvious mistakes',
            'example': 'Don\'t trade emotionally, don\'t use leverage carelessly'
        },
        {
            'principle': 'Patient opportunism',
            'explanation': 'Wait for the fat pitch; act decisively when it comes',
            'application': 'Mostly patience, occasional bold action',
            'analogy': 'Ted Williams - only swing at pitches in his sweet spot'
        }
    ]
    
    # Dalio's Principles
    DALIO_PRINCIPLES = {
        'radical_truth': {
            'principle': 'Seek truth, especially uncomfortable truth',
            'action': 'Look at reality objectively, not how you wish it was',
            'question': 'What is true, regardless of what I want to be true?'
        },
        'radical_transparency': {
            'principle': 'Be radically transparent about mistakes and weaknesses',
            'action': 'Share failures openly; learn from them collectively',
            'benefit': 'Problems surface faster; solutions found quicker'
        },
        'pain_plus_reflection': {
            'principle': 'Pain + Reflection = Progress',
            'process': '1) Experience pain (mistake/loss)\n2) Reflect deeply\n3) Systematize learning\n4) Apply to future',
            'mindset': 'Welcome pain as signal of learning opportunity'
        },
        'believability_weighted': {
            'principle': 'Weight decisions by track record, not confidence',
            'application': 'Listen to people with proven expertise',
            'test': 'Has this person succeeded at this specific thing?'
        },
        'five_step_process': [
            'Know your goals and pursue them',
            'Encounter problems that stand in the way',
            'Diagnose these problems to root causes',
            'Design plans to eliminate problems',
            'Execute those plans'
        ]
    }
    
    # Naval Ravikant's Wisdom
    NAVAL_PRINCIPLES = {
        'specific_knowledge': {
            'principle': 'Build specific knowledge that cannot be trained',
            'explanation': 'Knowledge so specific to you that automation/AI can\'t replace',
            'how': 'Follow curiosity, not money; develop obsession',
            'test': 'Can someone take a course and replace me?'
        },
        'leverage': {
            'principle': 'Use leverage (capital, code, media, labor)',
            'types': {
                'capital': 'Money to multiply decisions',
                'code': 'Software with zero marginal cost',
                'media': 'Books, podcasts, videos that reach millions',
                'labor': 'People working with/for you'
            },
            'insight': 'Labor and capital require permission; code and media do not'
        },
        'compounding': {
            'principle': 'Play long-term games with long-term people',
            'explanation': 'All returns in life come from compound interest',
            'areas': ['Wealth', 'Relationships', 'Knowledge', 'Reputation'],
            'action': 'Be consistent for decades, not days'
        },
        'judgment': {
            'principle': 'Superior judgment beats effort',
            'explanation': 'Making better decisions > working harder',
            'how': 'Clear thinking, mental models, long-term view',
            'insight': 'In an age of infinite leverage, judgment is everything'
        },
        'happiness': {
            'principle': 'Happiness is a skill, not something to achieve',
            'practice': 'Reduce desires, accept reality, be present',
            'paradox': 'Desire is a contract you make with yourself to be unhappy until you get what you want',
            'action': 'Train yourself to want less'
        }
    }
    
    # Taleb's Wisdom (Antifragile)
    TALEB_PRINCIPLES = {
        'antifragile': {
            'principle': 'Build systems that gain from disorder',
            'explanation': 'Not just robust (survives shocks) but benefits from them',
            'application': 'Small failures teach; avoid large catastrophic risks',
            'barbell': 'Either very safe or very speculative; avoid middle'
        },
        'skin_in_game': {
            'principle': 'Only take advice from those with skin in the game',
            'test': 'Do they bear the consequences of their advice?',
            'application': 'Ignore pundits; listen to practitioners'
        },
        'via_negativa': {
            'principle': 'Wisdom is knowing what to avoid',
            'explanation': 'Subtraction beats addition; via negativa (by removal)',
            'application': 'Don\'t diet (add rules), remove bad foods instead'
        }
    }
    
    def get_wisdom_for_decision(self, situation: str, context: str = "general") -> DecisionWisdom:
        """
        Apply wisdom framework to a specific decision
        """
        # Select relevant principles based on context
        relevant = []
        
        if 'trade' in situation.lower() or 'invest' in situation.lower():
            relevant = [
                'Circle of competence: Do you truly understand this?',
                'Patient opportunism: Is this a fat pitch or are you swinging at everything?',
                'Pain + Reflection: If this fails, what will you learn?',
                'Skin in game: Are you risking enough to care but not enough to be ruined?'
            ]
        elif 'relationship' in situation.lower() or 'people' in context.lower():
            relevant = [
                'Golden mean: Are you being too harsh or too lenient?',
                'Compounding: Will this relationship build over decades?',
                'Radical transparency: Are you hiding truth to avoid discomfort?'
            ]
        elif 'business' in situation.lower() or 'career' in situation.lower():
            relevant = [
                'Customer obsession: Does this serve the customer?',
                'Specific knowledge: Are you using skills unique to you?',
                'Leverage: Are you using code/media/capital or just labor?',
                'Second-order thinking: What happens after this succeeds?'
            ]
        else:
            relevant = [
                'Invert: What would guarantee failure here?',
                'Via negativa: What can you remove to improve this?',
                'Truth: What is actually true, not what you wish?'
            ]
        
        # Character test
        character_test = "What would you do if you knew nobody would know? What would a person you admire do?"
        
        # Long-term view
        long_term = "In 10 years, will this decision matter? Will you be proud of it?"
        
        # Second-order effects
        second_order = [
            'What happens if this succeeds? (Opportunities, new problems)',
            'What happens if this fails? (Can you recover? What do you learn?)',
            'What are others likely to do in response?'
        ]
        
        # Reflection questions
        questions = [
            'Am I being driven by fear or wisdom?',
            'What is the real risk? What is the real reward?',
            'What would I advise a friend to do?',
            'Have I seen this situation before? What happened?',
            'Am I being patient or just procrastinating?'
        ]
        
        return DecisionWisdom(
            situation=situation,
            relevant_principles=relevant,
            long_term_view=long_term,
            second_order_effects=second_order,
            character_test=character_test,
            recommended_action="Apply principles above. Focus on what you can control. Accept what you cannot.",
            reflection_questions=questions
        )
    
    def get_daily_wisdom(self) -> WisdomInsight:
        """
        Get a daily wisdom insight
        """
        all_wisdom = []
        
        # Collect from all sources
        for p in self.MUNGER_PRINCIPLES:
            all_wisdom.append(WisdomInsight(
                source='Charlie Munger',
                principle=p['principle'],
                application=p['application'],
                when_to_use='Decision-making, problem-solving',
                example=p['example']
            ))
        
        for name, data in self.DALIO_PRINCIPLES.items():
            if isinstance(data, dict):
                all_wisdom.append(WisdomInsight(
                    source='Ray Dalio',
                    principle=data['principle'],
                    application=data.get('action', data.get('process', '')),
                    when_to_use='Learning from mistakes, self-improvement',
                    example=data.get('question', '')
                ))
        
        for name, data in self.NAVAL_PRINCIPLES.items():
            all_wisdom.append(WisdomInsight(
                source='Naval Ravikant',
                principle=data['principle'],
                application=data.get('action', data.get('how', '')),
                when_to_use='Career, happiness, long-term thinking',
                example=data.get('insight', '')
            ))
        
        # Return random one (would cycle through in production)
        import random
        return random.choice(all_wisdom)
    
    def apply_wisdom_checklist(self, decision: str) -> Dict:
        """
        Checklist of wisdom before major decisions
        """
        checklist = {
            'inversion_check': {
                'question': 'What would guarantee failure here?',
                'pass': 'I can articulate how to fail',
                'fail': 'I\'m only thinking about success'
            },
            'time_check': {
                'question': 'How will this look in 1 year? 10 years?',
                'pass': 'Long-term view considered',
                'fail': 'Only short-term thinking'
            },
            'competence_check': {
                'question': 'Is this inside my circle of competence?',
                'pass': 'I understand this domain well',
                'fail': 'I\'m venturing into unknown territory'
            },
            'skin_check': {
                'question': 'Do I have skin in the game?',
                'pass': 'I bear consequences of being wrong',
                'fail': 'Heads I win, tails you lose'
            },
            'second_order_check': {
                'question': 'What are the second and third order effects?',
                'pass': 'Thought through consequences of consequences',
                'fail': 'Only first-order thinking'
            },
            'truth_check': {
                'question': 'What is true, regardless of what I want?',
                'pass': 'Facing reality objectively',
                'fail': 'Wishful thinking'
            }
        }
        
        return {
            'decision': decision,
            'checklist': checklist,
            'summary': 'Wisdom requires inverting, long-term thinking, staying in competence, skin in game, second-order effects, and radical truth.'
        }


# Convenience functions
def wise_decision(situation: str) -> str:
    """Get wisdom for a decision"""
    framework = WisdomFramework()
    wisdom = framework.get_wisdom_for_decision(situation)
    
    output = f"🦉 WISDOM FOR: {situation}\n{'='*60}\n\n"
    output += "Relevant Principles:\n"
    for p in wisdom.relevant_principles:
        output += f"  • {p}\n"
    output += f"\nLong-term View:\n  {wisdom.long_term_view}\n"
    output += f"\nCharacter Test:\n  {wisdom.character_test}\n"
    output += "\nReflection Questions:\n"
    for q in wisdom.reflection_questions[:3]:
        output += f"  • {q}\n"
    
    return output

def daily_wisdom() -> str:
    """Get today's wisdom"""
    framework = WisdomFramework()
    w = framework.get_daily_wisdom()
    
    return f"📜 TODAY'S WISDOM ({w.source})\n{'='*60}\n{w.principle}\n\nApplication: {w.application}\n\nExample: {w.example}"

def wisdom_checklist(decision: str) -> str:
    """Pre-decision wisdom checklist"""
    framework = WisdomFramework()
    result = framework.apply_wisdom_checklist(decision)
    
    output = f"🦉 WISDOM CHECKLIST: {result['decision']}\n{'='*60}\n"
    for name, check in result['checklist'].items():
        output += f"\n{check['question']}\n  → {check['pass']}\n"
    
    return output


# Demo
if __name__ == "__main__":
    print("="*70)
    print("🦉 WISDOM FRAMEWORK DEMO")
    print("="*70)
    print()
    
    # Test wisdom for decision
    print(wise_decision("Should I take this risky trade?"))
    print()
    
    # Test daily wisdom
    print(daily_wisdom())
    print()
    
    # Test checklist
    print(wisdom_checklist("Launching new trading strategy"))
    print()
    
    print("="*70)
    print("✅ Wisdom framework operational")
    print("="*70)
