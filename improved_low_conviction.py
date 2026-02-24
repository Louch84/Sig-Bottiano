#!/usr/bin/env python3
"""
Improved Low Conviction Pattern
Fixed thresholds and added dynamic exits based on backtesting
"""

import sys
sys.path.insert(0, '/Users/sigbotti/.openclaw/workspace')
sys.path.insert(0, '/Users/sigbotti/.openclaw/workspace/agents/options-trading')

import yfinance as yf
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from datetime import datetime
from dataclasses import dataclass

@dataclass
class PatternVersion:
    """Different versions of the pattern to test"""
    name: str
    rvol_threshold: float
    price_change_min: float
    price_change_max: float
    hold_days: int
    exit_on_volume_spike: bool
    exit_on_sma_break: bool

class ImprovedLowConvictionDetector:
    """
    Improved Low Conviction Pattern with:
    - Relaxed volume thresholds
    - Multiple hold periods
    - Smart exit criteria
    """
    
    def __init__(self):
        # Test multiple pattern variations
        self.versions = [
            PatternVersion("Conservative", 0.3, 0.5, 3.0, 3, True, True),
            PatternVersion("Moderate", 0.5, 0.3, 5.0, 3, True, False),
            PatternVersion("Relaxed", 0.7, 0.2, 3.0, 5, False, True),
            PatternVersion("Quick_Exit", 0.5, 0.5, 5.0, 1, True, True),
            PatternVersion("Hold_3d", 0.5, 0.5, 5.0, 3, True, True),
            PatternVersion("Hold_5d", 0.5, 0.5, 5.0, 5, True, True),
        ]
    
    def detect(self, df: pd.DataFrame, info: Dict, 
               version: PatternVersion = None) -> Dict:
        """
        Detect low conviction pattern with configurable thresholds
        """
        if version is None:
            version = self.versions[1]  # Default to Moderate
        
        if len(df) < 20:
            return {'pattern_found': False, 'reason': 'insufficient_data'}
        
        try:
            current_price = info.get('currentPrice', info.get('regularMarketPrice', 0))
            prev_close = info.get('previousClose', 0)
            today_volume = info.get('volume', info.get('regularMarketVolume', 0))
            
            if current_price == 0 or today_volume == 0:
                return {'pattern_found': False, 'reason': 'missing_data'}
            
            # Price change
            price_change = ((current_price - prev_close) / prev_close * 100) if prev_close else 0
            
            # RVOL calculation
            avg_volume_20d = df['Volume'].tail(20).mean()
            rvol = today_volume / avg_volume_20d if avg_volume_20d > 0 else 1
            
            # Moving averages
            closes = df['Close'].values
            sma20 = pd.Series(closes).rolling(20).mean().iloc[-1]
            sma50 = pd.Series(closes).rolling(50).mean().iloc[-1] if len(closes) >= 50 else None
            
            # Distance to highs
            high_20d = df['High'].tail(20).max()
            distance_to_high = ((high_20d - current_price) / current_price * 100)
            
            # IMPROVED CRITERIA with version parameters
            checks = {
                'price_up_min': price_change > version.price_change_min,
                'price_up_max': price_change < version.price_change_max,  # Not too extended
                'low_volume': rvol < version.rvol_threshold,
                'above_sma20': current_price > sma20,
                'near_highs': distance_to_high < 5.0  # Relaxed from 3%
            }
            
            criteria_met = sum(checks.values())
            pattern_found = criteria_met >= 4  # 4 out of 5 criteria
            
            return {
                'pattern_found': pattern_found,
                'version': version.name,
                'confidence': (criteria_met / 5) * 100,
                'price_change': round(price_change, 2),
                'rvol': round(rvol, 2),
                'checks': checks,
                'criteria_met': criteria_met,
                'suggested_hold': version.hold_days,
                'exit_rules': {
                    'volume_spike': version.exit_on_volume_spike,
                    'sma_break': version.exit_on_sma_break,
                    'time_stop': version.hold_days
                }
            }
            
        except Exception as e:
            return {'pattern_found': False, 'error': str(e)}
    
    def backtest_version(self, symbol: str, version: PatternVersion, 
                         period: str = "2y") -> Dict:
        """Backtest a specific pattern version"""
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=period)
        info = ticker.info
        
        trades = []
        
        for i in range(20, len(df) - 10):
            # Create info dict for this day
            day_info = {
                'currentPrice': df['Close'].iloc[i],
                'previousClose': df['Close'].iloc[i-1],
                'volume': df['Volume'].iloc[i],
                'regularMarketPrice': df['Close'].iloc[i],
                'regularMarketVolume': df['Volume'].iloc[i]
            }
            
            # Check for pattern
            signal = self.detect(df.iloc[:i+1], day_info, version)
            
            if signal['pattern_found']:
                entry_price = df['Close'].iloc[i]
                entry_date = df.index[i]
                
                # Simulate trade with exit rules
                exit_price = None
                exit_date = None
                exit_reason = None
                
                for j in range(1, min(version.hold_days + 1, len(df) - i)):
                    current_idx = i + j
                    current_close = df['Close'].iloc[current_idx]
                    current_volume = df['Volume'].iloc[current_idx]
                    avg_volume = df['Volume'].iloc[i-20:i].mean()
                    
                    # Check exit conditions
                    if version.exit_on_volume_spike and current_volume > avg_volume * 2:
                        exit_price = current_close
                        exit_date = df.index[current_idx]
                        exit_reason = 'volume_spike'
                        break
                    
                    if version.exit_on_sma_break:
                        sma20 = df['Close'].iloc[i-20:current_idx].mean()
                        if current_close < sma20:
                            exit_price = current_close
                            exit_date = df.index[current_idx]
                            exit_reason = 'sma_break'
                            break
                
                # Time-based exit
                if exit_price is None:
                    exit_idx = min(i + version.hold_days, len(df) - 1)
                    exit_price = df['Close'].iloc[exit_idx]
                    exit_date = df.index[exit_idx]
                    exit_reason = 'time_stop'
                
                # Calculate return (7x leverage for options estimate)
                stock_return = (exit_price - entry_price) / entry_price
                option_return = stock_return * 7
                
                trades.append({
                    'entry_date': entry_date,
                    'exit_date': exit_date,
                    'entry_price': entry_price,
                    'exit_price': exit_price,
                    'return': option_return,
                    'exit_reason': exit_reason,
                    'rvol_at_entry': signal['rvol'],
                    'hold_days': (exit_date - entry_date).days
                })
        
        if not trades:
            return {'version': version.name, 'trades': 0, 'win_rate': 0}
        
        returns = [t['return'] for t in trades]
        winning = [r for r in returns if r > 0]
        
        win_rate = len(winning) / len(returns) * 100 if returns else 0
        avg_return = np.mean(returns) * 100
        profit_factor = abs(sum(winning)) / abs(sum(r for r in returns if r < 0)) if any(r < 0 for r in returns) else float('inf')
        
        return {
            'version': version.name,
            'trades': len(trades),
            'win_rate': round(win_rate, 1),
            'avg_return': round(avg_return, 2),
            'profit_factor': round(profit_factor, 2),
            'best_trade': round(max(returns) * 100, 1),
            'worst_trade': round(min(returns) * 100, 1),
            'avg_hold_days': round(np.mean([t['hold_days'] for t in trades]), 1),
            'exit_reasons': {
                'volume_spike': sum(1 for t in trades if t['exit_reason'] == 'volume_spike'),
                'sma_break': sum(1 for t in trades if t['exit_reason'] == 'sma_break'),
                'time_stop': sum(1 for t in trades if t['exit_reason'] == 'time_stop')
            }
        }
    
    def find_best_version(self, symbols: List[str]) -> pd.DataFrame:
        """Test all versions on multiple symbols and find best"""
        all_results = []
        
        print(f"Testing {len(self.versions)} pattern versions on {len(symbols)} symbols...")
        print()
        
        for version in self.versions:
            print(f"Testing {version.name}...")
            version_results = []
            
            for symbol in symbols:
                try:
                    result = self.backtest_version(symbol, version)
                    result['symbol'] = symbol
                    version_results.append(result)
                except Exception as e:
                    print(f"  Error on {symbol}: {e}")
                    continue
            
            if version_results:
                avg_win_rate = np.mean([r['win_rate'] for r in version_results])
                avg_return = np.mean([r['avg_return'] for r in version_results])
                total_trades = sum(r['trades'] for r in version_results)
                
                all_results.append({
                    'Version': version.name,
                    'Total_Trades': total_trades,
                    'Avg_Win_Rate': round(avg_win_rate, 1),
                    'Avg_Return': round(avg_return, 2),
                    'Symbols_Tested': len(version_results)
                })
        
        return pd.DataFrame(all_results)


