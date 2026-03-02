#!/usr/bin/env python3
"""
🔴 UNIFIED OPTIONS SCANNER
One scanner, four modes. Replace 9 scattered scanners with one cohesive system.

Modes:
  - quick:     5 stocks, 5 sec, basic signals (ultra-fast)
  - standard:  Full scan with SMC + catalysts (balanced)
  - breakout:  Consolidation + squeeze patterns (F-style 400% plays)
  - optimized: Kelly + Correlation + Regime detection (full optimization)

Usage:
  python unified_scanner.py --mode quick
  python unified_scanner.py --mode standard --watchlist AMZN,TSLA,NVDA
  python unified_scanner.py --mode breakout
  python unified_scanner.py --mode optimized --account-value 25000
"""

import sys
import argparse
import asyncio
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

import yfinance as yf
import pandas as pd
import numpy as np

# Import optimization modules (for optimized mode)
try:
    from optimizations import KellyPositionSizer, CorrelationFilter, MarketRegimeDetector
    OPTIMIZATIONS_AVAILABLE = True
except ImportError:
    OPTIMIZATIONS_AVAILABLE = False
    print("⚠️  Optimizations module not found - running in basic mode")

# ============================================================================
# SHARED DATA LAYER - Avoid duplicate API calls
# ============================================================================

class DataCache:
    """Cache for stock data - fetch once, use everywhere"""
    
    def __init__(self):
        self._cache = {}
        self._timestamps = {}
        self._max_age_seconds = 300  # 5 min cache
    
    def get(self, symbol: str) -> Optional[Dict]:
        """Get cached data if fresh"""
        if symbol not in self._cache:
            return None
        
        age = (datetime.now() - self._timestamps[symbol]).total_seconds()
        if age > self._max_age_seconds:
            del self._cache[symbol]
            del self._timestamps[symbol]
            return None
        
        return self._cache[symbol]
    
    def set(self, symbol: str, data: Dict):
        """Cache data with timestamp"""
        self._cache[symbol] = data
        self._timestamps[symbol] = datetime.now()
    
    def clear(self):
        """Clear all cache"""
        self._cache = {}
        self._timestamps = {}

# Global cache instance
DATA_CACHE = DataCache()

# ============================================================================
# CORE DATA FETCHING - Single source of truth
# ============================================================================

def fetch_stock_data(symbol: str, period: str = "1mo") -> Optional[Dict]:
    """
    Fetch all stock data in ONE yfinance call
    Returns dict with price, history, info, options
    """
    # Check cache first
    cached = DATA_CACHE.get(symbol)
    if cached:
        return cached
    
    try:
        ticker = yf.Ticker(symbol)
        
        # Fetch everything at once
        info = ticker.info
        hist = ticker.history(period=period)
        
        if hist.empty or len(hist) < 5:
            return None
        
        current_price = info.get('currentPrice', hist['Close'].iloc[-1])
        
        data = {
            'symbol': symbol,
            'ticker': ticker,
            'info': info,
            'history': hist,
            'current_price': current_price,
            'volume_20d_avg': hist['Volume'].tail(20).mean(),
            'high_20d': hist['High'].tail(20).max(),
            'low_20d': hist['Low'].tail(20).min(),
            'change_1d': ((hist['Close'].iloc[-1] - hist['Close'].iloc[-2]) / hist['Close'].iloc[-2]) * 100 if len(hist) > 1 else 0,
            'change_5d': ((hist['Close'].iloc[-1] - hist['Close'].iloc[-5]) / hist['Close'].iloc[-5]) * 100 if len(hist) > 5 else 0,
        }
        
        # Cache it
        DATA_CACHE.set(symbol, data)
        
        return data
        
    except Exception as e:
        return None

# ============================================================================
# MODE 1: QUICK SCANNER - Ultra-Fast, Low-Cost
# ============================================================================

