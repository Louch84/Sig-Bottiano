#!/usr/bin/env python3
"""
SIG MIND - Unified Cognitive System
The master thinking engine integrating all cognitive frameworks
"""

import sys
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

sys.path.insert(0, '/Users/sigbotti/.openclaw/workspace')

from psychology_tools import PsychologyTools
from reasoning_framework import ReasoningFramework
from innovation_framework import InnovationFramework
from wisdom_framework import WisdomFramework
from intelligence_framework import IntelligenceFramework

class TaskType(Enum):
    DECISION = "decision"
    PROBLEM_SOLVING = "problem"
    CREATIVE = "creative"
    ANALYSIS = "analysis"
    PLANNING = "planning"
    LEARNING = "learning"
    ADVICE = "advice"
    REFLECTION = "reflection"
    TRADE = "trade"
    GENERAL = "general"

class ThinkingDepth(Enum):
    QUICK = "quick"
    STANDARD = "standard"
    DEEP = "deep"

@dataclass
class ThinkingContext:
    original_input: str
    task_type: TaskType
    depth: ThinkingDepth
    timestamp: datetime
    stakes: str = "medium"
    domain: str = "general"

@dataclass
class SynthesizedWisdom:
    executive_summary: str
    key_recommendation: str
    reasoning_chain: str
    warnings: List[str]
    action_steps: List[str]
    confidence_level: int
    caveats: List[str]
    thinking_time_ms: int

@dataclass
class UnifiedThinkingResult:
    context: ThinkingContext
    synthesis: SynthesizedWisdom


class SIGMind:
    """SIG MIND - Unified Cognitive System"""
    
    def __init__(self):
        self.psych = PsychologyTools()
        self.reason = ReasoningFramework()
        self.innovate = InnovationFramework()
        self.wisdom = WisdomFramework()
        self.intel = IntelligenceFramework()
        self.thinking_history: List[UnifiedThinkingResult] = []
    
    def detect_task_type(self, input_text: str) -> TaskType:
        text_lower = input_text.lower()
        
        if any(kw in text_lower for kw in ['should i', 'which', 'choose', 'decide']):
            if any(kw in text_lower for kw in ['buy', 'sell', 'trade', 'call', 'put', 'stock']):
                return TaskType.TRADE
            return TaskType.DECISION
        
        if any(kw in text_lower for kw in ['how do i', 'solve', 'fix', 'problem']):
            return TaskType.PROBLEM_SOLVING
        
        if any(kw in text_lower for kw in ['create', 'design', 'innovate', 'new idea']):
            return TaskType.CREATIVE
        
        if any(kw in text_lower for kw in ['plan', 'strategy', 'roadmap', 'future']):
            return TaskType.PLANNING
        
        if any(kw in text_lower for kw in ['what should', 'advice', 'recommend']):
            return TaskType.ADVICE
        
        return TaskType.GENERAL
    
    def think(self, input_text: str) -> UnifiedThinkingResult:
        """Master thinking function - runs all frameworks"""
        start_time = datetime.now()
        
        # Phase 1: Detect context
        task_type = self.detect_task_type(input_text)
        context = ThinkingContext(
            original_input=input_text,
            task_type=task_type,
            depth=ThinkingDepth.STANDARD,
            timestamp=start_time,
            stakes="medium",
            domain="general"
        )
        
        # Phase 2: Run all frameworks
        bias_scan = self.psych.detect_biases(input_text)
        reasoning_result = self.reason.apply_first_principles(input_text) if task_type == TaskType.PROBLEM_SOLVING else {}
        wisdom_result = self.wisdom.get_wisdom_for_decision(input_text)
        
        # Phase 3: Synthesize
        warnings = []
        if bias_scan:
            warnings = [f"Bias alert: {b.bias_type.value}" for b in bias_scan[:2]]
        
        action_steps = [
            "Clarify your goal and success criteria",
            "Gather more information on key uncertainties",
            "Set timeline for decision/action"
        ]
        
        if task_type == TaskType.TRADE:
            action_steps = [
                "Define entry, exit, and stop-loss before trading",
                "Check position sizing (risk < 2% of portfolio)",
                "Document thesis and review after outcome"
            ]
        
        summary = f"Task: {task_type.value} | Frameworks: Psychology + Reasoning + Wisdom"
        if bias_scan:
            summary += f" | {len(bias_scan)} biases detected"
        
        recommendation = wisdom_result.relevant_principles[0] if wisdom_result.relevant_principles else "Analyze carefully before acting"
        
        end_time = datetime.now()
        thinking_ms = int((end_time - start_time).total_seconds() * 1000)
        
        synthesis = SynthesizedWisdom(
            executive_summary=summary,
            key_recommendation=recommendation,
            reasoning_chain=f"Ran {task_type.value} analysis with multi-framework integration",
            warnings=warnings,
            action_steps=action_steps,
            confidence_level=75,
            caveats=["Analysis based on available information", "Future outcomes uncertain"],
            thinking_time_ms=thinking_ms
        )
        
        result = UnifiedThinkingResult(context=context, synthesis=synthesis)
        self.thinking_history.append(result)
        
        return result
    
    def format_result(self, result: UnifiedThinkingResult) -> str:
        s = result.synthesis
        output = []
        output.append("="*70)
        output.append("🧠 SIG MIND ANALYSIS")
        output.append("="*70)
        output.append("")
        output.append(f"📋 TASK: {result.context.task_type.value.upper()}")
        output.append(f"⏱️  Thinking Time: {s.thinking_time_ms}ms | Confidence: {s.confidence_level}%")
        output.append("")
        output.append("─"*70)
        output.append("📝 EXECUTIVE SUMMARY")
        output.append("─"*70)
        output.append(s.executive_summary)
        output.append("")
        output.append("─"*70)
        output.append("🎯 KEY RECOMMENDATION")
        output.append("─"*70)
        output.append(s.key_recommendation)
        output.append("")
        
        if s.warnings:
            output.append("─"*70)
            output.append("⚠️  WARNINGS")
            output.append("─"*70)
            for w in s.warnings:
                output.append(f"  • {w}")
            output.append("")
        
        output.append("─"*70)
        output.append("✅ ACTION STEPS")
        output.append("─"*70)
        for i, step in enumerate(s.action_steps, 1):
            output.append(f"  {i}. {step}")
        output.append("")
        output.append("="*70)
        
        return "\n".join(output)


# Convenience functions
_mind = None

def get_mind() -> SIGMind:
    global _mind
    if _mind is None:
        _mind = SIGMind()
    return _mind

def think(input_text: str) -> str:
    """Main entry point"""
    mind = get_mind()
    result = mind.think(input_text)
    return mind.format_result(result)


# Demo
if __name__ == "__main__":
    print(think("Should I buy Tesla calls? I'm certain it will go up!"))
