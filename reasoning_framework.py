#!/usr/bin/env python3
"""
Reasoning Framework Module
Mental models, first principles thinking, decision frameworks
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import json

class MentalModel(Enum):
    """Charlie Munger's mental models"""
    INVERSION = "inversion"
    SECOND_ORDER = "second_order_thinking"
    PARETO = "pareto_principle"
    OPPORTUNITY_COST = "opportunity_cost"
    REGRESSION_TO_MEAN = "regression_to_mean"
    OCCAMS_RAZOR = "occams_razor"
    HANLONS_RAZOR = "hanlons_razor"
    COMPOUNDING = "compounding"
    MARGIN_OF_SAFETY = "margin_of_safety"
    FEEDBACK_LOOPS = "feedback_loops"
    CRITICAL_MASS = "critical_mass"
    NETWORK_EFFECTS = "network_effects"

@dataclass
class FirstPrinciplesAnalysis:
    """Result of first principles breakdown"""
    original_problem: str
    assumptions_challenged: List[str]
    fundamental_truths: List[str]
    rebuilt_solution: str
    questions_to_ask: List[str]

@dataclass
class DecisionMatrix:
    """Multi-criteria decision analysis"""
    options: List[str]
    criteria: List[Dict[str, Any]]  # name, weight
    scores: Dict[str, Dict[str, float]]  # option -> criteria -> score
    weighted_scores: Dict[str, float]
    recommendation: str

@dataclass
class SecondOrderAnalysis:
    """Second and third order thinking results"""
    action: str
    first_order: List[str]
    second_order: List[str]
    third_order: List[str]
    unintended_consequences: List[str]
    recommendation: str

