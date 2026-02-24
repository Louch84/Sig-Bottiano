#!/usr/bin/env python3
"""
Pattern Backtester
Backtest trading patterns on historical data to validate signal quality
"""

import sys
sys.path.insert(0, '/Users/sigbotti/.openclaw/workspace')
sys.path.insert(0, '/Users/sigbotti/.openclaw/workspace/agents/options-trading')

import yfinance as yf
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass

@dataclass
class BacktestResult:
    """Results of a backtest"""
    pattern_name: str
    total_signals: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    avg_return: float
    max_drawdown: float
    sharpe_ratio: float
    profit_factor: float
    avg_trade_duration: int  # days
    best_trade: float
    worst_trade: float
    expectancy: float

class PatternBacktester:
    """
    Backtest trading patterns on historical stock data
    """
    
    def __init__(self, initial_capital: float = 10000.0):
        self.initial_capital = initial_capital
        self.results: List[BacktestResult] = []
    
    def fetch_historical_data(self, symbol: str, period: str = "1y") -> pd.DataFrame:
        """Fetch historical price data"""
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=period)
        return df
    
    def detect_low_conviction_pattern(self, df: pd.DataFrame, 
                                      lookback: int = 20,
                                      rvol_threshold: float = 0.3,
                                      price_change_threshold: float = 0.005) -> pd.DataFrame:
        """
        Detect low conviction pattern on historical data
        Pattern: Price up on low volume, near highs, above SMA
        """
        df = df.copy()
        
        # Calculate indicators
        df['SMA20'] = df['Close'].rolling(window=lookback).mean()
        df['Volume_SMA20'] = df['Volume'].rolling(window=lookback).mean()
        df['RVOL'] = df['Volume'] / df['Volume_SMA20']
        df['Price_Change'] = df['Close'].pct_change()
        df['High_20d'] = df['Close'].rolling(window=lookback).max()
        df['Near_Highs'] = df['Close'] >= (df['High_20d'] * 0.97)  # Within 3%
        df['Above_SMA'] = df['Close'] > df['SMA20']
        
        # Detect pattern
        df['Low_Conviction'] = (
            (df['RVOL'] < rvol_threshold) &
            (df['Price_Change'] > price_change_threshold) &
            df['Above_SMA'] &
            df['Near_Highs']
        )
        
        return df
    
    def backtest_low_conviction(self, symbol: str, 
                                hold_days: int = 5,
                                period: str = "2y") -> Dict:
        """
        Backtest low conviction pattern
        Buy when pattern triggers, hold for N days
        """
        print(f"📊 Backtesting Low Conviction Pattern on {symbol}...")
        
        df = self.fetch_historical_data(symbol, period)
        df = self.detect_low_conviction_pattern(df)
        
        trades = []
        capital = self.initial_capital
        
        for i in range(20, len(df) - hold_days):
            if df['Low_Conviction'].iloc[i]:
                # Pattern triggered - simulate entry
                entry_price = df['Close'].iloc[i]
                entry_date = df.index[i]
                
                # Hold for specified days
                if i + hold_days < len(df):
                    exit_price = df['Close'].iloc[i + hold_days]
                    exit_date = df.index[i + hold_days]
                    
                    # Calculate return
                    stock_return = (exit_price - entry_price) / entry_price
                    
                    # Options multiplier (rough estimate: 5-10x stock move)
                    option_return = stock_return * 7  # Assumes 7x leverage
                    
                    trades.append({
                        'entry_date': entry_date,
                        'exit_date': exit_date,
                        'entry_price': entry_price,
                        'exit_price': exit_price,
                        'stock_return': stock_return,
                        'option_return': option_return,
                        'days_held': hold_days,
                        'rvol': df['RVOL'].iloc[i]
                    })
        
        if not trades:
            return {'error': 'No pattern signals found in period', 'symbol': symbol}
        
        # Calculate metrics
        returns = [t['option_return'] for t in trades]
        winning = [r for r in returns if r > 0]
        losing = [r for r in returns if r <= 0]
        
        win_rate = len(winning) / len(returns) * 100 if returns else 0
        avg_return = np.mean(returns) * 100 if returns else 0
        best_trade = max(returns) * 100 if returns else 0
        worst_trade = min(returns) * 100 if returns else 0
        
        # Calculate equity curve
        equity = [self.initial_capital]
        for ret in returns:
            equity.append(equity[-1] * (1 + ret))
        
        # Max drawdown
        peak = equity[0]
        max_dd = 0
        for val in equity:
            if val > peak:
                peak = val
            dd = (peak - val) / peak
            if dd > max_dd:
                max_dd = dd
        
        # Profit factor
        gross_profit = sum(r for r in returns if r > 0)
        gross_loss = abs(sum(r for r in returns if r < 0))
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')
        
        # Expectancy
        expectancy = (win_rate/100 * avg_return) - ((100-win_rate)/100 * abs(np.mean(losing)*100 if losing else 0))
        
        result = BacktestResult(
            pattern_name="Low Conviction Pattern",
            total_signals=len(trades),
            winning_trades=len(winning),
            losing_trades=len(losing),
            win_rate=round(win_rate, 2),
            avg_return=round(avg_return, 2),
            max_drawdown=round(max_dd * 100, 2),
            sharpe_ratio=round(np.mean(returns) / np.std(returns) if np.std(returns) > 0 else 0, 2),
            profit_factor=round(profit_factor, 2),
            avg_trade_duration=hold_days,
            best_trade=round(best_trade, 2),
            worst_trade=round(worst_trade, 2),
            expectancy=round(expectancy, 2)
        )
        
        return {
            'result': result,
            'trades': trades,
            'equity_curve': equity,
            'symbol': symbol
        }
    
    def backtest_multiple_symbols(self, symbols: List[str], 
                                   pattern: str = "low_conviction") -> pd.DataFrame:
        """Backtest pattern on multiple symbols"""
        results = []
        
        for symbol in symbols:
            try:
                if pattern == "low_conviction":
                    backtest = self.backtest_low_conviction(symbol)
                    if 'result' in backtest:
                        r = backtest['result']
                        results.append({
                            'Symbol': symbol,
                            'Signals': r.total_signals,
                            'Win Rate %': r.win_rate,
                            'Avg Return %': r.avg_return,
                            'Best Trade %': r.best_trade,
                            'Worst Trade %': r.worst_trade,
                            'Max DD %': r.max_drawdown,
                            'Profit Factor': r.profit_factor,
                            'Expectancy': r.expectancy
                        })
            except Exception as e:
                print(f"   ⚠️  Error on {symbol}: {str(e)[:50]}")
                continue
        
        return pd.DataFrame(results)
    
    def print_backtest_summary(self, backtest_result: Dict):
        """Print formatted backtest results"""
        if 'error' in backtest_result:
            print(f"❌ {backtest_result['error']}")
            return
        
        r = backtest_result['result']
        
        print()
        print("="*70)
        print(f"📊 BACKTEST RESULTS: {r.pattern_name}")
        print(f"Symbol: {backtest_result['symbol']}")
        print("="*70)
        print()
        print(f"Total Signals:     {r.total_signals}")
        print(f"Winning Trades:    {r.winning_trades}")
        print(f"Losing Trades:     {r.losing_trades}")
        print(f"Win Rate:          {r.win_rate}%")
        print()
        print(f"Average Return:    {r.avg_return}%")
        print(f"Best Trade:        +{r.best_trade}%")
        print(f"Worst Trade:       {r.worst_trade}%")
        print(f"Max Drawdown:      {r.max_drawdown}%")
        print()
        print(f"Profit Factor:     {r.profit_factor}")
        print(f"Expectancy:        {r.expectancy}")
        print(f"Sharpe Ratio:      {r.sharpe_ratio}")
        print()
        print("="*70)
        
        if r.win_rate > 50 and r.profit_factor > 1.5:
            print("✅ Pattern shows EDGE - worth trading")
        elif r.win_rate > 40 and r.expectancy > 0:
            print("⚠️  Pattern shows marginal edge - trade with caution")
        else:
            print("❌ Pattern shows NO EDGE - don't trade this")
        print("="*70)


