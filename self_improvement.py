"""
Self-Improvement Loop System
Continuously learns from performance and optimizes
All free, local processing
"""

import json
import numpy as np
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
import sqlite3

@dataclass
class PerformanceRecord:
    """Record of a trading decision/outcome"""
    timestamp: str
    symbol: str
    direction: str
    entry_price: float
    exit_price: Optional[float]
    exit_reason: str  # target, stop, manual, open
    pnl: Optional[float]
    pnl_pct: Optional[float]
    agents_used: List[str]
    signal_score: int
    holding_period_days: int
    market_regime: str
    success: Optional[bool] = None

@dataclass
class AgentPerformance:
    """Performance metrics for an agent"""
    agent_name: str
    total_signals: int
    wins: int
    losses: int
    win_rate: float
    avg_win_pct: float
    avg_loss_pct: float
    profit_factor: float
    expectancy: float
    sharpe: float


class SelfImprovementSystem:
    """
    Continuous learning and optimization system
    Tracks performance, identifies patterns, adjusts weights
    """
    
    def __init__(self, db_path: str = "memory/performance.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
        
        # Agent weights (will be adjusted based on performance)
        self.agent_weights = {
            'fundamental': 0.10,
            'technical': 0.35,
            'sentiment': 0.30,
            'research': 0.20,
            'risk': 0.05
        }
    
    def _init_db(self):
        """Initialize performance database"""
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY,
                timestamp TEXT,
                symbol TEXT,
                direction TEXT,
                entry_price REAL,
                exit_price REAL,
                exit_reason TEXT,
                pnl REAL,
                pnl_pct REAL,
                agents_used TEXT,  -- JSON list
                signal_score INTEGER,
                holding_period_days INTEGER,
                market_regime TEXT,
                success INTEGER  -- 0 or 1
            )
        """)
        
        conn.execute("""
            CREATE TABLE IF NOT EXISTS agent_weights (
                date TEXT PRIMARY KEY,
                weights TEXT,  -- JSON
                reason TEXT
            )
        """)
        
        conn.commit()
        conn.close()
    
    def record_trade_entry(self, signal: dict) -> int:
        """Record when a trade is entered"""
        conn = sqlite3.connect(self.db_path)
        
        cursor = conn.execute(
            """INSERT INTO trades 
               (timestamp, symbol, direction, entry_price, agents_used, 
                signal_score, market_regime)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                datetime.now().isoformat(),
                signal.get('symbol', ''),
                signal.get('direction', ''),
                signal.get('entry_price', 0),
                json.dumps(signal.get('agents_used', [])),
                signal.get('move_potential_score', 0),
                signal.get('market_regime', 'NORMAL')
            )
        )
        
        trade_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return trade_id
    
    def record_trade_exit(
        self,
        trade_id: int,
        exit_price: float,
        exit_reason: str,
        holding_days: int
    ):
        """Record when a trade is exited"""
        # Fetch entry price
        conn = sqlite3.connect(self.db_path)
        
        cursor = conn.execute(
            "SELECT entry_price, direction FROM trades WHERE id = ?",
            (trade_id,)
        )
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return
        
        entry_price, direction = row
        
        # Calculate P&L
        if direction == 'CALL':
            pnl = exit_price - entry_price
        else:  # PUT
            pnl = entry_price - exit_price
        
        pnl_pct = (pnl / entry_price) * 100 if entry_price > 0 else 0
        success = 1 if pnl > 0 else 0
        
        # Update record
        conn.execute(
            """UPDATE trades SET
               exit_price = ?, exit_reason = ?, pnl = ?, pnl_pct = ?,
               holding_period_days = ?, success = ?
               WHERE id = ?""",
            (exit_price, exit_reason, pnl, pnl_pct, holding_days, success, trade_id)
        )
        
        conn.commit()
        conn.close()
        
        print(f"📊 Trade recorded: P&L ${pnl:.2f} ({pnl_pct:+.1f}%)")
    
    def analyze_agent_performance(self, days: int = 30) -> Dict[str, AgentPerformance]:
        """Analyze how each agent is performing"""
        
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        
        conn = sqlite3.connect(self.db_path)
        
        # Get all completed trades
        cursor = conn.execute(
            """SELECT agents_used, pnl_pct, success
               FROM trades
               WHERE timestamp > ? AND exit_price IS NOT NULL""",
            (cutoff,)
        )
        
        trades = cursor.fetchall()
        conn.close()
        
        if not trades:
            return {}
        
        # Track performance per agent
        agent_stats = {}
        
        for agents_json, pnl_pct, success in trades:
            agents = json.loads(agents_json)
            
            for agent in agents:
                if agent not in agent_stats:
                    agent_stats[agent] = {
                        'wins': 0, 'losses': 0,
                        'wins_pct': [], 'losses_pct': []
                    }
                
                if success:
                    agent_stats[agent]['wins'] += 1
                    agent_stats[agent]['wins_pct'].append(pnl_pct)
                else:
                    agent_stats[agent]['losses'] += 1
                    agent_stats[agent]['losses_pct'].append(abs(pnl_pct))
        
        # Calculate metrics
        results = {}
        for agent, stats in agent_stats.items():
            total = stats['wins'] + stats['losses']
            if total == 0:
                continue
            
            win_rate = stats['wins'] / total
            avg_win = np.mean(stats['wins_pct']) if stats['wins_pct'] else 0
            avg_loss = np.mean(stats['losses_pct']) if stats['losses_pct'] else 0
            
            # Profit factor
            gross_profit = sum(stats['wins_pct'])
            gross_loss = sum(stats['losses_pct'])
            profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0
            
            # Expectancy
            expectancy = (win_rate * avg_win) - ((1 - win_rate) * avg_loss)
            
            results[agent] = AgentPerformance(
                agent_name=agent,
                total_signals=total,
                wins=stats['wins'],
                losses=stats['losses'],
                win_rate=win_rate,
                avg_win_pct=avg_win,
                avg_loss_pct=avg_loss,
                profit_factor=profit_factor,
                expectancy=expectancy,
                sharpe=0.0  # Would need more data
            )
        
        return results
    
    def optimize_weights(self) -> Dict[str, float]:
        """
        Optimize agent weights based on performance
        Better performing agents get higher weights
        """
        performance = self.analyze_agent_performance(days=30)
        
        if not performance:
            print("⚠️  No performance data yet, using default weights")
            return self.agent_weights
        
        # Calculate new weights based on expectancy
        total_expectancy = sum(p.expectancy for p in performance.values())
        
        if total_expectancy <= 0:
            print("⚠️  Negative overall expectancy, using defensive weights")
            # Reduce all weights, increase risk management
            return {
                'fundamental': 0.10,
                'technical': 0.30,
                'sentiment': 0.25,
                'research': 0.15,
                'risk': 0.20  # Increase risk weight
            }
        
        # New weights proportional to expectancy
        new_weights = {}
        for agent, perf in performance.items():
            if agent in self.agent_weights:
                # Weight = (agent expectancy / total expectancy) * 0.8 + 0.1
                # This gives min 10% weight, max based on performance
                new_weights[agent] = max(0.05, (perf.expectancy / total_expectancy) * 0.7 + 0.1)
        
        # Normalize to sum to 1.0
        total_weight = sum(new_weights.values())
        new_weights = {k: v / total_weight for k, v in new_weights.items()}
        
        # Log change
        self._log_weight_change(new_weights, performance)
        
        self.agent_weights = new_weights
        
        print("🎯 Optimized agent weights based on performance:")
        for agent, weight in sorted(new_weights.items(), key=lambda x: x[1], reverse=True):
            perf = performance.get(agent)
            if perf:
                print(f"   {agent}: {weight:.1%} (Win rate: {perf.win_rate:.0%}, Expectancy: {perf.expectancy:.2f})")
        
        return new_weights
    
    def _log_weight_change(self, new_weights: dict, performance: dict):
        """Log weight changes to database"""
        conn = sqlite3.connect(self.db_path)
        
        reason_parts = []
        for agent, perf in performance.items():
            reason_parts.append(f"{agent}:{perf.win_rate:.0%}")
        
        conn.execute(
            "INSERT OR REPLACE INTO agent_weights (date, weights, reason) VALUES (?, ?, ?)",
            (
                datetime.now().strftime('%Y-%m-%d'),
                json.dumps(new_weights),
                " | ".join(reason_parts)
            )
        )
        
        conn.commit()
        conn.close()
    
    def get_optimal_thresholds(self) -> dict:
        """
        Analyze what signal thresholds work best
        """
        conn = sqlite3.connect(self.db_path)
        
        # Analyze by score ranges
        cursor = conn.execute(
            """SELECT 
               CASE 
                 WHEN signal_score >= 70 THEN 'high'
                 WHEN signal_score >= 50 THEN 'medium'
                 ELSE 'low'
               END as score_range,
               AVG(success) as win_rate,
               AVG(pnl_pct) as avg_pnl,
               COUNT(*) as count
               FROM trades
               WHERE exit_price IS NOT NULL
               GROUP BY score_range"""
        )
        
        results = {}
        for row in cursor.fetchall():
            score_range, win_rate, avg_pnl, count = row
            results[score_range] = {
                'win_rate': win_rate or 0,
                'avg_pnl': avg_pnl or 0,
                'count': count
            }
        
        conn.close()
        
        return results
    
    def generate_insights(self) -> List[str]:
        """Generate actionable insights from performance data"""
        insights = []
        
        # Analyze agent performance
        perf = self.analyze_agent_performance(days=30)
        
        for agent, stats in perf.items():
            if stats.win_rate > 0.6 and stats.profit_factor > 2:
                insights.append(f"✅ {agent} is performing well ({stats.win_rate:.0%} win rate) - rely on it more")
            elif stats.win_rate < 0.4:
                insights.append(f"⚠️  {agent} underperforming ({stats.win_rate:.0%} win rate) - reduce weight or debug")
        
        # Analyze score thresholds
        thresholds = self.get_optimal_thresholds()
        if thresholds.get('high', {}).get('win_rate', 0) > 0.6:
            insights.append("✅ High score signals (70+) perform well - prioritize these")
        
        if thresholds.get('low', {}).get('win_rate', 0) < 0.4:
            insights.append("⚠️  Low score signals (<50) underperform - consider skipping")
        
        return insights
    
    def run_optimization_cycle(self):
        """Run full optimization cycle"""
        print("="*70)
        print("🔄 SELF-IMPROVEMENT CYCLE")
        print("="*70)
        print()
        
        # Check if enough data
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute("SELECT COUNT(*) FROM trades WHERE exit_price IS NOT NULL")
        completed_trades = cursor.fetchone()[0]
        conn.close()
        
        if completed_trades < 10:
            print(f"⚠️  Only {completed_trades} completed trades. Need 10+ for optimization.")
            print("   Continue trading to gather more data.")
            return
        
        print(f"📊 Analyzing {completed_trades} completed trades...\n")
        
        # Generate insights
        insights = self.generate_insights()
        if insights:
            print("💡 Insights:")
            for insight in insights:
                print(f"   {insight}")
            print()
        
        # Optimize weights
        new_weights = self.optimize_weights()
        
        print("\n✅ Optimization complete")
        print("   Weights will be used for next scan")
    
    def get_statistics(self) -> dict:
        """Get trading statistics summary"""
        conn = sqlite3.connect(self.db_path)
        
        # Total trades
        cursor = conn.execute("SELECT COUNT(*) FROM trades")
        total_trades = cursor.fetchone()[0]
        
        # Completed trades
        cursor = conn.execute("SELECT COUNT(*) FROM trades WHERE exit_price IS NOT NULL")
        completed = cursor.fetchone()[0]
        
        # Win rate
        cursor = conn.execute("SELECT AVG(success) FROM trades WHERE exit_price IS NOT NULL")
        win_rate = cursor.fetchone()[0] or 0
        
        # Total P&L
        cursor = conn.execute("SELECT SUM(pnl) FROM trades WHERE exit_price IS NOT NULL")
        total_pnl = cursor.fetchone()[0] or 0
        
        # Avg holding period
        cursor = conn.execute("SELECT AVG(holding_period_days) FROM trades WHERE exit_price IS NOT NULL")
        avg_holding = cursor.fetchone()[0] or 0
        
        conn.close()
        
        return {
            'total_trades': total_trades,
            'completed_trades': completed,
            'win_rate': win_rate * 100 if win_rate else 0,
            'total_pnl': total_pnl,
            'avg_holding_days': avg_holding
        }