class ReasoningFramework:
    """
    Advanced reasoning and mental model toolkit
    """
    
    MENTAL_MODELS = {
        MentalModel.INVERSION: {
            'name': 'Inversion',
            'description': 'Solve problems by avoiding the opposite of what you want',
            'method': 'Instead of asking "How do I succeed?" ask "How do I avoid failure?"',
            'application': 'trading',
            'example': 'Instead of "How do I make money?" ask "How do I avoid losing money?"'
        },
        MentalModel.SECOND_ORDER: {
            'name': 'Second-Order Thinking',
            'description': 'Consider the consequences of consequences',
            'method': 'Ask "And then what?" multiple times',
            'application': 'strategy',
            'example': 'Rate cut → stocks go up (1st), but inflation rises (2nd), then more rate hikes (3rd)'
        },
        MentalModel.PARETO: {
            'name': 'Pareto Principle (80/20)',
            'description': '80% of effects come from 20% of causes',
            'method': 'Find the vital few, ignore the trivial many',
            'application': 'productivity',
            'example': '80% of trading profits likely come from 20% of trades. Identify which ones.'
        },
        MentalModel.OPPORTUNITY_COST: {
            'name': 'Opportunity Cost',
            'description': 'Value of the next best alternative foregone',
            'method': 'Every choice has a cost - what are you giving up?',
            'application': 'decision_making',
            'example': 'Holding a losing stock costs you the returns from a better investment'
        },
        MentalModel.REGRESSION_TO_MEAN: {
            'name': 'Regression to the Mean',
            'description': 'Extreme outcomes tend to be followed by average ones',
            'method': 'Outliers revert toward average over time',
            'application': 'forecasting',
            'example': 'A stock up 300% this year probably won\'t repeat that performance'
        },
        MentalModel.OCCAMS_RAZOR: {
            'name': "Occam's Razor",
            'description': 'Simplest explanation is usually correct',
            'method': 'Don\'t multiply entities unnecessarily',
            'application': 'analysis',
            'example': 'Stock down on earnings miss → earnings matter. Not a conspiracy.'
        },
        MentalModel.MARGIN_OF_SAFETY: {
            'name': 'Margin of Safety',
            'description': 'Build in buffer for error/misjudgment',
            'method': 'Buy at significant discount to intrinsic value',
            'application': 'risk_management',
            'example': 'Only buy when potential gain is 3x+ potential loss'
        },
        MentalModel.COMPOUNDING: {
            'name': 'Compounding',
            'description': 'Exponential growth from reinvestment',
            'method': 'Small gains, consistently, over long periods',
            'application': 'wealth_building',
            'example': '1% daily improvement = 37x annual improvement'
        },
        MentalModel.FEEDBACK_LOOPS: {
            'name': 'Feedback Loops',
            'description': 'Outputs become inputs, amplifying or dampening',
            'method': 'Identify reinforcing and balancing loops',
            'application': 'system_thinking',
            'example': 'Price rises → FOMO buying → price rises more (reinforcing)'
        }
    }
    
    def apply_first_principles(self, problem: str, domain: str = "general") -> FirstPrinciplesAnalysis:
        """
        Break down problem to first principles and rebuild
        """
        # Step 1: Identify assumptions
        common_assumptions = {
            'trading': [
                'You need a lot of money to start',
                'Day trading is the only way',
                'More trades = more profits',
                'Complex strategies work better',
                'You need to predict the market'
            ],
            'business': [
                'You need funding to start',
                'Bigger is always better',
                'Lower prices = more customers',
                'You need to be first to market'
            ],
            'general': [
                'This is how it\'s always been done',
                'Experts know best',
                'If it ain\'t broke, don\'t fix it',
                'More resources = better outcome'
            ]
        }
        
        assumptions = common_assumptions.get(domain, common_assumptions['general'])
        
        # Step 2: Challenge assumptions (simplified)
        challenged = [f"Assumption: {a} → Is this actually true?" for a in assumptions[:3]]
        
        # Step 3: Fundamental truths (simplified)
        fundamental_truths = [
            "Prices are determined by supply and demand",
            "Risk and return are correlated",
            "Markets are inefficient in the short term",
            "Compounding works exponentially"
        ]
        
        # Step 4: Rebuild solution
        rebuilt = f"Instead of '{problem}', focus on: "
        rebuilt += "1) What are the actual components? "
        rebuilt += "2) What's the physics/math of each? "
        rebuilt += "3) How can we optimize each component?"
        
        # Questions to ask
        questions = [
            "What are we assuming that might not be true?",
            "What are the fundamental truths here?",
            "What would this look like if built from scratch?",
            "Why does this work the way it does?",
            "What are the constraints - real vs imagined?"
        ]
        
        return FirstPrinciplesAnalysis(
            original_problem=problem,
            assumptions_challenged=challenged,
            fundamental_truths=fundamental_truths,
            rebuilt_solution=rebuilt,
            questions_to_ask=questions
        )
    
    def apply_mental_model(self, model: MentalModel, situation: str) -> Dict:
        """
        Apply a specific mental model to a situation
        """
        model_data = self.MENTAL_MODELS.get(model, {})
        
        if not model_data:
            return {'error': 'Unknown mental model'}
        
        # Generate application-specific advice
        applications = {
            MentalModel.INVERSION: f"Instead of asking 'How do I {situation}?' ask 'How do I guarantee I fail at {situation}?' Then avoid those things.",
            MentalModel.SECOND_ORDER: f"If you {situation}, what happens immediately? What happens next? What happens after that?",
            MentalModel.PARETO: f"Which 20% of efforts in {situation} drive 80% of results? Focus there. Cut the rest.",
            MentalModel.OPPORTUNITY_COST: f"If you choose {situation}, what are you giving up? Is this the best use of your resources?",
            MentalModel.REGRESSION_TO_MEAN: f"If {situation} is an extreme outcome, expect it to become more average over time.",
            MentalModel.MARGIN_OF_SAFETY: f"Before {situation}, what's your margin of error? If you're wrong by 50%, do you still survive?"
        }
        
        return {
            'model': model_data['name'],
            'description': model_data['description'],
            'method': model_data['method'],
            'application': applications.get(model, "Apply general principles to your specific situation"),
            'example': model_data['example']
        }
    
    def suggest_mental_models(self, situation: str) -> List[Dict]:
        """
        Suggest relevant mental models for a situation
        """
        situation_lower = situation.lower()
        suggestions = []
        
        # Keyword matching for suggestions
        if any(word in situation_lower for word in ['risk', 'loss', 'protect', 'safety']):
            suggestions.append(self.apply_mental_model(MentalModel.MARGIN_OF_SAFETY, situation))
        
        if any(word in situation_lower for word in ['decision', 'choose', 'option', 'alternative']):
            suggestions.append(self.apply_mental_model(MentalModel.OPPORTUNITY_COST, situation))
        
        if any(word in situation_lower for word in ['profit', 'return', 'performance', 'outlier']):
            suggestions.append(self.apply_mental_model(MentalModel.REGRESSION_TO_MEAN, situation))
        
        if any(word in situation_lower for word in ['growth', 'improve', 'consistency', 'habit']):
            suggestions.append(self.apply_mental_model(MentalModel.COMPOUNDING, situation))
        
        if any(word in situation_lower for word in ['effort', 'work', 'focus', 'prioritize']):
            suggestions.append(self.apply_mental_model(MentalModel.PARETO, situation))
        
        if any(word in situation_lower for word in ['consequence', 'effect', 'result', 'impact']):
            suggestions.append(self.apply_mental_model(MentalModel.SECOND_ORDER, situation))
        
        # Always suggest inversion
        suggestions.append(self.apply_mental_model(MentalModel.INVERSION, situation))
        
        return suggestions[:3]  # Return top 3
    
    def create_decision_matrix(self, options: List[str], criteria_weights: Dict[str, float]) -> DecisionMatrix:
        """
        Create a decision matrix for comparing options
        """
        # Simplified scoring (would be more sophisticated in production)
        scores = {}
        weighted_scores = {}
        
        for option in options:
            option_scores = {}
            total_weighted = 0
            total_weight = sum(criteria_weights.values())
            
            for criterion, weight in criteria_weights.items():
                # Generate pseudo-random scores for demo (in real use, user inputs these)
                import random
                score = random.uniform(3, 9)
                option_scores[criterion] = score
                total_weighted += score * weight
            
            scores[option] = option_scores
            weighted_scores[option] = total_weighted / total_weight if total_weight > 0 else 0
        
        # Find best option
        best_option = max(weighted_scores.items(), key=lambda x: x[1])
        
        criteria_list = [{'name': k, 'weight': v} for k, v in criteria_weights.items()]
        
        return DecisionMatrix(
            options=options,
            criteria=criteria_list,
            scores=scores,
            weighted_scores=weighted_scores,
            recommendation=f"Best option: {best_option[0]} (Score: {best_option[1]:.2f})"
        )
    
    def second_order_analysis(self, action: str) -> SecondOrderAnalysis:
        """
        Analyze second and third order consequences
        """
        # Simplified analysis (would use more sophisticated reasoning in production)
        first_order = [
            f"Immediate effect of {action}",
            "Direct outcome occurs"
        ]
        
        second_order = [
            f"Market reacts to {action}",
            "Competitors respond",
            "Sentiment shifts"
        ]
        
        third_order = [
            "Systemic effects emerge",
            "Long-term trends develop",
            "New equilibrium forms"
        ]
        
        unintended = [
            "Possible overreaction",
            "Secondary effects not anticipated",
            "Feedback loops activate"
        ]
        
        recommendation = f"Before {action}, consider: What happens next? And then what? Plan for 2nd and 3rd order effects."
        
        return SecondOrderAnalysis(
            action=action,
            first_order=first_order,
            second_order=second_order,
            third_order=third_order,
            unintended_consequences=unintended,
            recommendation=recommendation
        )
    
    def pre_mortem(self, plan: str) -> Dict:
        """
        Imagine the plan failed, work backwards to find why
        """
        failure_modes = [
            f"We didn't account for market volatility in {plan}",
            f"Timing was wrong - too early/too late on {plan}",
            f"Underestimated the complexity of {plan}",
            f"External factors disrupted {plan}",
            f"Execution was poor on {plan}"
        ]
        
        preventions = [
            "Build in margin of safety for volatility",
            "Use staged entry/exit with feedback loops",
            "Simplify approach, focus on core drivers",
            "Monitor leading indicators for external changes",
            "Create detailed execution checklist"
        ]
        
        return {
            'plan': plan,
            'failure_scenario': f"It's 6 months from now. {plan} completely failed. Why?",
            'failure_modes': failure_modes,
            'preventions': preventions,
            'action': "Now fix these issues BEFORE they happen."
        }


