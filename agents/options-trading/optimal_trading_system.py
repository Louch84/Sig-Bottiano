#!/usr/bin/env python3
"""
OPTIMAL TRADING SYSTEM
Integrates LangGraph workflow with existing systems
Best of both worlds: state management + proven trading logic
"""

import sys
sys.path.insert(0, '/Users/sigbotti/.openclaw/workspace')
sys.path.insert(0, '/Users/sigbotti/.openclaw/workspace/agents/options-trading')

from typing import List, Dict, Optional
from datetime import datetime
import time

# Import both systems
from langgraph_scanner import LangGraphTradingScanner
from optimized_scanner import OptimizedScanner
try:
    from watchlist import get_under_50_watchlist
except ImportError:
    # Fallback watchlist
    def get_under_50_watchlist():
        return ['AMC', 'GME', 'SOFI', 'RIVN', 'LCID', 'F', 'AAL', 'BAC', 'INTC', 'T', 'NOK', 'PLTR', 'SNAP', 'UBER', 'LYFT']

class OptimalTradingSystem:
    """
    Optimal trading system combining:
    - LangGraph workflow (state management, error recovery)
    - Existing optimized scanner (proven trading logic)
    - Self-improvement tracking
    - Performance monitoring
    """
    
    def __init__(self, account_value: float = 10000, use_langgraph: bool = True):
        self.account_value = account_value
        self.use_langgraph = use_langgraph
        
        # Initialize scanners
        if use_langgraph:
            print("🚀 Using LangGraph workflow scanner")
            self.scanner = LangGraphTradingScanner(account_value)
        else:
            print("⚡ Using optimized scanner (legacy mode)")
            self.scanner = OptimizedScanner(account_value)
        
        # Performance tracking
        self.scan_count = 0
        self.total_time_ms = 0
        self.signals_generated = 0
    
    def scan_single(self, symbol: str) -> Dict:
        """Scan single symbol with optimal workflow"""
        start = time.time()
        
        if self.use_langgraph:
            # Use LangGraph state management
            result = self.scanner.scan_symbol(symbol)
        else:
            # Use legacy scanner
            result = self._legacy_scan(symbol)
        
        elapsed_ms = int((time.time() - start) * 1000)
        
        # Track performance
        self.scan_count += 1
        self.total_time_ms += elapsed_ms
        if result.get('signal'):
            self.signals_generated += 1
        
        return result
    
    def scan_watchlist(self, min_confidence: float = 0.6) -> List[Dict]:
        """Scan full watchlist with optimal batching"""
        watchlist = get_under_50_watchlist()
        
        print(f"📊 Scanning {len(watchlist)} stocks with optimal workflow...")
        print(f"   Account: ${self.account_value:,}")
        print(f"   Min confidence: {min_confidence:.0%}")
        print()
        
        start = time.time()
        
        if self.use_langgraph and hasattr(self.scanner, 'scan_multiple'):
            # Use LangGraph batch processing
            results = self.scanner.scan_multiple(watchlist[:15])  # Top 15
        else:
            # Sequential scanning with progress
            results = []
            for i, symbol in enumerate(watchlist[:15]):
                print(f"[{i+1}/15] {symbol}...", end=" ")
                result = self.scan_single(symbol)
                
                if result.get('signal') and result.get('confidence', 0) >= min_confidence:
                    sig = result['signal']
                    print(f"🎯 {sig['direction']} (conf: {sig['confidence']:.0%})")
                else:
                    print("➖ No signal")
                
                results.append(result)
        
        elapsed = time.time() - start
        
        # Filter top signals
        signals = [r['signal'] for r in results 
                   if r.get('signal') and r.get('confidence', 0) >= min_confidence]
        signals.sort(key=lambda x: x.get('confidence', 0), reverse=True)
        
        # Print summary
        print()
        print("="*70)
        print(f"✅ SCAN COMPLETE")
        print(f"   Time: {elapsed:.1f}s ({elapsed/len(watchlist[:15]):.2f}s per stock)")
        print(f"   Signals: {len(signals)} above {min_confidence:.0%} confidence")
        print("="*70)
        print()
        
        if signals:
            print("🎯 TOP SIGNALS:")
            for i, sig in enumerate(signals[:5], 1):
                emoji = "📈" if sig['direction'] == 'CALL' else "📉" if sig['direction'] == 'PUT' else "➖"
                print(f"   {i}. {emoji} {sig['symbol']} {sig['direction']}")
                print(f"      Confidence: {sig['confidence']:.0%} | Score: {sig['score']:.0f}/100")
                if sig.get('kelly_contracts'):
                    print(f"      Position: {sig['kelly_contracts']} contracts | Risk: ${sig['kelly_risk']:.2f}")
                print()
        
        return signals
    
    def quick_scan(self, symbols: List[str]) -> List[Dict]:
        """Quick scan for specific symbols"""
        print(f"⚡ Quick scan: {', '.join(symbols)}")
        print()
        
        signals = []
        for symbol in symbols:
            result = self.scan_single(symbol)
            if result.get('signal') and result.get('confidence', 0) >= 0.55:
                signals.append(result['signal'])
        
        return sorted(signals, key=lambda x: x.get('confidence', 0), reverse=True)
    
    def get_performance_stats(self) -> Dict:
        """Get scanner performance statistics"""
        avg_time = self.total_time_ms / self.scan_count if self.scan_count > 0 else 0
        
        return {
            'total_scans': self.scan_count,
            'signals_generated': self.signals_generated,
            'avg_time_ms': avg_time,
            'success_rate': self.signals_generated / self.scan_count if self.scan_count > 0 else 0
        }
    
    def _legacy_scan(self, symbol: str) -> Dict:
        """Fallback to legacy scanner"""
        # This would call the optimized scanner
        # For now, return minimal structure
        return {
            'symbol': symbol,
            'signal': None,
            'confidence': 0
        }


# CLI Interface
def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Optimal Trading System')
    parser.add_argument('--account', type=float, default=10000, help='Account value')
    parser.add_argument('--mode', choices=['full', 'quick', 'legacy'], default='full',
                       help='Scan mode')
    parser.add_argument('--confidence', type=float, default=0.6, help='Min confidence')
    parser.add_argument('--symbols', nargs='+', help='Specific symbols to scan')
    
    args = parser.parse_args()
    
    print("="*70)
    print("🎯 OPTIMAL TRADING SYSTEM")
    print("="*70)
    print(f"Mode: {args.mode}")
    print(f"LangGraph: {'✅' if args.mode != 'legacy' else '❌'}")
    print()
    
    # Initialize
    use_langgraph = args.mode != 'legacy'
    system = OptimalTradingSystem(account_value=args.account, use_langgraph=use_langgraph)
    
    # Run scan
    if args.symbols:
        signals = system.quick_scan(args.symbols)
    elif args.mode == 'quick':
        # Quick scan of top 5
        signals = system.quick_scan(['AMC', 'GME', 'SOFI', 'RIVN', 'LCID'])
    else:
        # Full scan
        signals = system.scan_watchlist(min_confidence=args.confidence)
    
    # Print final stats
    stats = system.get_performance_stats()
    print()
    print("📊 Performance:")
    print(f"   Scans: {stats['total_scans']}")
    print(f"   Avg time: {stats['avg_time_ms']:.0f}ms")
    print(f"   Signals: {stats['signals_generated']}")
    
    return signals


if __name__ == "__main__":
    signals = main()
