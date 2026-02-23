#!/usr/bin/env python3
"""
Optimized Full Scanner
Uses Kelly sizing, correlation filter, advanced SMC, and backtesting
"""

import sys
sys.path.insert(0, '/Users/sigbotti/.openclaw/workspace/agents/options-trading')

import asyncio
from datetime import datetime
from full_scanner import FullLiveScanner, print_comprehensive_report
from optimizations import (
    KellyPositionSizer, 
    CorrelationFilter, 
    MarketRegimeDetector
)

class OptimizedScanner:
    """Full scanner with all optimizations applied"""
    
    def __init__(self, account_value: float = 10000):
        self.base_scanner = FullLiveScanner()
        self.kelly = KellyPositionSizer(account_value=account_value)
        self.correlation = CorrelationFilter(max_correlation=0.7)
        self.regime = MarketRegimeDetector()
        
        # Default VIX (would fetch real VIX in production)
        self.current_vix = 20  # Update this daily
    
    async def scan(self):
        """Run optimized scan"""
        print("="*80)
        print("🔴 OPTIMIZED MULTI-AGENT SCANNER")
        print("Kelly Sizing | Correlation Filter | Advanced SMC | Regime Detection")
        print("="*80)
        print()
        
        # Check market regime
        regime_info = self.regime.detect_regime(self.current_vix)
        print(f"📊 MARKET REGIME: {regime_info['regime']}")
        print(f"   VIX: {regime_info['vix']} | Action: {regime_info['action']}")
        print(f"   Strategy: {regime_info['recommendation']}")
        print()
        
        # Get base signals
        signals = await self.base_scanner.scan()
        
        if not signals:
            print("❌ No signals found")
            return []
        
        print(f"\n✅ Found {len(signals)} raw signals")
        
        # Step 1: Apply correlation filter
        print("\n📊 Applying correlation filter...")
        for signal in signals:
            self.correlation.update_price_history(
                signal.symbol, 
                signal.price
            )
        
        signal_dicts = [s.__dict__ for s in signals]
        filtered = self.correlation.filter_correlated_signals(signal_dicts)
        print(f"   ✓ Filtered to {len(filtered)} uncorrelated signals")
        
        # Step 2: Apply Kelly sizing
        print("\n💰 Calculating Kelly position sizes...")
        for sig in filtered:
            # Estimate option price (roughly 5% of stock price for ATM)
            option_price = sig['price'] * 0.05
            
            kelly_result = self.kelly.size_from_signal(
                win_probability=sig['confidence'],
                risk_reward=sig['risk_reward'],
                option_price=option_price
            )
            
            sig['kelly'] = kelly_result
            sig['max_contracts'] = kelly_result['max_contracts']
            sig['risk_amount'] = kelly_result['risk_amount']
        
        print(f"   ✓ Position sizing complete")
        
        return filtered

def print_optimized_report(signals):
    """Print report with optimization details"""
    if not signals:
        print("\n❌ No signals after optimization")
        return
    
    print("\n" + "="*80)
    print("🏆 TOP OPTIMIZED SIGNALS")
    print("="*80)
    
    for i, sig in enumerate(signals[:5], 1):
        emoji = "🟢" if sig['direction'] == "CALL" else "🔴"
        
        print(f"\n{i}. {emoji} {sig['symbol']} | {sig['direction']}")
        print(f"   Price: ${sig['price']:.2f} | Move Potential: {sig['move_potential_score']}/100")
        
        # Kelly sizing
        kelly = sig.get('kelly', {})
        print(f"\n   💰 POSITION SIZING (Kelly):")
        print(f"      Kelly %: {kelly.get('kelly_pct', 0):.1f}% (raw)")
        print(f"      Recommended: {kelly.get('recommended_pct', 0):.1f}% (adjusted)")
        print(f"      Max Contracts: {sig.get('max_contracts', 1)}")
        print(f"      Risk Amount: ${sig.get('risk_amount', 0):.2f}")
        
        # Trade setup
        print(f"\n   📈 TRADE SETUP:")
        print(f"      Entry: ${sig['entry']:.2f}")
        print(f"      Stop: ${sig['stop']:.2f} | Target: ${sig['target_2']:.2f}")
        print(f"      R:R = 1:{sig['risk_reward']:.1f}")
        print(f"      Confidence: {sig['confidence']:.0%}")
        
        # SMC signals if any
        if sig.get('smc_signals'):
            print(f"\n   📊 SMC:")
            for smc in sig['smc_signals'][:2]:
                print(f"      {smc}")
        
        # Catalysts
        print(f"\n   🚀 CATALYSTS:")
        for cat in sig.get('catalysts', [])[:2]:
            print(f"      {cat}")
    
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"Total Signals: {len(signals)}")
    
    total_risk = sum(s.get('risk_amount', 0) for s in signals[:5])
    print(f"Total Risk (Top 5): ${total_risk:.2f}")
    print(f"Avg Kelly %: {sum(s.get('kelly', {}).get('recommended_pct', 0) for s in signals) / len(signals):.1f}%")
    print("="*80)

async def main():
    # Set your account value here
    ACCOUNT_VALUE = 10000  # Change this to your account size
    
    scanner = OptimizedScanner(account_value=ACCOUNT_VALUE)
    signals = await scanner.scan()
    print_optimized_report(signals)
    
    print("\n💡 NEXT STEPS:")
    print("   1. Check market regime before trading")
    print("   2. Use Kelly position sizes (not fixed amounts)")
    print("   3. Don't trade correlated stocks together")
    print("   4. Update VIX daily for regime detection")

if __name__ == "__main__":
    asyncio.run(main())
