#!/usr/bin/env python3
"""
Sig Botti Self-Reflection System
Analyzes task completion and extracts lessons for continuous improvement.
"""
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Add skills to path
sys.path.insert(0, '/Users/sigbotti/.openclaw/workspace/skills/advanced-memory/scripts')
from store_memory import store_memory

MEMORY_DIR = Path(os.path.expanduser('~/.openclaw/memory'))
REFLECTION_LOG = MEMORY_DIR / 'reflections.jsonl'

def reflect_on_task(task_description, actions_taken, outcome, user_feedback=None, errors=None):
    """
    Reflect on a completed task and extract lessons.
    
    Args:
        task_description: What was the goal
        actions_taken: List of steps/actions performed
        outcome: success/partial/failure
        user_feedback: Any explicit feedback from user
        errors: Any errors encountered
    """
    reflection = {
        'timestamp': datetime.now().isoformat(),
        'task': task_description,
        'actions': actions_taken,
        'outcome': outcome,
        'feedback': user_feedback,
        'errors': errors or []
    }
    
    # Generate insights
    insights = []
    
    if outcome == 'failure' or errors:
        insights.append(f"Failed task pattern: {task_description[:50]}...")
        if errors:
            insights.append(f"Error type: {errors[0] if isinstance(errors, list) else errors}")
    
    if outcome == 'success':
        insights.append(f"Successful approach for: {task_description[:50]}...")
    
    if user_feedback:
        insights.append(f"User preference noted: {user_feedback}")
    
    reflection['insights'] = insights
    
    # Store in vector memory
    content = f"""Task: {task_description}
Outcome: {outcome}
Actions: {'; '.join(actions_taken) if isinstance(actions_taken, list) else actions_taken}
Insights: {'; '.join(insights)}
"""
    
    store_memory(
        content=content,
        tags='reflection,' + outcome + ',lesson',
        metadata={
            'type': 'reflection',
            'outcome': outcome,
            'timestamp': datetime.now().isoformat()
        }
    )
    
    # Append to reflection log
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    with open(REFLECTION_LOG, 'a') as f:
        f.write(json.dumps(reflection) + '\n')
    
    return reflection

def get_recent_reflections(limit=10):
    """Get recent reflections for analysis."""
    if not REFLECTION_LOG.exists():
        return []
    
    reflections = []
    with open(REFLECTION_LOG) as f:
        for line in f:
            reflections.append(json.loads(line))
    
    return reflections[-limit:]

def analyze_patterns():
    """Analyze reflection patterns for systemic issues."""
    reflections = get_recent_reflections(100)
    
    if not reflections:
        return {}
    
    outcomes = {'success': 0, 'partial': 0, 'failure': 0}
    error_types = {}
    
    for r in reflections:
        outcomes[r['outcome']] = outcomes.get(r['outcome'], 0) + 1
        if r.get('errors'):
            for e in r['errors']:
                error_types[e] = error_types.get(e, 0) + 1
    
    return {
        'success_rate': outcomes['success'] / len(reflections),
        'total_reflections': len(reflections),
        'common_errors': sorted(error_types.items(), key=lambda x: x[1], reverse=True)[:5]
    }

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--task', required=True)
    parser.add_argument('--actions')
    parser.add_argument('--outcome', choices=['success', 'partial', 'failure'], required=True)
    parser.add_argument('--feedback')
    parser.add_argument('--errors')
    parser.add_argument('--analyze', action='store_true')
    args = parser.parse_args()
    
    if args.analyze:
        print(json.dumps(analyze_patterns(), indent=2))
    else:
        actions = args.actions.split(',') if args.actions else []
        errors = args.errors.split(',') if args.errors else []
        result = reflect_on_task(args.task, actions, args.outcome, args.feedback, errors)
        print(json.dumps(result, indent=2))
