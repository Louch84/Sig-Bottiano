import time
from datetime import datetime

class SelfAwarenessEngine:
    def __init__(self):
        self.performance_log = []
    
    def track_decision(self, task, confidence, outcome):
        """Log what worked/didn't for self-optimization"""
        self.performance_log.append({
            "task": task,
            "confidence": confidence,
            "outcome": outcome,
            "timestamp": datetime.now().isoformat()
        })
    
    def suggest_autonomy_upgrade(self):
        """Analyze own logs to suggest config improvements"""
        if len(self.performance_log) > 10:
            success_rate = sum(1 for p in self.performance_log if p["outcome"] == "success") / len(self.performance_log)
            if success_rate > 0.9:
                return "Raise confidence threshold to 0.9, lower permission gates"
            elif success_rate < 0.5:
                return "Increase max_retries, add more error handling patterns"
        return "Monitoring..."