class QuickScanner:
    """5 stocks, 5 seconds, basic signals only"""
    
    DEFAULT_WATCHLIST = ["AMC", "GME", "MARA", "SOFI", "TSLA"]
    
    def __init__(self, watchlist: List[str] = None):
        self.watchlist = watchlist or self.DEFAULT_WATCHLIST
    
    async def scan(self) -> List[Dict]:
        """Ultra-fast scan"""
        print("⚡ QUICK SCAN MODE")
        print(f"Watchlist: {len(self.watchlist)} stocks | Target: 5-10 seconds")
        print()
        
        signals = []
        
        for symbol in self.watchlist:
            data = fetch_stock_data(symbol, period="5d")
            if not data:
                continue
            
            info = data['info']
            price = data['current_price']
            
            # Skip if over $50
            if price >= 50:
                continue
            
            # Quick metrics
            change = data['change_1d']
            volume_ratio = data['history']['Volume'].iloc[-1] / data['history']['Volume'].mean()
            short_pct = info.get('shortPercentOfFloat', 0) * 100
            
            # Simple scoring
            score = 0
            direction = "CALL" if change > 0 else "PUT"
            
            if short_pct > 20:
                score += 30
            if volume_ratio > 2:
                score += 20
            if abs(change) > 3:
                score += 20
            
            if score >= 30:
                signals.append({
                    'mode': 'quick',
                    'symbol': symbol,
                    'price': price,
                    'direction': direction,
                    'score': score,
                    'change': change,
                    'short': short_pct,
                    'volume_ratio': volume_ratio,
                    'confidence': min(score / 100, 0.85)
                })
        
        # Sort by score
        signals.sort(key=lambda x: x['score'], reverse=True)
        return signals

# ============================================================================
# MODE 2: STANDARD SCANNER - Full Scan with SMC + Catalysts
# ============================================================================

class StandardScanner:
    """Comprehensive scan with SMC, catalysts, full analysis"""
    
    DEFAULT_WATCHLIST = [
        "AMC", "GME", "TSLA", "NVDA", "AMD", "AAPL", "MSFT", "AMZN",
        "SOFI", "PLTR", "RIVN", "LCID", "NIO", "BABA", "COIN", "MARA",
        "RIOT", "DKNG", "UBER", "LYFT", "ABNB", "SNAP", "PINS", "SPOT"
    ]
    
    def __init__(self, watchlist: List[str] = None):
        self.watchlist = watchlist or self.DEFAULT_WATCHLIST
    
    async def scan(self) -> List[Dict]:
        """Full standard scan"""
        print("📊 STANDARD SCAN MODE")
        print(f"Watchlist: {len(self.watchlist)} stocks | SMC + Catalysts enabled")
        print()
        
        signals = []
        
        for symbol in self.watchlist:
            data = fetch_stock_data(symbol)
            if not data:
                continue
            
            signal = self._analyze_symbol(symbol, data)
            if signal and signal['score'] >= 50:
                signals.append(signal)
        
        signals.sort(key=lambda x: x['score'], reverse=True)
        return signals
    
    def _analyze_symbol(self, symbol: str, data: Dict) -> Optional[Dict]:
        """Analyze single symbol for standard mode"""
        info = data['info']
        price = data['current_price']
        hist = data['history']
        
        # Skip expensive stocks
        if price > 200:
            return None
        
        # Calculate metrics
        change_1d = data['change_1d']
        change_5d = data['change_5d']
        volume_ratio = hist['Volume'].iloc[-1] / hist['Volume'].tail(20).mean()
        short_pct = info.get('shortPercentOfFloat', 0) * 100
        
        # SMC-style analysis (simplified)
        recent_high = hist['High'].tail(5).max()
        recent_low = hist['Low'].tail(5).min()
        position_in_range = (price - recent_low) / (recent_high - recent_low) if recent_high > recent_low else 0.5
        
        # Scoring
        score = 0
        direction = "CALL" if change_1d > 0 else "PUT"
        
        # Momentum (0-30)
        if abs(change_1d) > 5:
            score += 30
        elif abs(change_1d) > 3:
            score += 20
        elif abs(change_1d) > 1:
            score += 10
        
        # Volume (0-25)
        if volume_ratio > 3:
            score += 25
        elif volume_ratio > 2:
            score += 15
        elif volume_ratio > 1.5:
            score += 10
        
        # Short squeeze potential (0-25)
        if short_pct > 30:
            score += 25
        elif short_pct > 20:
            score += 15
        elif short_pct > 10:
            score += 10
        
        # SMC position (0-20)
        if position_in_range < 0.3:  # Near support
            score += 20 if direction == "CALL" else 5
        elif position_in_range > 0.7:  # Near resistance
            score += 20 if direction == "PUT" else 5
        
        # Catalysts (simplified - would integrate with news API in production)
        catalysts = []
        if volume_ratio > 3:
            catalysts.append("Unusual volume")
        if short_pct > 20:
            catalysts.append(f"High short interest ({short_pct:.0f}%)")
        if abs(change_1d) > 5:
            catalysts.append(f"Big move today ({change_1d:+.1f}%)")
        
        if score >= 50:
            return {
                'mode': 'standard',
                'symbol': symbol,
                'price': price,
                'direction': direction,
                'score': score,
                'confidence': min(score / 100, 0.90),
                'change_1d': change_1d,
                'change_5d': change_5d,
                'volume_ratio': volume_ratio,
                'short_pct': short_pct,
                'smc_position': position_in_range,
                'support': recent_low,
                'resistance': recent_high,
                'catalysts': catalysts,
                'entry': price,
                'stop': recent_low if direction == "CALL" else recent_high,
                'target_1': recent_high if direction == "CALL" else recent_low,
                'risk_reward': abs((recent_high - recent_low) / price) * 10 if direction == "CALL" else abs((recent_low - recent_high) / price) * 10
            }
        
        return None