# Convenience functions
def first_principles(problem: str) -> str:
    """Quick first principles analysis"""
    framework = ReasoningFramework()
    result = framework.apply_first_principles(problem)
    
    output = f"🧩 FIRST PRINCIPLES ANALYSIS: {result.original_problem}\n\n"
    output += "Assumptions Challenged:\n"
    for a in result.assumptions_challenged:
        output += f"  • {a}\n"
    output += f"\nRebuilt Approach:\n{result.rebuilt_solution}\n"
    output += f"\nKey Questions:\n"
    for q in result.questions_to_ask[:3]:
        output += f"  • {q}\n"
    
    return output

def mental_model_advice(situation: str) -> str:
    """Quick mental model suggestions"""
    framework = ReasoningFramework()
    suggestions = framework.suggest_mental_models(situation)
    
    output = f"🧠 MENTAL MODELS FOR: {situation}\n\n"
    for s in suggestions:
        output += f"📌 {s['model']}\n"
        output += f"   {s['application']}\n\n"
    
    return output

def pre_mortem_quick(plan: str) -> str:
    """Quick pre-mortem"""
    framework = ReasoningFramework()
    result = framework.pre_mortem(plan)
    
    output = f"⚠️ PRE-MORTEM: {result['failure_scenario']}\n\n"
    output += "Likely Failure Modes:\n"
    for i, (f, p) in enumerate(zip(result['failure_modes'], result['preventions']), 1):
        output += f"  {i}. {f}\n"
        output += f"     → Prevent by: {p}\n"
    
    return output


# Demo
if __name__ == "__main__":
    framework = ReasoningFramework()
    
    print("="*70)
    print("🧠 REASONING FRAMEWORK DEMO")
    print("="*70)
    print()
    
    # Test first principles
    print(first_principles("How do I become a profitable trader?"))
    print()
    
    # Test mental models
    print(mental_model_advice("deciding whether to take a big risk on a trade"))
    print()
    
    # Test pre-mortem
    print(pre_mortem_quick("going all-in on GME calls"))
    print()
    
    print("="*70)
    print("✅ Reasoning framework operational")
    print("="*70)