class FeedbackLoop:
    """
    Quick feedback mechanism for continuous improvement
    """
    
    def __init__(self, feedback_file: str = "memory/feedback.json"):
        self.feedback_file = Path(feedback_file)
        self.feedback = self._load_feedback()
    
    def _load_feedback(self) -> List[dict]:
        """Load historical feedback"""
        if self.feedback_file.exists():
            return json.loads(self.feedback_file.read_text())
        return []
    
    def add_feedback(self, category: str, issue: str, severity: str = "medium"):
        """Add feedback for improvement"""
        self.feedback.append({
            'timestamp': datetime.now().isoformat(),
            'category': category,
            'issue': issue,
            'severity': severity,
            'status': 'open'
        })
        self._save()
    
    def mark_resolved(self, index: int):
        """Mark feedback as resolved"""
        if 0 <= index < len(self.feedback):
            self.feedback[index]['status'] = 'resolved'
            self.feedback[index]['resolved_at'] = datetime.now().isoformat()
            self._save()
    
    def get_open_issues(self) -> List[dict]:
        """Get unresolved issues"""
        return [f for f in self.feedback if f['status'] == 'open']
    
    def _save(self):
        """Save feedback"""
        self.feedback_file.parent.mkdir(parents=True, exist_ok=True)
        self.feedback_file.write_text(json.dumps(self.feedback, indent=2))


# Global instances
self_improvement = SelfImprovementSystem()
feedback_loop = FeedbackLoop()

# Demo
if __name__ == "__main__":
    print("="*70)
    print("🔄 SELF-IMPROVEMENT SYSTEM DEMO")
    print("="*70)
    print()
    
    # Simulate some trade data
    print("Simulating trade data...")
    
    # Simulate 15 trades
    for i in range(15):
        signal = {
            'symbol': ['AMC', 'GME', 'TSLA', 'AAPL'][i % 4],
            'direction': 'CALL' if i % 3 == 0 else 'PUT',
            'entry_price': 10.0 + i,
            'agents_used': ['technical', 'sentiment'],
            'move_potential_score': 50 + (i * 3),
            'market_regime': 'NORMAL'
        }
        
        trade_id = self_improvement.record_trade_entry(signal)
        
        # Simulate exit (60% win rate)
        exit_price = signal['entry_price'] * (1.05 if i % 5 != 0 else 0.97)
        self_improvement.record_trade_exit(
            trade_id,
            exit_price,
            'target' if i % 5 != 0 else 'stop',
            3
        )
    
    print("\n✅ Simulated 15 trades")
    
    # Run optimization
    print()
    self_improvement.run_optimization_cycle()