def test_improved_pattern():
    """Test the improved pattern on multiple symbols"""
    print("="*70)
    print("🔧 IMPROVED LOW CONVICTION PATTERN TESTING")
    print("="*70)
    print()
    
    detector = ImprovedLowConvictionDetector()
    
    symbols = ['NOK', 'T', 'F', 'BAC', 'KMI', 'SOFI', 'PLTR', 'XOM']
    
    # Find best version
    results = detector.find_best_version(symbols)
    
    print()
    print("="*70)
    print("RESULTS SUMMARY")
    print("="*70)
    print(results.to_string(index=False))
    print()
    
    # Show best version
    best = results.loc[results['Avg_Win_Rate'].idxmax()]
    print(f"🏆 BEST VERSION: {best['Version']}")
    print(f"   Win Rate: {best['Avg_Win_Rate']}%")
    print(f"   Avg Return: {best['Avg_Return']}%")
    print(f"   Total Trades: {best['Total_Trades']}")
    print()
    
    # Detailed backtest on best symbol
    print("="*70)
    print("DETAILED BACKTEST: Best symbol with best version")
    print("="*70)
    
    # Find best symbol for best version
    best_version_name = best['Version']
    best_version = next(v for v in detector.versions if v.name == best_version_name)
    
    for symbol in symbols[:3]:
        result = detector.backtest_version(symbol, best_version)
        if result['trades'] > 0:
            print(f"\n{symbol}:")
            print(f"  Trades: {result['trades']}")
            print(f"  Win Rate: {result['win_rate']}%")
            print(f"  Avg Return: {result['avg_return']}%")
            print(f"  Exit reasons: {result['exit_reasons']}")
    
    return results


if __name__ == "__main__":
    test_improved_pattern()