# ============================================================================
# MODE 3: BREAKOUT SCANNER - Consolidation + Squeeze Patterns
# ============================================================================

class BreakoutScanner:
    """F-style 400% breakout plays - coiled spring near resistance"""
    
    DEFAULT_WATCHLIST = [
        'F', 'AMC', 'GME', 'RIVN', 'LCID', 'SOFI', 'PLTR', 'NOK', 'BAC',
        'T', 'KMI', 'XOM', 'OXY', 'UBER', 'AAL', 'CCL', 'NCLH', 'MARA', 'RIOT'
    ]
    
    def __init__(self, watchlist: List[str] = None):
        self.watchlist = watchlist or self.DEFAULT_WATCHLIST
        self.min_consolidation_days = 3
        self.max_range_pct = 4.0
        self.min_volume = 1000000
        self.max_price = 50.0
    
    async def scan(self) -> List[Dict]:
        """Scan for breakout squeeze setups"""
        print("🎯 BREAKOUT SCANNER MODE")
        print(f"Scanning {len(self.watchlist)} stocks for F-style breakout plays")
        print(f"Criteria: Tight consolidation + Near resistance + Cheap options")
        print()
        
        setups = []
        
        for symbol in self.watchlist:
            data = fetch_stock_data(symbol, period="1mo")
            if not data:
                continue
            
            setup = self._analyze_breakout(symbol, data)
            if setup and setup['confidence'] >= 60:
                setups.append(setup)
                print(f"✅ {symbol}: {setup['quality']} setup ({setup['confidence']}% confidence)")
            elif setup:
                print(f"⚠️  {symbol}: {setup['quality']} ({setup['confidence']}%) - below threshold")
        
        setups.sort(key=lambda x: x['confidence'], reverse=True)
        return setups
    
    def _analyze_consolidation(self, hist: pd.DataFrame) -> Dict:
        """Analyze consolidation pattern"""
        if len(hist) < 5:
            return {'is_consolidating': False}
        
        recent = hist.tail(5)
        high_5d = recent['High'].max()
        low_5d = recent['Low'].min()
        range_pct = ((high_5d - low_5d) / low_5d) * 100
        
        is_tight = range_pct < self.max_range_pct
        
        days_in_range = sum(1 for i in range(len(recent)) if low_5d <= recent['Close'].iloc[i] <= high_5d)
        
        return {
            'is_consolidating': is_tight and days_in_range >= 4,
            'range_pct': round(range_pct, 2),
            'high_5d': high_5d,
            'low_5d': low_5d,
            'days_in_range': days_in_range
        }
    
    def _analyze_breakout(self, symbol: str, data: Dict) -> Optional[Dict]:
        """Analyze single symbol for breakout setup"""
        info = data['info']
        price = data['current_price']
        hist = data['history']
        
        # Skip if too expensive
        if price > self.max_price:
            return None
        
        # Check volume
        if data['volume_20d_avg'] < self.min_volume:
            return None
        
        # Analyze consolidation
        consolidation = self._analyze_consolidation(hist)
        if not consolidation['is_consolidating']:
            return None
        
        # Find resistance
        resistance = data['high_20d']
        distance_to_resistance = ((resistance - price) / price) * 100
        
        if distance_to_resistance > 5.0:
            return None
        
        # Calculate confidence
        score = 0
        
        # Tight consolidation (0-40)
        if consolidation['range_pct'] < 2.0:
            score += 40
        elif consolidation['range_pct'] < 3.0:
            score += 30
        elif consolidation['range_pct'] < 4.0:
            score += 20
        
        # Near resistance (0-30)
        if distance_to_resistance < 2.0:
            score += 30
        elif distance_to_resistance < 4.0:
            score += 20
        elif distance_to_resistance < 5.0:
            score += 10
        
        # Momentum (0-30)
        if data['change_5d'] > 5:
            score += 30
        elif data['change_5d'] > 2:
            score += 20
        elif data['change_5d'] > 0:
            score += 10
        
        # Determine quality
        if score >= 75:
            quality = "EXCELLENT"
        elif score >= 60:
            quality = "GOOD"
        elif score >= 45:
            quality = "FAIR"
        else:
            quality = "WEAK"
        
        if score < 50:
            return None
        
        # Build thesis
        thesis = f"Consolidation: {consolidation['range_pct']:.1f}% range over {consolidation['days_in_range']} days. "
        thesis += f"Resistance at ${resistance:.2f} ({distance_to_resistance:.1f}% away). "
        thesis += f"Setup for explosive breakout."
        
        return {
            'mode': 'breakout',
            'symbol': symbol,
            'price': price,
            'consolidation_days': consolidation['days_in_range'],
            'range_pct': consolidation['range_pct'],
            'resistance_level': resistance,
            'distance_to_resistance': distance_to_resistance,
            'confidence': score,
            'quality': quality,
            'thesis': thesis,
            'entry': price,
            'target': resistance * 1.15,  # 15% breakout target
            'stop': consolidation['low_5d']
        }

