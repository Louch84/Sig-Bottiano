#!/usr/bin/env python3
"""
Breakout Squeeze Scanner
Finds consolidation + breakout setups like the F 400% play
Pattern: Coiled spring near resistance with cheap OTM options
"""

import sys
sys.path.insert(0, '/Users/sigbotti/.openclaw/workspace')
sys.path.insert(0, '/Users/sigbotti/.openclaw/workspace/agents/options-trading')

import yfinance as yf
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class BreakoutSetup:
    """A breakout squeeze setup"""
    symbol: str
    current_price: float
    consolidation_days: int
    range_pct: float  # How tight the consolidation
    resistance_level: float
    distance_to_resistance: float
    suggested_strike: float
    option_cost: float
    confidence: float
    setup_quality: str  # excellent, good, fair
    thesis: str

class BreakoutSqueezeScanner:
    """
    Scanner for the F-style 400% breakout plays
    """
    
    def __init__(self):
        self.min_consolidation_days = 3
        self.max_range_pct = 4.0  # Consolidation range must be tight
        self.min_volume = 1000000  # 1M minimum daily volume
        self.max_price = 50.0  # Under $50 for cheap options
        
    def analyze_consolidation(self, df: pd.DataFrame) -> Dict:
        """
        Analyze if stock is in consolidation pattern
        """
        if len(df) < 5:
            return {'is_consolidating': False}
        
        # Get last 5 days
        recent = df.tail(5)
        
        # Calculate range
        high_5d = recent['High'].max()
        low_5d = recent['Low'].min()
        range_pct = ((high_5d - low_5d) / low_5d) * 100
        
        # Check if tight consolidation
        is_tight = range_pct < self.max_range_pct
        
        # Check volume consistency
        avg_volume = recent['Volume'].mean()
        volume_consistent = recent['Volume'].std() / avg_volume < 0.5
        
        # Count days in range
        days_in_range = 0
        for i in range(len(recent)):
            if low_5d <= recent['Close'].iloc[i] <= high_5d:
                days_in_range += 1
        
        return {
            'is_consolidating': is_tight and days_in_range >= 4,
            'range_pct': round(range_pct, 2),
            'high_5d': high_5d,
            'low_5d': low_5d,
            'days_in_range': days_in_range,
            'volume_consistent': volume_consistent,
            'avg_volume': avg_volume
        }
    
    def find_resistance(self, df: pd.DataFrame, info: Dict) -> Dict:
        """
        Find resistance level and distance
        """
        recent = df.tail(20)
        
        # Resistance = recent highs
        resistance = recent['High'].max()
        
        # Alternative: 20-day high
        high_20d = df['High'].tail(20).max()
        
        current = info.get('currentPrice', df['Close'].iloc[-1])
        
        distance = ((resistance - current) / current) * 100
        
        return {
            'resistance': resistance,
            'high_20d': high_20d,
            'distance_to_resistance': distance,
            'is_near_resistance': distance < 5.0  # Within 5%
        }
    
    def check_options(self, symbol: str, current_price: float, resistance: float) -> Dict:
        """
        Check if cheap OTM options available
        """
        try:
            ticker = yf.Ticker(symbol)
            expirations = ticker.options
            
            if not expirations:
                return {'has_options': False}
            
            # Get nearest weekly expiration (0-7 DTE)
            nearest_exp = None
            for exp in expirations[:3]:
                exp_date = datetime.strptime(exp, '%Y-%m-%d')
                days_to_exp = (exp_date - datetime.now()).days
                if 0 <= days_to_exp <= 7:
                    nearest_exp = exp
                    break
            
            if not nearest_exp:
                nearest_exp = expirations[0]  # Use first available
            
            # Get options chain
            chain = ticker.option_chain(nearest_exp)
            calls = chain.calls
            
            # Find strike just above resistance (OTM)
            otm_calls = calls[calls['strike'] > current_price]
            
            if otm_calls.empty:
                return {'has_options': False}
            
            # Get cheapest OTM call
            cheapest = otm_calls.nsmallest(3, 'lastPrice')
            
            best_option = cheapest.iloc[0]
            
            return {
                'has_options': True,
                'expiration': nearest_exp,
                'suggested_strike': best_option['strike'],
                'option_cost': best_option['lastPrice'],
                'option_bid': best_option['bid'],
                'option_ask': best_option['ask'],
                'volume': best_option['volume'],
                'open_interest': best_option['openInterest'],
                'iv': best_option['impliedVolatility'] * 100 if best_option['impliedVolatility'] else 0,
                'distance_from_price': ((best_option['strike'] - current_price) / current_price * 100)
            }
            
        except Exception as e:
            return {'has_options': False, 'error': str(e)}
    
    def calculate_confidence(self, consolidation: Dict, resistance: Dict, options: Dict) -> Tuple[float, str]:
        """
        Calculate confidence score for the setup
        """
        score = 0
        factors = []
        
        # Tight consolidation (0-40 points)
        if consolidation['range_pct'] < 2.0:
            score += 40
            factors.append("Excellent consolidation (<2%)")
        elif consolidation['range_pct'] < 3.0:
            score += 30
            factors.append("Good consolidation (<3%)")
        elif consolidation['range_pct'] < 4.0:
            score += 20
            factors.append("Fair consolidation (<4%)")
        
        # Near resistance (0-30 points)
        if resistance['distance_to_resistance'] < 2.0:
            score += 30
            factors.append("Very close to breakout (<2%)")
        elif resistance['distance_to_resistance'] < 4.0:
            score += 20
            factors.append("Near resistance (<4%)")
        elif resistance['distance_to_resistance'] < 5.0:
            score += 10
            factors.append("Approaching resistance (<5%)")
        
        # Option price vs potential (0-30 points) - higher priced can still be explosive
        if options['option_cost'] < 0.50:
            score += 30
            factors.append("Cheap options (<$0.50) - high leverage")
        elif options['option_cost'] < 1.00:
            score += 25
            factors.append("Affordable options (<$1.00) - good leverage")
        elif options['option_cost'] < 2.00:
            score += 20
            factors.append("Standard options (<$2.00) - solid setup")
        else:
            score += 10
            factors.append("Higher cost options - need perfect setup")
        
        # Determine quality
        if score >= 75:
            quality = "EXCELLENT"
        elif score >= 60:
            quality = "GOOD"
        elif score >= 45:
            quality = "FAIR"
        else:
            quality = "WEAK"
        
        return score, quality, factors
    
    def scan_symbol(self, symbol: str) -> Optional[BreakoutSetup]:
        """
        Scan a single symbol for breakout setup
        """
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period="1mo")
            info = ticker.info
            
            if len(df) < 10:
                return None
            
            current_price = info.get('currentPrice', df['Close'].iloc[-1])
            
            # Skip if too expensive
            if current_price > self.max_price:
                return None
            
            # Check volume
            avg_volume = df['Volume'].tail(20).mean()
            if avg_volume < self.min_volume:
                return None
            
            # Analyze consolidation
            consolidation = self.analyze_consolidation(df)
            if not consolidation['is_consolidating']:
                return None
            
            # Find resistance
            resistance = self.find_resistance(df, info)
            if not resistance['is_near_resistance']:
                return None
            
            # Check options
            options = self.check_options(symbol, current_price, resistance['resistance'])
            if not options['has_options']:
                return None
            
            # Skip if options too expensive (allow up to $2.00 for higher conviction setups)
            if options['option_cost'] > 2.00:
                return None
            
            # Calculate confidence
            score, quality, factors = self.calculate_confidence(consolidation, resistance, options)
            
            # Only return good setups
            if score < 50:
                return None
            
            # Build thesis
            thesis = f"Consolidation: {consolidation['range_pct']:.1f}% range over {consolidation['days_in_range']} days. "
            thesis += f"Resistance at ${resistance['resistance']:.2f} ({resistance['distance_to_resistance']:.1f}% away). "
            thesis += f"OTM calls available at ${options['suggested_strike']:.2f} for ${options['option_cost']:.2f}. "
            thesis += "Setup for explosive breakout like F."
            
            return BreakoutSetup(
                symbol=symbol,
                current_price=current_price,
                consolidation_days=consolidation['days_in_range'],
                range_pct=consolidation['range_pct'],
                resistance_level=resistance['resistance'],
                distance_to_resistance=resistance['distance_to_resistance'],
                suggested_strike=options['suggested_strike'],
                option_cost=options['option_cost'],
                confidence=score,
                setup_quality=quality,
                thesis=thesis
            )
            
        except Exception as e:
            return None
    
    def scan_watchlist(self, symbols: List[str]) -> List[BreakoutSetup]:
        """
        Scan multiple symbols
        """
        setups = []
        
        print(f"🔍 Scanning {len(symbols)} stocks for BREAKOUT SQUEEZE setups...")
        print(f"   Criteria: Tight consolidation + Near resistance + Cheap OTM options")
        print()
        
        for symbol in symbols:
            try:
                setup = self.scan_symbol(symbol)
                if setup and setup.confidence >= 60:
                    setups.append(setup)
                    print(f"✅ {symbol}: {setup.setup_quality} setup ({setup.confidence}% confidence)")
                elif setup:
                    print(f"⚠️  {symbol}: {setup.setup_quality} ({setup.confidence}% confidence) - below threshold")
            except Exception as e:
                print(f"   Error scanning {symbol}: {str(e)[:40]}")
                continue
        
        # Sort by confidence
        setups.sort(key=lambda x: x.confidence, reverse=True)
        
        return setups
    
    def print_results(self, setups: List[BreakoutSetup]):
        """
        Print formatted results
        """
        if not setups:
            print("\n❌ No breakout setups found")
            return
        
        print()
        print("="*70)
        print("🎯 BREAKOUT SQUEEZE SETUPS FOUND")
        print("="*70)
        print()
        
        for i, setup in enumerate(setups[:5], 1):
            emoji = "🚀" if setup.confidence >= 75 else "⚡" if setup.confidence >= 60 else "📊"
            print(f"{emoji} #{i} {setup.symbol} - {setup.setup_quality} ({setup.confidence}%)")
            print(f"   Price: ${setup.current_price:.2f}")
            print(f"   Consolidation: {setup.range_pct:.1f}% range ({setup.consolidation_days} days)")
            print(f"   Resistance: ${setup.resistance_level:.2f} ({setup.distance_to_resistance:.1f}% away)")
            print(f"   Play: ${setup.suggested_strike:.2f} CALL @ ${setup.option_cost:.2f}")
            print(f"   Thesis: {setup.thesis[:100]}...")
            print()
        
        print("="*70)
        print(f"Found {len(setups)} high-quality breakout setups")
        print("="*70)


# Convenience function
def scan_breakout_squeeze(symbols: List[str] = None):
    """
    Quick scan for breakout squeeze setups
    """
    if symbols is None:
        # Default watchlist - stocks known to make big moves
        symbols = [
            'F', 'AMC', 'GME', 'RIVN', 'LCID', 'SOFI', 'PLTR', 'NOK', 'BAC',
            'T', 'KMI', 'XOM', 'OXY', 'UBER', 'AAL', 'CCL', 'NCLH'
        ]
    
    scanner = BreakoutSqueezeScanner()
    setups = scanner.scan_watchlist(symbols)
    scanner.print_results(setups)
    return setups


# Demo
if __name__ == "__main__":
    print("="*70)
    print("🎯 BREAKOUT SQUEEZE SCANNER")
    print("Finds F-style 400% breakout plays")
    print("="*70)
    print()
    
    # Test on symbols including F
    scan_breakout_squeeze(['F', 'NOK', 'T', 'BAC', 'KMI', 'SOFI'])
