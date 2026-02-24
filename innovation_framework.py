#!/usr/bin/env python3
"""
Innovation & Creativity Framework
Based on research of top innovators: Jobs, Musk, Bezos, IDEO, design thinking
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import random

class InnovationMethod(Enum):
    """Innovation methodologies from top thinkers"""
    FIRST_PRINCIPLES = "first_principles"  # Musk
    SIMPLICITY_FOCUS = "simplicity_focus"   # Jobs
    CUSTOMER_OBSESSION = "customer_obsession"  # Bezos
    DESIGN_THINKING = "design_thinking"    # IDEO
    LATERAL_THINKING = "lateral_thinking"  # de Bono
    SCAMPER = "scamper"                    # Eberle
    BRAINSTORMING = "brainstorming"        # Osborn
    MIND_MAPPING = "mind_mapping"          # Buzan

@dataclass
class CreativeSolution:
    """Generated creative solution"""
    approach: str
    solution: str
    rationale: str
    risks: List[str]
    implementation_steps: List[str]

@dataclass
class InnovationAudit:
    """Assessment of innovation potential"""
    current_approach: str
    innovation_score: int  # 0-100
    constraints_identified: List[str]
    assumptions_challenged: List[str]
    opportunities: List[str]
    recommended_methods: List[str]

class InnovationFramework:
    """
    Innovation and creativity toolkit based on world's best thinkers
    """
    
    # Steve Jobs' innovation principles
    JOBS_PRINCIPLES = {
        'simplicity': 'Simplicity is the ultimate sophistication. Remove until only essence remains.',
        'focus': 'Focus means saying no to 1000 good ideas to say yes to 1 great one.',
        'integration': 'Design is how it works, not just how it looks. Hardware + software + service.',
        'user_experience': 'Start with customer experience, work backwards to technology.',
        'courage': 'Have the courage to follow your heart and intuition.'
    }
    
    # Elon Musk's first principles questions
    MUSK_QUESTIONS = [
        'What are we assuming that might not be true?',
        'What is the physics/math of this problem?',
        'What are the fundamental truths?',
        'What would this look like if built from scratch?',
        'What are the constraints - real vs imagined?',
        'How can we make it 10x better, not 10% better?',
        'What is the optimal solution if cost/time were not issues?'
    ]
    
    # Jeff Bezos' innovation frameworks
    BEZOS_FRAMEWORKS = {
        'customer_obsession': 'Start with customer and work backwards. What do they need?',
        'long_term_thinking': 'Focus on long-term market leadership over short-term profits.',
        'day_1_mentality': 'Always operate like it\'s Day 1 - avoid Day 2 complacency.',
        'disagree_and_commit': 'Have conviction, challenge ideas, but commit fully once decided.',
        'two_way_door': 'Most decisions are reversible (two-way doors). Make them quickly.'
    }
    
    # IDEO Design Thinking phases
    DESIGN_THINKING_PHASES = [
        ('Empathize', 'Understand user needs deeply. Observe, engage, immerse.'),
        ('Define', 'Frame the problem clearly. What is the actual problem?'),
        ('Ideate', 'Generate many ideas. Quantity over quality initially.'),
        ('Prototype', 'Build quick, testable versions. Fail fast, learn fast.'),
        ('Test', 'Get feedback. Iterate based on what you learn.')
    ]
    
    # SCAMPER creativity technique
    SCAMPER_TECHNIQUES = {
        'S': ('Substitute', 'What can be replaced? Materials, people, processes?'),
        'C': ('Combine', 'What can be merged? Features, purposes, systems?'),
        'A': ('Adapt', 'What else is like this? What can be borrowed?'),
        'M': ('Modify', 'Change size, color, shape, attributes?'),
        'P': ('Put to other uses', 'New applications? Different contexts?'),
        'E': ('Eliminate', 'What can be removed? Simplified? Streamlined?'),
        'R': ('Reverse', 'Do the opposite? Change order? Rearrange?')
    }
    
    def apply_first_principles(self, problem: str) -> Dict:
        """
        Musk-style first principles breakdown
        """
        questions = random.sample(self.MUSK_QUESTIONS, 4)
        
        return {
            'problem': problem,
            'method': 'First Principles (Musk)',
            'questions_to_ask': questions,
            'approach': f"Break '{problem}' down to fundamental truths. Challenge all assumptions.",
            'key_insight': 'Most people reason by analogy. Reason from fundamentals instead.',
            'action': 'Strip away history and analogy. Ask: What is physics of this problem?'
        }
    
    def apply_simplicity_focus(self, solution: str) -> Dict:
        """
        Jobs-style simplicity
        """
        return {
            'current': solution,
            'method': 'Simplicity Focus (Jobs)',
            'principle': self.JOBS_PRINCIPLES['simplicity'],
            'questions': [
                'What can be removed without losing function?',
                'What is the essence of this solution?',
                'Would a 5-year-old understand this?',
                'Is this beautiful in its simplicity?'
            ],
            'action': 'Remove, remove, remove until only the essential remains.',
            'insight': 'Simple is harder than complex. But worth it.'
        }
    
    def apply_customer_obsession(self, idea: str) -> Dict:
        """
        Bezos-style customer obsession
        """
        return {
            'idea': idea,
            'method': 'Customer Obsession (Bezos)',
            'principles': [
                self.BEZOS_FRAMEWORKS['customer_obsession'],
                self.BEZOS_FRAMEWORKS['long_term_thinking']
            ],
            'questions': [
                'Who is the customer?',
                'What is their current pain?',
                'What would delight them?',
                'What would they pay for?',
                'What is the minimum to solve their problem?'
            ],
            'action': 'Start with customer and work backwards. Not technology-forward.',
            'insight': 'Customers are always dissatisfied. Even when they don\'t know it yet.'
        }
    
    def apply_design_thinking(self, challenge: str) -> Dict:
        """
        IDEO-style design thinking
        """
        return {
            'challenge': challenge,
            'method': 'Design Thinking (IDEO)',
            'phases': self.DESIGN_THINKING_PHASES,
            'current_phase': 'Start with EMPATHIZE - deeply understand user',
            'key_principles': [
                'Human-centered: Start with people, not technology',
                'Ambiguity tolerance: Be comfortable with uncertainty',
                'Experimentation: Prototype to learn, not to prove',
                'Collaboration: Diverse teams create better solutions'
            ],
            'action': 'Move through phases iteratively. Test early and often.',
            'insight': 'Fail fast to learn fast. Prototypes are questions, not answers.'
        }
    
    def apply_scamper(self, product_or_process: str) -> Dict:
        """
        SCAMPER creativity technique
        """
        ideas = []
        for letter, (technique, description) in self.SCAMPER_TECHNIQUES.items():
            ideas.append(f"{letter} - {technique}: {description}")
        
        return {
            'target': product_or_process,
            'method': 'SCAMPER',
            'techniques': ideas,
            'action': f"Apply each SCAMPER technique to {product_or_process}",
            'example': f"Substitute parts of {product_or_process}. Combine with other things. Adapt from other industries.",
            'insight': 'Forced association creates novel solutions.'
        }
    
    def generate_creative_solutions(self, problem: str, num_solutions: int = 3) -> List[CreativeSolution]:
        """
        Generate multiple creative approaches
        """
        methods = [
            ('First Principles', self.apply_first_principles),
            ('Design Thinking', self.apply_design_thinking),
            ('Customer Obsession', self.apply_customer_obsession),
            ('SCAMPER', self.apply_scamper)
        ]
        
        solutions = []
        for i, (method_name, method_func) in enumerate(methods[:num_solutions]):
            result = method_func(problem)
            
            solutions.append(CreativeSolution(
                approach=method_name,
                solution=f"Apply {method_name}: {result.get('action', 'See details')}",
                rationale=result.get('insight', 'Innovation requires fresh perspective'),
                risks=['Implementation complexity', 'Resistance to change', 'Resource requirements'],
                implementation_steps=['Understand method deeply', 'Apply to specific problem', 'Test and iterate']
            ))
        
        return solutions
    
    def audit_innovation_potential(self, current_approach: str) -> InnovationAudit:
        """
        Audit how innovative current approach is
        """
        # Simplified scoring
        score = 50  # Base score
        
        # Reduce score for common anti-patterns
        if 'always done this way' in current_approach.lower():
            score -= 20
        if 'industry standard' in current_approach.lower():
            score -= 15
        if 'best practice' in current_approach.lower():
            score -= 10
        
        # Increase score for innovative indicators
        if 'new' in current_approach.lower() or 'different' in current_approach.lower():
            score += 10
        if 'experiment' in current_approach.lower():
            score += 15
        if 'question' in current_approach.lower():
            score += 10
        
        constraints = [
            'Historical precedent',
            'Resource limitations',
            'Risk aversion',
            'Time pressure'
        ]
        
        assumptions = [
            'This is the only way to do it',
            'Customers want what they have',
            'Change is too risky',
            'We don\'t have resources'
        ]
        
        opportunities = [
            'Challenge fundamental assumptions',
            'Look at adjacent industries',
            'Apply new technology',
            'Simplify dramatically'
        ]
        
        recommended = []
        if score < 40:
            recommended = ['First Principles', 'SCAMPER', 'Design Thinking']
        elif score < 60:
            recommended = ['Customer Obsession', 'Simplicity Focus']
        else:
            recommended = ['Maintain innovation', 'Scale successful experiments']
        
        return InnovationAudit(
            current_approach=current_approach,
            innovation_score=max(0, min(100, score)),
            constraints_identified=constraints,
            assumptions_challenged=assumptions,
            opportunities=opportunities,
            recommended_methods=recommended
        )


# Convenience functions
def innovate(problem: str) -> str:
    """Quick innovation suggestions"""
    framework = InnovationFramework()
    solutions = framework.generate_creative_solutions(problem, 3)
    
    output = f"🚀 INNOVATION APPROACHES FOR: {problem}\n{'='*60}\n"
    for i, sol in enumerate(solutions, 1):
        output += f"\n{i}. {sol.approach}\n"
        output += f"   Solution: {sol.solution}\n"
        output += f"   Why: {sol.rationale}\n"
    
    return output

def simplify(solution: str) -> str:
    """Quick simplicity check"""
    framework = InnovationFramework()
    result = framework.apply_simplicity_focus(solution)
    
    return f"✨ SIMPLICITY CHECK (Jobs Style)\n{'='*60}\n{result['principle']}\n\nAsk:\n" + "\n".join(f"  • {q}" for q in result['questions'])

def customer_focus(idea: str) -> str:
    """Quick customer obsession check"""
    framework = InnovationFramework()
    result = framework.apply_customer_obsession(idea)
    
    return f"👤 CUSTOMER OBSESSION (Bezos Style)\n{'='*60}\n" + "\n".join(f"  • {q}" for q in result['questions'])


# Demo
if __name__ == "__main__":
    print("="*70)
    print("🚀 INNOVATION FRAMEWORK DEMO")
    print("="*70)
    print()
    
    # Test innovation generation
    print(innovate("How to make trading scanner better"))
    print()
    
    # Test simplicity
    print(simplify("Complex trading system with 50 indicators and 20 screens"))
    print()
    
    # Test customer focus
    print(customer_focus("New feature for traders"))
    print()
    
    print("="*70)
    print("✅ Innovation framework operational")
    print("="*70)