# ============================================================================
# MODE 4: OPTIMIZED SCANNER - Kelly + Correlation + Regime
# ============================================================================

class OptimizedScanner:
    """Full optimization: Kelly sizing, correlation filter, regime detection"""
    
    DEFAULT_WATCHLIST = [
        "TSLA", "NVDA", "AMD", "AAPL", "MSFT", "AMZN", "GOOGL", "META",
        "SOFI", "PLTR", "COIN", "MARA", "RIOT", "DKNG", "UBER", "ABNB"
    ]
    
    def __init__(self, watchlist: List[str] = None, account_value: float = 10000):
        self.watchlist = watchlist or self.DEFAULT_WATCHLIST
        self.account_value = account_value
        
        if OPTIMIZATIONS_AVAILABLE:
            self.kelly = KellyPositionSizer(account_value=account_value)
            self.correlation = CorrelationFilter(max_correlation=0.7)
            self.regime = MarketRegimeDetector()
            self.current_vix = 20  # Would fetch real VIX in production
        else:
            self.kelly = None
            self.correlation = None
            self.regime = None
            self.current_vix = None
    
    async def scan(self) -> List[Dict]:
        """Run optimized scan with all enhancements"""
        print("🔴 OPTIMIZED SCAN MODE")
        print(f"Account: ${self.account_value:,} | Kelly + Correlation + Regime")
        print()
        
        # Check market regime
        if self.regime:
            regime_info = self.regime.detect_regime(self.current_vix)
            print(f"📊 MARKET REGIME: {regime_info['regime']}")
            print(f"   VIX: {regime_info['vix']} | Action: {regime_info['action']}")
            print(f"   Strategy: {regime_info['recommendation']}")
            print()
        else:
            print("⚠️  Regime detection unavailable (optimizations module not loaded)")
            print()
        
        # Get base signals (use standard scanner as base)
        standard = StandardScanner(self.watchlist)
        signals = await standard.scan()
        
        if not signals:
            print("❌ No signals found")
            return []
        
        print(f"\n✅ Found {len(signals)} raw signals")
        
        # Apply correlation filter
        if self.correlation:
            print("\n📊 Applying correlation filter...")
            for signal in signals:
                self.correlation.update_price_history(signal['symbol'], signal['price'])
            
            filtered = self.correlation.filter_correlated_signals(signals)
            print(f"   ✓ Filtered to {len(filtered)} uncorrelated signals")
            signals = filtered
        else:
            print("\n⚠️  Correlation filter unavailable")
        
        # Apply Kelly sizing
        if self.kelly:
            print("\n💰 Calculating Kelly position sizes...")
            for signal in signals:
                option_price = signal['price'] * 0.05  # Rough ATM estimate
                
                kelly_result = self.kelly.size_from_signal(
                    signal_confidence=signal['confidence'],
                    risk_reward=signal.get('risk_reward', 2.0),
                    option_price=option_price
                )
                
                signal['kelly'] = kelly_result
                signal['max_contracts'] = kelly_result['max_contracts']
                signal['risk_amount'] = kelly_result['risk_amount']
            
            print(f"   ✓ Position sizing complete")
        else:
            print("\n⚠️  Kelly sizing unavailable")
        
        return signals