# Convenience functions
def backtest_pattern(symbol: str, pattern: str = "low_conviction"):
    """Quick backtest function"""
    bt = PatternBacktester()
    result = bt.backtest_low_conviction(symbol)
    bt.print_backtest_summary(result)
    return result

def backtest_watchlist(symbols: List[str] = None):
    """Backtest on multiple symbols"""
    if symbols is None:
        symbols = ['NOK', 'T', 'BAC', 'F', 'SOFI', 'KMI']
    
    print("="*70)
    print(f"📊 BACKTESTING: Low Conviction Pattern")
    print(f"Symbols: {', '.join(symbols)}")
    print("="*70)
    print()
    
    bt = PatternBacktester()
    results_df = bt.backtest_multiple_symbols(symbols)
    
    print(results_df.to_string(index=False))
    print()
    
    # Summary stats
    if not results_df.empty:
        print(f"Average Win Rate: {results_df['Win Rate %'].mean():.1f}%")
        print(f"Average Return: {results_df['Avg Return %'].mean():.1f}%")
        print(f"Symbols with >50% win rate: {(results_df['Win Rate %'] > 50).sum()}/{len(results_df)}")
    
    return results_df


# Demo
if __name__ == "__main__":
    print("="*70)
    print("📈 PATTERN BACKTESTER")
    print("="*70)
    print()
    
    # Single symbol test
    print("Testing Low Conviction Pattern on NOK...")
    result = backtest_pattern('NOK')
    print()
    
    # Multi-symbol test (comment out for faster testing)
    print("Testing on multiple symbols...")
    results = backtest_watchlist(['NOK', 'T', 'F'])
