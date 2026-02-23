#!/usr/bin/env python3
"""
Token Usage & Cost Tracker
Monitors and optimizes API/token consumption
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path

class CostTracker:
    """Tracks and optimizes token/API usage"""
    
    def __init__(self):
        self.log_file = Path("/Users/sigbotti/.openclaw/workspace/.usage_log")
        self.daily_budget = {
            'tokens': 100000,
            'api_calls': 500,
            'compute_minutes': 60
        }
        self.load_today()
    
    def load_today(self):
        """Load today's usage"""
        if self.log_file.exists():
            data = json.loads(self.log_file.read_text())
            today = datetime.now().strftime('%Y-%m-%d')
            self.today_usage = data.get(today, {
                'tokens': 0,
                'api_calls': 0,
                'compute_seconds': 0,
                'sessions': 0
            })
        else:
            self.today_usage = {
                'tokens': 0,
                'api_calls': 0,
                'compute_seconds': 0,
                'sessions': 0
            }
    
    def log_usage(self, tokens: int = 0, api_calls: int = 0, compute_seconds: int = 0):
        """Log resource usage"""
        self.today_usage['tokens'] += tokens
        self.today_usage['api_calls'] += api_calls
        self.today_usage['compute_seconds'] += compute_seconds
        self.today_usage['sessions'] += 1
        self.save()
    
    def save(self):
        """Save usage log"""
        today = datetime.now().strftime('%Y-%m-%d')
        if self.log_file.exists():
            data = json.loads(self.log_file.read_text())
        else:
            data = {}
        
        data[today] = self.today_usage
        
        # Keep only last 30 days
        cutoff = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        data = {k: v for k, v in data.items() if k >= cutoff}
        
        self.log_file.write_text(json.dumps(data, indent=2))
    
    def get_status(self) -> dict:
        """Get current usage status"""
        token_pct = (self.today_usage['tokens'] / self.daily_budget['tokens']) * 100
        api_pct = (self.today_usage['api_calls'] / self.daily_budget['api_calls']) * 100
        
        return {
            'tokens_used': self.today_usage['tokens'],
            'token_budget': self.daily_budget['tokens'],
            'token_pct': token_pct,
            'api_calls': self.today_usage['api_calls'],
            'api_budget': self.daily_budget['api_calls'],
            'api_pct': api_pct,
            'sessions': self.today_usage['sessions'],
            'status': 'OK' if token_pct < 80 else 'WARNING' if token_pct < 95 else 'CRITICAL'
        }
    
    def should_compress(self) -> bool:
        """Check if we should compress responses"""
        status = self.get_status()
        return status['token_pct'] > 60  # Compress at 60% usage
    
    def estimate_cost(self, action: str) -> int:
        """Estimate token cost of an action"""
        costs = {
            'file_read': 500,
            'file_edit': 300,
            'web_search': 800,
            'code_generation': 1500,
            'full_scanner_run': 2000,
            'explain_concept': 1000,
            'quick_answer': 200
        }
        return costs.get(action, 500)

cost_tracker = CostTracker()

# Log this session
cost_tracker.log_usage(tokens=500, compute_seconds=1)

if __name__ == "__main__":
    status = cost_tracker.get_status()
    print(f"📊 Daily Usage: {status['token_pct']:.0f}% of budget")
    print(f"   Tokens: {status['tokens_used']:,} / {status['token_budget']:,}")
    print(f"   API Calls: {status['api_calls']} / {status['api_budget']}")
    print(f"   Status: {status['status']}")