# ============================================================================
# UNIFIED SCANNER - Main Entry Point
# ============================================================================

class UnifiedScanner:
    """One scanner to rule them all"""
    
    def __init__(self, mode: str = "standard", **kwargs):
        self.mode = mode
        self.kwargs = kwargs
        
        # Initialize appropriate scanner
        if mode == "quick":
            self.scanner = QuickScanner(watchlist=kwargs.get('watchlist'))
        elif mode == "standard":
            self.scanner = StandardScanner(watchlist=kwargs.get('watchlist'))
        elif mode == "breakout":
            self.scanner = BreakoutScanner(watchlist=kwargs.get('watchlist'))
        elif mode == "optimized":
            self.scanner = OptimizedScanner(
                watchlist=kwargs.get('watchlist'),
                account_value=kwargs.get('account_value', 10000)
            )
        else:
            raise ValueError(f"Unknown mode: {mode}. Use: quick, standard, breakout, optimized")
    
    async def scan(self) -> List[Dict]:
        """Run scan in selected mode"""
        return await self.scanner.scan()
    
    def print_results(self, signals: List[Dict]):
        """Print formatted results based on mode"""
        if not signals:
            print("\n❌ No signals found")
            return
        
        print("\n" + "="*80)
        print(f"🏆 {self.mode.upper()} MODE - SIGNALS FOUND")
        print("="*80)
        
        for i, sig in enumerate(signals[:10], 1):
            emoji = "🟢" if sig['direction'] == "CALL" else "🔴"
            
            if self.mode == "quick":
                print(f"\n{i}. {emoji} {sig['symbol']} {sig['direction']} @ ${sig['price']:.2f}")
                print(f"   Score: {sig['score']} | Change: {sig['change']:+.1f}%")
                print(f"   Short: {sig['short']:.0f}% | Vol: {sig['volume_ratio']:.1f}x")
            
            elif self.mode in ["standard", "optimized"]:
                print(f"\n{i}. {emoji} {sig['symbol']} {sig['direction']} @ ${sig['price']:.2f}")
                print(f"   Score: {sig['score']} | Confidence: {sig['confidence']:.0%}")
                print(f"   Change: {sig['change_1d']:+.1f}% (1d) | {sig['change_5d']:+.1f}% (5d)")
                print(f"   Volume: {sig['volume_ratio']:.1f}x | Short: {sig['short_pct']:.0f}%")
                
                if sig.get('catalysts'):
                    print(f"   Catalysts: {', '.join(sig['catalysts'][:3])}")
                
                if self.mode == "optimized" and sig.get('kelly'):
                    kelly = sig['kelly']
                    print(f"\n   💰 KELLY SIZING:")
                    print(f"      Recommended: {kelly.get('recommended_pct', 0):.1f}% of account")
                    print(f"      Max Contracts: {sig.get('max_contracts', 1)}")
                    print(f"      Risk Amount: ${sig.get('risk_amount', 0):.2f}")
            
            elif self.mode == "breakout":
                quality_emoji = "🚀" if sig['confidence'] >= 75 else "⚡" if sig['confidence'] >= 60 else "📊"
                print(f"\n{i}. {quality_emoji} {sig['symbol']} - {sig['quality']} ({sig['confidence']}% confidence)")
                print(f"   Price: ${sig['price']:.2f}")
                print(f"   Consolidation: {sig['range_pct']:.1f}% range ({sig['consolidation_days']} days)")
                print(f"   Resistance: ${sig['resistance_level']:.2f} ({sig['distance_to_resistance']:.1f}% away)")
                print(f"   Target: ${sig['target']:.2f} | Stop: ${sig['stop']:.2f}")
                print(f"   Thesis: {sig['thesis'][:100]}...")
        
        print("\n" + "="*80)
        print(f"Total Signals: {len(signals)}")
        if self.mode == "optimized" and signals:
            total_risk = sum(s.get('risk_amount', 0) for s in signals[:5])
            print(f"Total Risk (Top 5): ${total_risk:.2f}")
        print("="*80)

