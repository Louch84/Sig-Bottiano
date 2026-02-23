#!/usr/bin/env python3
"""
Self-Optimization Master
Integrates all self-improvement systems
Runs continuous optimization
"""

import sys
import time
sys.path.insert(0, '/Users/sigbotti/.openclaw/workspace')

from meta_learning import meta_learner
from self_improvement import self_improvement
from github_manager import github_manager, commit_workspace
from health_monitor import health_monitor, self_healer
from metrics_collector import metrics_collector, performance_tracker

class SelfOptimizationMaster:
    """
    Master controller for all self-optimization systems
    Runs them in coordinated cycles
    """
    
    def __init__(self):
        self.systems = {
            'meta_learning': meta_learner,
            'trading_improvement': self_improvement,
            'health': health_monitor,
            'healer': self_healer,
            'metrics': metrics_collector,
            'github': github_manager
        }
        
        self.optimization_cycles = 0
    
    def run_full_optimization(self):
        """Run complete optimization cycle"""
        self.optimization_cycles += 1
        
        print("="*70)
        print(f"🚀 SELF-OPTIMIZATION CYCLE #{self.optimization_cycles}")
        print("="*70)
        print()
        
        # 1. Health Check
        print("🏥 STEP 1: Health Check")
        health = health_monitor.get_summary()
        print(f"   Status: {health['status']}")
        
        if health['failed'] > 0:
            print("   ⚠️ Issues detected, attempting self-healing...")
            actions = self_healer.check_and_heal()
            for action in actions:
                emoji = "✅" if action['success'] else "❌"
                print(f"   {emoji} {action['component']}: {action['action']}")
        else:
            print("   ✅ All systems healthy")
        print()
        
        # 2. Meta-Learning
        print("🧠 STEP 2: Meta-Learning Analysis")
        insights = meta_learner.generate_insights()
        if insights:
            print("   Insights:")
            for insight in insights[:3]:
                print(f"   - {insight}")
        else:
            print("   ℹ️ No new insights (need more data)")
        print()
        
        # 3. Trading Performance
        print("📈 STEP 3: Trading Performance")
        trading_stats = self_improvement.get_statistics()
        if trading_stats['total_trades'] > 0:
            print(f"   Total trades: {trading_stats['total_trades']}")
            print(f"   Win rate: {trading_stats['win_rate']:.1f}%")
            print(f"   PnL: ${trading_stats['total_pnl']:.2f}")
        else:
            print("   ℹ️ No trades recorded yet")
        print()
        
        # 4. Performance Metrics
        print("📊 STEP 4: Performance Metrics")
        success_rate = metrics_collector.get_success_rate(7)
        response_stats = metrics_collector.get_stats('response_time', 7)
        print(f"   Success rate: {success_rate:.1f}%")
        print(f"   Avg response: {response_stats['avg']:.0f}ms")
        print()
        
        # 5. GitHub Backup
        print("💾 STEP 5: GitHub Backup")
        if github_manager.is_repo_initialized():
            if github_manager.has_changes():
                print("   Changes detected, committing...")
                success = commit_workspace(f"Auto-optimization cycle #{self.optimization_cycles}")
                if success:
                    print("   ✅ Backed up to GitHub")
                else:
                    print("   ⚠️ Backup failed (check remote)")
            else:
                print("   ℹ️ No changes to backup")
        else:
            print("   ⚠️ GitHub not initialized")
            print("   Run: github_manager.set_remote('https://github.com/YOURNAME/repo.git')")
        print()
        
        # 6. Generate Dashboard
        print("📱 STEP 6: Generate Dashboard")
        dashboard_path = metrics_collector.save_dashboard()
        print(f"   ✅ Dashboard: file://{Path(dashboard_path).absolute()}")
        print()
        
        print("="*70)
        print("✅ OPTIMIZATION CYCLE COMPLETE")
        print("="*70)
        print()
        
        return {
            'health': health['status'],
            'success_rate': success_rate,
            'insights_count': len(insights),
            'cycle': self.optimization_cycles
        }
    
    def get_system_status(self) -> dict:
        """Get complete system status"""
        return {
            'optimization_cycles': self.optimization_cycles,
            'health': health_monitor.get_summary(),
            'metrics': {
                'success_rate_7d': metrics_collector.get_success_rate(7),
                'avg_response_ms': metrics_collector.get_stats('response_time', 7)['avg']
            },
            'meta_learning': {
                'insights': len(meta_learner.generate_insights())
            },
            'github': {
                'initialized': github_manager.is_repo_initialized(),
                'has_changes': github_manager.has_changes()
            }
        }
    
    def print_status(self):
        """Print full system status"""
        status = self.get_system_status()
        
        print("="*70)
        print("🤖 SELF-OPTIMIZATION MASTER STATUS")
        print("="*70)
        print()
        print(f"Optimization cycles: {status['optimization_cycles']}")
        print()
        print(f"Health: {status['health']['status']}")
        print(f"Success rate: {status['metrics']['success_rate_7d']:.1f}%")
        print(f"Avg response: {status['metrics']['avg_response_ms']:.0f}ms")
        print()
        print(f"GitHub: {'✅' if status['github']['initialized'] else '❌'} {'(changes pending)' if status['github']['has_changes'] else ''}")
        print()
        print("="*70)


# Global instance
self_optimization = SelfOptimizationMaster()

# Demo
if __name__ == "__main__":
    print("="*70)
    print("🚀 SELF-OPTIMIZATION MASTER")
    print("="*70)
    print()
    
    # Show status
    self_optimization.print_status()
    print()
    
    # Run optimization
    result = self_optimization.run_full_optimization()
    
    print("\nNext steps:")
    print("1. Initialize GitHub: github_manager.init_repo() + set_remote()")
    print("2. Run optimization daily: self_optimization.run_full_optimization()")
    print("3. Check dashboard: open memory/dashboard.html")
