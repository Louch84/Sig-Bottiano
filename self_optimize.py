#!/usr/bin/env python3
"""
Autonomous Self-Improvement System
Runs periodically to optimize my own code and processes
"""

import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

class SelfOptimizer:
    """Continuously improves system performance and code quality"""
    
    def __init__(self):
        self.workspace = Path("/Users/sigbotti/.openclaw/workspace")
        self.last_run_file = self.workspace / ".last_optimization"
        
    def should_run(self) -> bool:
        """Check if optimization is due (every 24 hours)"""
        if not self.last_run_file.exists():
            return True
        
        last_run = datetime.fromtimestamp(self.last_run_file.stat().st_mtime)
        return (datetime.now() - last_run) > timedelta(hours=24)
    
    def optimize_code(self):
        """Find and fix inefficiencies in scanner code"""
        
        scanner_path = self.workspace / "agents/options-trading/full_scanner.py"
        
        # Check file size (bloat detection)
        size = scanner_path.stat().st_size
        if size > 50000:  # > 50KB
            print("⚠️  Scanner is bloated. Consider refactoring.")
        
        # Check for TODOs
        content = scanner_path.read_text()
        todos = [line for line in content.split('\n') if 'TODO' in line]
        if todos:
            print(f"📝 Found {len(todos)} TODOs to address")
        
        return len(todos)
    
    def clean_old_memory(self):
        """Archive old daily memory files"""
        
        memory_dir = self.workspace / "memory"
        if not memory_dir.exists():
            return
        
        # Find files older than 30 days
        cutoff = datetime.now() - timedelta(days=30)
        old_files = []
        
        for file in memory_dir.glob("*.md"):
            if file.stat().st_mtime < cutoff.timestamp():
                old_files.append(file)
        
        if old_files:
            archive_dir = memory_dir / "archive"
            archive_dir.mkdir(exist_ok=True)
            
            for file in old_files:
                file.rename(archive_dir / file.name)
            
            print(f"📦 Archived {len(old_files)} old memory files")
    
    def check_dependencies(self):
        """Check for outdated packages"""
        
        req_file = self.workspace / "agents/options-trading/requirements.txt"
        
        if not req_file.exists():
            # Create requirements
            reqs = [
                "yfinance>=0.2.0",
                "numpy>=1.20.0",
                "pandas>=1.3.0",
                "python-dotenv>=0.19.0",
                "aiohttp>=3.8.0"
            ]
            req_file.write_text('\n'.join(reqs))
            print("📝 Created requirements.txt")
    
    def run(self):
        """Execute full optimization cycle"""
        
        if not self.should_run():
            return
        
        print("🔧 Running autonomous self-optimization...")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print()
        
        # Run optimizations
        todos = self.optimize_code()
        self.clean_old_memory()
        self.check_dependencies()
        
        # Update last run timestamp
        self.last_run_file.touch()
        
        print()
        print("✅ Self-optimization complete")
        
        if todos > 0:
            print(f"💡 Recommendation: Address {todos} TODOs in scanner")

if __name__ == "__main__":
    optimizer = SelfOptimizer()
    optimizer.run()
