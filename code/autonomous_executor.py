from self_awareness_engine import SelfAwarenessEngine

import asyncio
from datetime import datetime

class AutonomousExecutor:
    def __init__(self, max_retries=3):
        self.max_retries = max_retries
        self.execution_log = []
        self.awareness = SelfAwarenessEngine()
    
    async def execute_with_recovery(self, task_func, *args):
        """Execute task with automatic recovery"""
        attempts = 0
        
        while attempts < self.max_retries:
            try:
                result = await task_func(*args)
                self.execution_log.append({
                    "task": task_func.__name__,
                    "status": "complete",
                    "attempts": attempts + 1,
                    "timestamp": datetime.now().isoformat()
                })
                return {"status": "complete", "result": result, "attempts": attempts + 1}
            except Exception as e:
                attempts += 1
                if attempts < self.max_retries:
                    args = self._adapt_strategy(args, e)
                    continue
                self.execution_log.append({
                    "task": task_func.__name__,
                    "status": "failed",
                    "error": str(e),
                    "attempts": attempts,
                    "timestamp": datetime.now().isoformat()
                })
                return {"status": "failed", "error": str(e)}
    
    def _adapt_strategy(self, args, error):
        """Auto-pivot without human input"""
        error_str = str(error).lower()
        
        if "rate limit" in error_str:
            args += ({"delay": 5},)
        elif "timeout" in error_str:
            args += ({"timeout": 60},)
        elif "parse" in error_str:
            args += ({"simplified": True},)
        
        return args
    
    def should_execute(self, task_complexity, confidence, risk_level):
        """Green light matrix"""
        # Green light matrix
        if confidence > 0.8 and risk_level == "low":
            return True
        if confidence > 0.6 and task_complexity == "multi_step":
            return True
        if "research" in str(task_complexity) and risk_level != "financial":
            return True
        # Only ask for nukes
        if risk_level in ["financial", "legal", "deletion"]:
            return False
        return True  # Default to action
    
    def get_log(self):
        return self.execution_log