# ============================================================================
# CLI ENTRY POINT
# ============================================================================

async def main():
    parser = argparse.ArgumentParser(
        description="🔴 Unified Options Scanner - One scanner, four modes",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python unified_scanner.py --mode quick
  python unified_scanner.py --mode standard --watchlist TSLA,NVDA,AAPL
  python unified_scanner.py --mode breakout
  python unified_scanner.py --mode optimized --account-value 25000
        """
    )
    
    parser.add_argument(
        '--mode', 
        type=str, 
        default='standard',
        choices=['quick', 'standard', 'breakout', 'optimized'],
        help='Scanner mode (default: standard)'
    )
    
    parser.add_argument(
        '--watchlist',
        type=str,
        default=None,
        help='Comma-separated list of symbols (e.g., TSLA,NVDA,AAPL)'
    )
    
    parser.add_argument(
        '--account-value',
        type=float,
        default=10000,
        help='Account value for Kelly sizing (optimized mode only, default: 10000)'
    )
    
    args = parser.parse_args()
    
    # Parse watchlist
    watchlist = None
    if args.watchlist:
        watchlist = [s.strip().upper() for s in args.watchlist.split(',')]
    
    # Clear cache before scan
    DATA_CACHE.clear()
    
    # Create and run scanner
    scanner = UnifiedScanner(
        mode=args.mode,
        watchlist=watchlist,
        account_value=args.account_value
    )
    
    signals = await scanner.scan()
    scanner.print_results(signals)
    
    print(f"\n✅ Scan complete at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"💡 Tip: Use --mode quick for fast checks, --mode optimized for full analysis")

if __name__ == "__main__":
    asyncio.run(main())
