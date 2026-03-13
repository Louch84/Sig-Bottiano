#!/usr/bin/env python3
"""
Error Pattern Analyzer
Analyzes errors to find patterns
"""

from datetime import datetime, timedelta
from collections import Counter
import os

ERROR_LOG = "/Users/sigbotti/.openclaw/workspace/logs/errors.log"

def analyze_errors():
    """Find patterns in errors"""
    if not os.path.exists(ERROR_LOG):
        return "No errors logged yet"
    
    with open(ERROR_LOG, 'r') as f:
        errors = f.readlines()
    
    # Extract function names
    functions = [line.split('|')[1].strip() for line in errors if '|' in line]
    
    if not functions:
        return "No patterns found"
    
    # Count by function
    counts = Counter(functions)
    
    report = "ERROR PATTERNS:\n"
    report += "=" * 30 + "\n"
    for func, count in counts.most_common(5):
        report += f"{func}: {count} failures\n"
    
    return report

if __name__ == "__main__":
    print(analyze_errors())
