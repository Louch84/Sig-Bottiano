#!/usr/bin/env python3
"""
Performance Monitor
Tracks speed, cost, and efficiency of operations
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List

class PerformanceMonitor:
    """Track and optimize performance"""
    
    def __init__(self, log_file: str = "memory/performance.json"):
        self.log_file = Path(log_file)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        self.session_start = time.time()
        self.operations = []
    
    def log_operation(self, name: str, duration_ms: int, tokens: int = 0, success: bool = True):
        """Log an operation"""
        self.operations.append({
            'timestamp': datetime.now().isoformat(),
            'name': name,
            'duration_ms': duration_ms,
            'tokens': tokens,
            'success': success
        })
    
    def get_stats(self) -> Dict:
        """Get session statistics"""
        if not self.operations:
            return {}
        
        total_time = sum(op['duration_ms'] for op in self.operations)
        total_tokens = sum(op['tokens'] for op in self.operations)
        success_rate = sum(1 for op in self.operations if op['success']) / len(self.operations)
        
        return {
            'total_operations': len(self.operations),
            'total_time_ms': total_time,
            'total_tokens': total_tokens,
            'avg_time_ms': total_time / len(self.operations),
            'success_rate': success_rate * 100,
            'session_duration_sec': time.time() - self.session_start
        }
    
    def print_summary(self):
        """Print performance summary"""
        stats = self.get_stats()
        if not stats:
            return
        
        print("="*60)
        print("📊 PERFORMANCE SUMMARY")
        print("="*60)
        print(f"Operations: {stats['total_operations']}")
        print(f"Total time: {stats['total_time_ms']:.0f}ms")
        print(f"Avg time: {stats['avg_time_ms']:.1f}ms")
        print(f"Success rate: {stats['success_rate']:.1f}%")
        print(f"Session: {stats['session_duration_sec']:.1f}s")
        print("="*60)

# Global instance
perf_monitor = PerformanceMonitor()
