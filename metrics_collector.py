#!/usr/bin/env python3
"""
Metrics Collector & Dashboard
Tracks performance, generates insights, shows trends
"""

import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass
import time

@dataclass
class Metric:
    timestamp: str
    metric_type: str
    value: float
    unit: str
    context: str

class MetricsCollector:
    """
    Collects and analyzes performance metrics
    """
    
    def __init__(self, db_path: str = "memory/metrics.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """Initialize metrics database"""
        conn = sqlite3.connect(self.db_path)
        
        conn.execute("""
            CREATE TABLE IF NOT EXISTS metrics (
                id INTEGER PRIMARY KEY,
                timestamp TEXT,
                metric_type TEXT,
                value REAL,
                unit TEXT,
                context TEXT
            )
        """)
        
        conn.execute("""
            CREATE TABLE IF NOT EXISTS daily_summary (
                date TEXT PRIMARY KEY,
                total_interactions INTEGER,
                avg_response_time_ms REAL,
                success_rate REAL,
                error_rate REAL,
                top_tools TEXT
            )
        """)
        
        conn.commit()
        conn.close()
    
    def record(self, metric_type: str, value: float, unit: str = "", context: str = ""):
        """Record a metric"""
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            """INSERT INTO metrics (timestamp, metric_type, value, unit, context)
               VALUES (?, ?, ?, ?, ?)""",
            (datetime.now().isoformat(), metric_type, value, unit, context)
        )
        conn.commit()
        conn.close()
    
    def record_response_time(self, duration_ms: int, task: str = ""):
        """Record response time"""
        self.record('response_time', duration_ms, 'ms', task)
    
    def record_success(self, task_type: str):
        """Record successful task"""
        self.record('success', 1, 'boolean', task_type)
    
    def record_error(self, error_type: str, details: str = ""):
        """Record error"""
        self.record('error', 1, 'count', f"{error_type}: {details}")
    
    def record_tool_usage(self, tool_name: str):
        """Record tool usage"""
        self.record('tool_usage', 1, 'count', tool_name)
    
    def record_token_usage(self, input_tokens: int, output_tokens: int, model: str = ""):
        """Record token usage"""
        self.record('tokens_input', input_tokens, 'tokens', model)
        self.record('tokens_output', output_tokens, 'tokens', model)
    
    def get_stats(self, metric_type: str, days: int = 7) -> Dict:
        """Get statistics for a metric type"""
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute(
            """SELECT value, timestamp FROM metrics 
               WHERE metric_type = ? AND timestamp > ?
               ORDER BY timestamp""",
            (metric_type, cutoff)
        )
        
        values = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        if not values:
            return {'count': 0, 'avg': 0, 'min': 0, 'max': 0}
        
        return {
            'count': len(values),
            'avg': sum(values) / len(values),
            'min': min(values),
            'max': max(values)
        }
    
    def get_success_rate(self, days: int = 7) -> float:
        """Calculate success rate"""
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        
        conn = sqlite3.connect(self.db_path)
        
        cursor = conn.execute(
            """SELECT COUNT(*) FROM metrics 
               WHERE metric_type = 'success' AND timestamp > ?""",
            (cutoff,)
        )
        successes = cursor.fetchone()[0]
        
        cursor = conn.execute(
            """SELECT COUNT(*) FROM metrics 
               WHERE metric_type = 'error' AND timestamp > ?""",
            (cutoff,)
        )
        errors = cursor.fetchone()[0]
        
        conn.close()
        
        total = successes + errors
        if total == 0:
            return 100.0
        
        return (successes / total) * 100
    
    def get_top_tools(self, n: int = 5, days: int = 7) -> List[tuple]:
        """Get most used tools"""
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute(
            """SELECT context, COUNT(*) as count FROM metrics 
               WHERE metric_type = 'tool_usage' AND timestamp > ?
               GROUP BY context
               ORDER BY count DESC
               LIMIT ?""",
            (cutoff, n)
        )
        
        results = cursor.fetchall()
        conn.close()
        
        return results
    
    def generate_report(self, days: int = 7) -> str:
        """Generate performance report"""
        lines = []
        lines.append("="*70)
        lines.append("📊 PERFORMANCE REPORT")
        lines.append(f"Period: Last {days} days")
        lines.append("="*70)
        lines.append("")
        
        # Response times
        response_stats = self.get_stats('response_time', days)
        lines.append("⏱️  Response Times:")
        lines.append(f"   Average: {response_stats['avg']:.0f}ms")
        lines.append(f"   Range: {response_stats['min']:.0f}ms - {response_stats['max']:.0f}ms")
        lines.append("")
        
        # Success rate
        success_rate = self.get_success_rate(days)
        lines.append(f"✅ Success Rate: {success_rate:.1f}%")
        lines.append("")
        
        # Top tools
        top_tools = self.get_top_tools(5, days)
        if top_tools:
            lines.append("🔧 Most Used Tools:")
            for tool, count in top_tools:
                lines.append(f"   {tool}: {count} uses")
        lines.append("")
        
        lines.append("="*70)
        
        return '\n'.join(lines)
    
    def generate_html_dashboard(self) -> str:
        """Generate HTML dashboard"""
        
        # Get data
        response_stats = self.get_stats('response_time', 7)
        success_rate = self.get_success_rate(7)
        top_tools = self.get_top_tools(5, 7)
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Sig Botti - Performance Dashboard</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #1a1a1a;
            color: #e0e0e0;
        }}
        h1 {{
            color: #00d4aa;
            border-bottom: 2px solid #00d4aa;
            padding-bottom: 10px;
        }}
        .metric-card {{
            background: #2a2a2a;
            border-radius: 8px;
            padding: 20px;
            margin: 10px 0;
        }}
        .metric-value {{
            font-size: 48px;
            font-weight: bold;
            color: #00d4aa;
        }}
        .metric-label {{
            color: #888;
            font-size: 14px;
        }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
        }}
        th, td {{
            padding: 10px;
            text-align: left;
            border-bottom: 1px solid #444;
        }}
        th {{
            color: #00d4aa;
        }}
        .status-good {{ color: #00d4aa; }}
        .status-warn {{ color: #ffd700; }}
        .status-bad {{ color: #ff6b6b; }}
    </style>
</head>
<body>
    <h1>🧠 Sig Botti - Performance Dashboard</h1>
    <p>Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    
    <div class="grid">
        <div class="metric-card">
            <div class="metric-value">{response_stats['avg']:.0f}ms</div>
            <div class="metric-label">Avg Response Time</div>
        </div>
        
        <div class="metric-card">
            <div class="metric-value">{success_rate:.1f}%</div>
            <div class="metric-label">Success Rate</div>
        </div>
        
        <div class="metric-card">
            <div class="metric-value">{response_stats['count']}</div>
            <div class="metric-label">Total Operations</div>
        </div>
    </div>
    
    <div class="metric-card">
        <h2>🔧 Top Tools</h2>
        <table>
            <tr><th>Tool</th><th>Uses</th></tr>
"""
        
        for tool, count in top_tools:
            html += f"            <tr><td>{tool}</td><td>{count}</td></tr>\n"
        
        html += """        </table>
    </div>
    
    <div class="metric-card">
        <h2>📈 Insights</h2>
        <p>Performance is being tracked continuously. This dashboard updates in real-time.</p>
    </div>
</body>
</html>
"""
        
        return html
    
    def save_dashboard(self, path: str = "memory/dashboard.html"):
        """Save dashboard to file"""
        html = self.generate_html_dashboard()
        Path(path).write_text(html)
        print(f"✅ Dashboard saved to: {path}")
        return path


class PerformanceTracker:
    """
    High-level performance tracking with context managers
    """
    
    def __init__(self):
        self.collector = MetricsCollector()
    
    def track_task(self, task_name: str):
        """Context manager for tracking task execution"""
        class TaskTracker:
            def __init__(tracker_self, collector, name):
                tracker_self.collector = collector
                tracker_self.name = name
                tracker_self.start_time = None
            
            def __enter__(tracker_self):
                tracker_self.start_time = time.time()
                return tracker_self
            
            def __exit__(tracker_self, exc_type, exc_val, exc_tb):
                duration_ms = int((time.time() - tracker_self.start_time) * 1000)
                tracker_self.collector.record_response_time(duration_ms, tracker_self.name)
                
                if exc_type is None:
                    tracker_self.collector.record_success(tracker_self.name)
                else:
                    tracker_self.collector.record_error(
                        type(exc_val).__name__,
                        str(exc_val)[:100]
                    )
        
        return TaskTracker(self.collector, task_name)
    
    def print_summary(self, days: int = 7):
        """Print performance summary"""
        print(self.collector.generate_report(days))


# Global instance
metrics_collector = MetricsCollector()
performance_tracker = PerformanceTracker()

# Convenience functions
def track_time(task_name: str):
    """Context manager to track task time"""
    return performance_tracker.track_task(task_name)

def record_metric(metric_type: str, value: float, unit: str = "", context: str = ""):
    """Record any metric"""
    metrics_collector.record(metric_type, value, unit, context)


# Demo
if __name__ == "__main__":
    print("="*70)
    print("📊 METRICS COLLECTOR & DASHBOARD")
    print("="*70)
    print()
    
    # Simulate some metrics
    print("Recording sample metrics...")
    
    metrics_collector.record_response_time(1200, "scan")
    metrics_collector.record_response_time(800, "analysis")
    metrics_collector.record_response_time(1500, "code_gen")
    
    metrics_collector.record_success("trading_scan")
    metrics_collector.record_success("code_edit")
    
    metrics_collector.record_tool_usage("web_search")
    metrics_collector.record_tool_usage("file_write")
    metrics_collector.record_tool_usage("exec")
    
    print("✅ Metrics recorded")
    print()
    
    # Generate report
    print(metrics_collector.generate_report())
    
    # Save dashboard
    dashboard_path = metrics_collector.save_dashboard()
    print(f"\n📱 Open dashboard: file://{Path(dashboard_path).absolute()}")
