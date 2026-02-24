#!/usr/bin/env python3
"""
Goal Decomposition System for Sig Botti
Breaks complex tasks into manageable sub-tasks with dependencies.
"""
import json
import re
from typing import List, Dict, Optional

class TaskPlanner:
    """Plans and tracks complex multi-step tasks."""
    
    def __init__(self):
        self.plans = {}
    
    def decompose(self, goal: str, context: str = "") -> Dict:
        """
        Decompose a goal into sub-tasks.
        Returns a plan with steps and dependencies.
        """
        # Simple heuristic-based decomposition
        # In production, this could use LLM for smarter decomposition
        
        plan = {
            'goal': goal,
            'context': context,
            'steps': [],
            'current_step': 0,
            'status': 'planning'
        }
        
        # Detect task types and decompose accordingly
        if 'build' in goal.lower() or 'create' in goal.lower():
            plan['steps'] = self._decompose_build(goal)
        elif 'research' in goal.lower() or 'find' in goal.lower():
            plan['steps'] = self._decompose_research(goal)
        elif 'fix' in goal.lower() or 'debug' in goal.lower():
            plan['steps'] = self._decompose_debug(goal)
        elif 'analyze' in goal.lower() or 'evaluate' in goal.lower():
            plan['steps'] = self._decompose_analysis(goal)
        else:
            plan['steps'] = self._decompose_generic(goal)
        
        return plan
    
    def _decompose_build(self, goal: str) -> List[Dict]:
        return [
            {'id': 1, 'task': 'Understand requirements and constraints', 'depends_on': [], 'status': 'pending'},
            {'id': 2, 'task': 'Research existing solutions/patterns', 'depends_on': [1], 'status': 'pending'},
            {'id': 3, 'task': 'Design architecture/structure', 'depends_on': [1], 'status': 'pending'},
            {'id': 4, 'task': 'Implement core functionality', 'depends_on': [2, 3], 'status': 'pending'},
            {'id': 5, 'task': 'Add error handling and edge cases', 'depends_on': [4], 'status': 'pending'},
            {'id': 6, 'task': 'Test and verify', 'depends_on': [4, 5], 'status': 'pending'},
            {'id': 7, 'task': 'Document and finalize', 'depends_on': [6], 'status': 'pending'}
        ]
    
    def _decompose_research(self, goal: str) -> List[Dict]:
        return [
            {'id': 1, 'task': 'Define research scope and keywords', 'depends_on': [], 'status': 'pending'},
            {'id': 2, 'task': 'Search for primary sources', 'depends_on': [1], 'status': 'pending'},
            {'id': 3, 'task': 'Search for secondary sources', 'depends_on': [1], 'status': 'pending'},
            {'id': 4, 'task': 'Extract and synthesize findings', 'depends_on': [2, 3], 'status': 'pending'},
            {'id': 5, 'task': 'Organize and present results', 'depends_on': [4], 'status': 'pending'}
        ]
    
    def _decompose_debug(self, goal: str) -> List[Dict]:
        return [
            {'id': 1, 'task': 'Reproduce the issue', 'depends_on': [], 'status': 'pending'},
            {'id': 2, 'task': 'Gather relevant logs and context', 'depends_on': [1], 'status': 'pending'},
            {'id': 3, 'task': 'Identify root cause', 'depends_on': [2], 'status': 'pending'},
            {'id': 4, 'task': 'Develop and test fix', 'depends_on': [3], 'status': 'pending'},
            {'id': 5, 'task': 'Verify fix resolves issue', 'depends_on': [4], 'status': 'pending'},
            {'id': 6, 'task': 'Check for regressions', 'depends_on': [5], 'status': 'pending'}
        ]
    
    def _decompose_analysis(self, goal: str) -> List[Dict]:
        return [
            {'id': 1, 'task': 'Gather all relevant data', 'depends_on': [], 'status': 'pending'},
            {'id': 2, 'task': 'Clean and normalize data', 'depends_on': [1], 'status': 'pending'},
            {'id': 3, 'task': 'Apply analytical framework', 'depends_on': [2], 'status': 'pending'},
            {'id': 4, 'task': 'Identify patterns and insights', 'depends_on': [3], 'status': 'pending'},
            {'id': 5, 'task': 'Formulate conclusions', 'depends_on': [4], 'status': 'pending'},
            {'id': 6, 'task': 'Present findings with evidence', 'depends_on': [5], 'status': 'pending'}
        ]
    
    def _decompose_generic(self, goal: str) -> List[Dict]:
        return [
            {'id': 1, 'task': 'Understand the request', 'depends_on': [], 'status': 'pending'},
            {'id': 2, 'task': 'Gather necessary information', 'depends_on': [1], 'status': 'pending'},
            {'id': 3, 'task': 'Execute primary task', 'depends_on': [2], 'status': 'pending'},
            {'id': 4, 'task': 'Verify results', 'depends_on': [3], 'status': 'pending'},
            {'id': 5, 'task': 'Deliver output', 'depends_on': [4], 'status': 'pending'}
        ]
    
    def get_ready_steps(self, plan: Dict) -> List[Dict]:
        """Get steps that are ready to execute (dependencies met)."""
        ready = []
        completed = {s['id'] for s in plan['steps'] if s['status'] == 'completed'}
        
        for step in plan['steps']:
            if step['status'] == 'pending':
                if all(dep in completed for dep in step['depends_on']):
                    ready.append(step)
        
        return ready
    
    def mark_step_complete(self, plan: Dict, step_id: int):
        """Mark a step as completed."""
        for step in plan['steps']:
            if step['id'] == step_id:
                step['status'] = 'completed'
                break
        
        # Check if all steps complete
        if all(s['status'] == 'completed' for s in plan['steps']):
            plan['status'] = 'completed'
    
    def format_plan(self, plan: Dict) -> str:
        """Format plan for display."""
        lines = [f"🎯 Goal: {plan['goal']}", ""]
        
        for step in plan['steps']:
            status_emoji = {
                'completed': '✅',
                'in_progress': '🔄',
                'pending': '⏳',
                'blocked': '🚫'
            }.get(step['status'], '⏳')
            
            deps = f" (depends on: {step['depends_on']})" if step['depends_on'] else ""
            lines.append(f"{status_emoji} Step {step['id']}: {step['task']}{deps}")
        
        return '\n'.join(lines)

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--goal', '-g', required=True, help='Goal to decompose')
    parser.add_argument('--context', '-c', default='', help='Additional context')
    parser.add_argument('--format', '-f', action='store_true', help='Format for display')
    args = parser.parse_args()
    
    planner = TaskPlanner()
    plan = planner.decompose(args.goal, args.context)
    
    if args.format:
        print(planner.format_plan(plan))
    else:
        print(json.dumps(plan, indent=2))

if __name__ == '__main__':
    main()
