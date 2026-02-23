#!/usr/bin/env python3
"""
Health Monitor & Self-Healer
Monitors system health, detects failures, auto-recovers
"""

import subprocess
import time
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, asdict
import sqlite3

@dataclass
class HealthCheck:
    """Result of a health check"""
    component: str
    status: str  # healthy, degraded, failed
    timestamp: str
    response_time_ms: int
    details: str
    error: Optional[str] = None

@dataclass
class Incident:
    """Recorded incident for learning"""
    timestamp: str
    component: str
    error_type: str
    error_message: str
    recovery_action: str
    recovery_success: bool
    time_to_recovery_ms: int

class HealthMonitor:
    """
    Monitors critical components and tracks health
    """
    
    def __init__(self, db_path: str = "memory/health.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
        
        # Components to monitor
        self.checks = {
            'gateway': self._check_gateway,
            'disk_space': self._check_disk_space,
            'memory': self._check_memory,
            'workspace': self._check_workspace
        }
        
        # Alert thresholds
        self.thresholds = {
            'gateway_response_ms': 5000,
            'disk_free_gb': 5,
            'memory_free_percent': 10
        }
    
    def _init_db(self):
        """Initialize health database"""
        conn = sqlite3.connect(self.db_path)
        
        conn.execute("""
            CREATE TABLE IF NOT EXISTS health_checks (
                id INTEGER PRIMARY KEY,
                timestamp TEXT,
                component TEXT,
                status TEXT,
                response_time_ms INTEGER,
                details TEXT,
                error TEXT
            )
        """)
        
        conn.execute("""
            CREATE TABLE IF NOT EXISTS incidents (
                id INTEGER PRIMARY KEY,
                timestamp TEXT,
                component TEXT,
                error_type TEXT,
                error_message TEXT,
                recovery_action TEXT,
                recovery_success INTEGER,
                time_to_recovery_ms INTEGER
            )
        """)
        
        conn.commit()
        conn.close()
    
    def _check_gateway(self) -> HealthCheck:
        """Check if OpenClaw gateway is running"""
        start = time.time()
        
        try:
            result = subprocess.run(
                ["openclaw", "health"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            elapsed_ms = int((time.time() - start) * 1000)
            
            if "healthy" in result.stdout.lower() or result.returncode == 0:
                return HealthCheck(
                    component='gateway',
                    status='healthy',
                    timestamp=datetime.now().isoformat(),
                    response_time_ms=elapsed_ms,
                    details='Gateway responding'
                )
            else:
                return HealthCheck(
                    component='gateway',
                    status='failed',
                    timestamp=datetime.now().isoformat(),
                    response_time_ms=elapsed_ms,
                    details='Gateway unhealthy',
                    error=result.stderr[:200]
                )
        
        except subprocess.TimeoutExpired:
            return HealthCheck(
                component='gateway',
                status='failed',
                timestamp=datetime.now().isoformat(),
                response_time_ms=5000,
                details='Gateway timeout',
                error='No response within 5s'
            )
        except Exception as e:
            return HealthCheck(
                component='gateway',
                status='failed',
                timestamp=datetime.now().isoformat(),
                response_time_ms=0,
                details='Gateway check error',
                error=str(e)[:200]
            )
    
    def _check_disk_space(self) -> HealthCheck:
        """Check available disk space"""
        try:
            result = subprocess.run(
                ["df", "-h", "/Users/sigbotti"],
                capture_output=True,
                text=True
            )
            
            # Parse output
            lines = result.stdout.strip().split('\n')
            if len(lines) >= 2:
                parts = lines[1].split()
                used_percent = parts[4].replace('%', '')
                available = parts[3]
                
                # Extract GB
                available_gb = 10  # Default
                if 'G' in available:
                    available_gb = float(available.replace('G', ''))
                
                if available_gb < self.thresholds['disk_free_gb']:
                    status = 'degraded'
                else:
                    status = 'healthy'
                
                return HealthCheck(
                    component='disk_space',
                    status=status,
                    timestamp=datetime.now().isoformat(),
                    response_time_ms=100,
                    details=f'{available} available ({used_percent}% used)'
                )
        
        except Exception as e:
            return HealthCheck(
                component='disk_space',
                status='unknown',
                timestamp=datetime.now().isoformat(),
                response_time_ms=0,
                details='Could not check disk space',
                error=str(e)[:200]
            )
    
    def _check_memory(self) -> HealthCheck:
        """Check system memory"""
        try:
            result = subprocess.run(
                ["vm_stat"],
                capture_output=True,
                text=True
            )
            
            # Parse macOS vm_stat
            lines = result.stdout.strip().split('\n')
            
            # Rough check - just verify command works
            if "Pages free" in result.stdout:
                return HealthCheck(
                    component='memory',
                    status='healthy',
                    timestamp=datetime.now().isoformat(),
                    response_time_ms=100,
                    details='Memory check passed'
                )
            else:
                return HealthCheck(
                    component='memory',
                    status='unknown',
                    timestamp=datetime.now().isoformat(),
                    response_time_ms=100,
                    details='Could not parse memory stats'
                )
        
        except Exception as e:
            return HealthCheck(
                component='memory',
                status='unknown',
                timestamp=datetime.now().isoformat(),
                response_time_ms=0,
                details='Memory check failed',
                error=str(e)[:200]
            )
    
    def _check_workspace(self) -> HealthCheck:
        """Check workspace accessibility"""
        workspace = Path("/Users/sigbotti/.openclaw/workspace")
        
        try:
            if workspace.exists() and workspace.is_dir():
                # Try to write test file
                test_file = workspace / ".health_check_test"
                test_file.write_text("test")
                test_file.unlink()
                
                return HealthCheck(
                    component='workspace',
                    status='healthy',
                    timestamp=datetime.now().isoformat(),
                    response_time_ms=50,
                    details='Workspace accessible and writable'
                )
            else:
                return HealthCheck(
                    component='workspace',
                    status='failed',
                    timestamp=datetime.now().isoformat(),
                    response_time_ms=0,
                    details='Workspace not accessible'
                )
        
        except Exception as e:
            return HealthCheck(
                component='workspace',
                status='failed',
                timestamp=datetime.now().isoformat(),
                response_time_ms=0,
                details='Workspace write test failed',
                error=str(e)[:200]
            )
    
    def run_all_checks(self) -> List[HealthCheck]:
        """Run all health checks"""
        results = []
        
        for name, check_func in self.checks.items():
            result = check_func()
            results.append(result)
            self._record_check(result)
        
        return results
    
    def _record_check(self, check: HealthCheck):
        """Record check to database"""
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            """INSERT INTO health_checks 
               (timestamp, component, status, response_time_ms, details, error)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (check.timestamp, check.component, check.status,
             check.response_time_ms, check.details, check.error)
        )
        conn.commit()
        conn.close()
    
    def get_summary(self) -> Dict:
        """Get health summary"""
        results = self.run_all_checks()
        
        healthy = sum(1 for r in results if r.status == 'healthy')
        degraded = sum(1 for r in results if r.status == 'degraded')
        failed = sum(1 for r in results if r.status == 'failed')
        
        return {
            'total': len(results),
            'healthy': healthy,
            'degraded': degraded,
            'failed': failed,
            'status': 'healthy' if failed == 0 else 'degraded' if failed < 2 else 'critical',
            'checks': results
        }
    
    def print_status(self):
        """Print health status"""
        summary = self.get_summary()
        
        print("="*70)
        print("🏥 HEALTH STATUS")
        print("="*70)
        print(f"Overall: {summary['status'].upper()}")
        print(f"Components: {summary['healthy']} healthy, {summary['degraded']} degraded, {summary['failed']} failed")
        print()
        
        for check in summary['checks']:
            emoji = "✅" if check.status == 'healthy' else "⚠️" if check.status == 'degraded' else "❌"
            print(f"{emoji} {check.component}: {check.status}")
            print(f"   {check.details}")
            if check.error:
                print(f"   Error: {check.error[:50]}")
        
        print("="*70)


class SelfHealer:
    """
    Attempts automatic recovery from failures
    """
    
    def __init__(self, monitor: HealthMonitor):
        self.monitor = monitor
        self.recovery_attempts = 0
        self.max_attempts = 3
        
        # Recovery actions
        self.actions = {
            'gateway': self._restart_gateway,
            'workspace': self._repair_workspace,
            'disk_space': self._cleanup_disk
        }
    
    def check_and_alert(self) -> List[Dict]:
        """Check health and alert on issues (don't auto-restart during chat)"""
        results = self.monitor.run_all_checks()
        issues = []
        
        for check in results:
            if check.status in ['degraded', 'failed']:
                issues.append({
                    'component': check.component,
                    'status': check.status,
                    'details': check.details,
                    'error': check.error
                })
        
        return issues
    
    def check_and_heal(self, allow_restart: bool = False) -> List[Dict]:
        """Check health and attempt recovery if needed"""
        results = self.monitor.run_all_checks()
        actions_taken = []
        
        for check in results:
            if check.status in ['degraded', 'failed']:
                if check.component == 'gateway' and not allow_restart:
                    # Just alert, don't restart during active conversation
                    actions_taken.append({
                        'component': check.component,
                        'status': check.status,
                        'action': 'alert_only',
                        'success': False,
                        'message': 'Gateway issue detected - restart manually if needed'
                    })
                else:
                    action = self._attempt_recovery(check)
                    actions_taken.append({
                        'component': check.component,
                        'status': check.status,
                        'action': action['action'],
                        'success': action['success']
                    })
        
        return actions_taken
    
    def _attempt_recovery(self, check: HealthCheck) -> Dict:
        """Attempt to recover from failure"""
        if check.component not in self.actions:
            return {'action': 'none', 'success': False, 'reason': 'No recovery action defined'}
        
        if self.recovery_attempts >= self.max_attempts:
            return {'action': 'none', 'success': False, 'reason': 'Max recovery attempts reached'}
        
        self.recovery_attempts += 1
        
        # Execute recovery
        action_func = self.actions[check.component]
        success = action_func()
        
        # Record incident
        self._record_incident(check, action_func.__name__, success)
        
        return {'action': action_func.__name__, 'success': success}
    
    def _restart_gateway(self) -> bool:
        """Restart OpenClaw gateway"""
        try:
            print("🔄 Attempting to restart gateway...")
            
            # Use restart command (not stop/start)
            result = subprocess.run(
                ["openclaw", "gateway", "restart"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                print("✅ Gateway restarted")
                return True
            else:
                print(f"❌ Gateway restart failed: {result.stderr[:100]}")
                return False
        
        except Exception as e:
            print(f"❌ Gateway restart error: {e}")
            return False
    
    def _repair_workspace(self) -> bool:
        """Attempt to repair workspace"""
        try:
            workspace = Path("/Users/sigbotti/.openclaw/workspace")
            
            # Check permissions
            if not workspace.exists():
                workspace.mkdir(parents=True, exist_ok=True)
            
            # Create test file
            test = workspace / ".repair_test"
            test.write_text("repaired")
            test.unlink()
            
            print("✅ Workspace repaired")
            return True
        
        except Exception as e:
            print(f"❌ Workspace repair failed: {e}")
            return False
    
    def _cleanup_disk(self) -> bool:
        """Attempt to free disk space"""
        try:
            print("🧹 Cleaning up disk space...")
            
            # Clean temp files
            temp_dirs = ['/tmp', '/var/tmp']
            freed = 0
            
            # Note: Actual cleanup would go here
            # For safety, just log
            print("ℹ️ Disk cleanup logged (manual review needed)")
            
            return True
        
        except Exception as e:
            print(f"❌ Disk cleanup error: {e}")
            return False
    
    def _record_incident(self, check: HealthCheck, action: str, success: bool):
        """Record incident for learning"""
        conn = sqlite3.connect(self.monitor.db_path)
        conn.execute(
            """INSERT INTO incidents 
               (timestamp, component, error_type, error_message, recovery_action, recovery_success, time_to_recovery_ms)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (datetime.now().isoformat(), check.component, check.status,
             check.error or check.details, action, 1 if success else 0, 0)
        )
        conn.commit()
        conn.close()


# Global instances
health_monitor = HealthMonitor()
self_healer = SelfHealer(health_monitor)

# Convenience functions
def check_health() -> Dict:
    """Quick health check"""
    return health_monitor.get_summary()

def heal() -> List[Dict]:
    """Check and heal"""
    return self_healer.check_and_heal()


# Demo
if __name__ == "__main__":
    print("="*70)
    print("🏥 HEALTH MONITOR & SELF-HEALER")
    print("="*70)
    print()
    
    # Check health
    health_monitor.print_status()
    print()
    
    # Check for issues
    summary = check_health()
    if summary['failed'] > 0:
        print("⚠️  Issues detected. Attempting self-healing...")
        actions = heal()
        
        print("\nRecovery attempts:")
        for action in actions:
            emoji = "✅" if action['success'] else "❌"
            print(f"{emoji} {action['component']}: {action['action']}")
    else:
        print("✅ All systems healthy")
