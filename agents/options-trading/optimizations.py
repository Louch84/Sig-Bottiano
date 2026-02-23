"""
Optimization Modules
Kelly sizing, backtesting, and advanced SMC
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta

# ============================================
# 1. KELLY CRITERION POSITION SIZING
# ============================================

class KellyPositionSizer:
    """
    Kelly Criterion for optimal position sizing.
    
    Formula: f* = (bp - q) / b
    Where:
    - b = average win / average loss (odds)
    - p = win probability
    - q = 1 - p (loss probability)
    - f* = optimal fraction of account to risk
    """
    
    def __init__(self, account_value: float = 10000, kelly_fraction: float = 0.25):
        """
        Args:
            account_value: Total account value
            kelly_fraction: Use half/quarter Kelly (0.25-0.5 recommended)
        """
        self.account_value = account_value
        self.kelly_fraction = kelly_fraction
        self.max_risk_per_trade = 0.05  # Max 5% per trade
    
    def calculate_position_size(
        self,
        win_probability: float,
        avg_win_pct: float,
        avg_loss_pct: float,
        option_price: float,
        contract_multiplier: int = 100
    ) -> Dict:
        """
        Calculate optimal position size using Kelly Criterion
        
        Returns:
            {
                'kelly_pct': Optimal Kelly percentage,
                'recommended_pct': Adjusted for safety,
                'max_contracts': Number of contracts to buy,
                'risk_amount': Dollar amount at risk,
                'confidence': Signal quality (0-1)
            }
        """
        if avg_loss_pct <= 0:
            avg_loss_pct = 0.01  # Prevent division by zero
        
        # Calculate odds (b)
        b = avg_win_pct / avg_loss_pct
        
        # Kelly formula: f* = (bp - q) / b
        q = 1 - win_probability
        kelly_raw = (b * win_probability - q) / b
        
        # Adjust Kelly (half/quarter Kelly for safety)
        kelly_adjusted = kelly_raw * self.kelly_fraction
        
        # Cap at max risk per trade
        recommended_pct = min(abs(kelly_adjusted), self.max_risk_per_trade)
        
        # Calculate contracts
        risk_amount = self.account_value * recommended_pct
        max_contracts = int(risk_amount / (option_price * contract_multiplier))
        max_contracts = max(1, min(max_contracts, 10))  # 1-10 contracts
        
        return {
            'kelly_raw': kelly_raw,
            'kelly_pct': kelly_raw * 100,
            'recommended_pct': recommended_pct * 100,
            'max_contracts': max_contracts,
            'risk_amount': risk_amount,
            'confidence': win_probability
        }
    
    def size_from_signal(self, signal_confidence: float, risk_reward: float, option_price: float) -> Dict:
        """
        Quick sizing from signal parameters
        
        Args:
            signal_confidence: 0.0-1.0 (from your scanner)
            risk_reward: Risk:Reward ratio (e.g., 4.0 for 1:4)
            option_price: Current option price
        """
        # Estimate win probability from confidence and R:R
        # Higher R:R means we can win less often and still profit
        # Formula: p = 1 / (1 + b) where b = R:R
        breakeven_win_rate = 1 / (1 + risk_reward)
        
        # Adjust for signal confidence
        win_probability = breakeven_win_rate + (signal_confidence * (1 - breakeven_win_rate))
        win_probability = min(0.95, win_probability)  # Cap at 95%
        
        # Assume 3:1 avg win:loss ratio based on R:R
        avg_win = risk_reward * 0.75  # Slightly less than max
        avg_loss = 1.0
        
        return self.calculate_position_size(
            win_probability=win_probability,
            avg_win_pct=avg_win,
            avg_loss_pct=avg_loss,
            option_price=option_price
        )


# ============================================
# 2. CORRELATION FILTER
# ============================================

class CorrelationFilter:
    """
    Filter out highly correlated stocks to reduce portfolio risk.
    Prevents "doubling down" on the same move.
    """
    
    def __init__(self, max_correlation: float = 0.7):
        """
        Args:
            max_correlation: Don't trade stocks with correlation > this
        """
        self.max_correlation = max_correlation
        self.price_history = {}
    
    def update_price_history(self, symbol: str, price: float):
        """Store price for correlation calculation"""
        if symbol not in self.price_history:
            self.price_history[symbol] = []
        self.price_history[symbol].append(price)
        # Keep last 30 days
        self.price_history[symbol] = self.price_history[symbol][-30:]
    
    def get_correlation(self, symbol1: str, symbol2: str) -> float:
        """Calculate correlation between two stocks"""
        if symbol1 not in self.price_history or symbol2 not in self.price_history:
            return 0.0
        
        prices1 = self.price_history[symbol1]
        prices2 = self.price_history[symbol2]
        
        # Need at least 10 data points
        if len(prices1) < 10 or len(prices2) < 10:
            return 0.0
        
        # Calculate returns
        returns1 = np.diff(prices1) / prices1[:-1]
        returns2 = np.diff(prices2) / prices2[:-1]
        
        # Use minimum length
        min_len = min(len(returns1), len(returns2))
        returns1 = returns1[-min_len:]
        returns2 = returns2[-min_len:]
        
        if len(returns1) < 5:
            return 0.0
        
        correlation = np.corrcoef(returns1, returns2)[0, 1]
        return abs(correlation) if not np.isnan(correlation) else 0.0
    
    def filter_correlated_signals(self, signals: List[Dict]) -> List[Dict]:
        """
        Filter out highly correlated signals.
        Keeps the highest-scoring signal from each correlated group.
        """
        if not signals:
            return []
        
        # Sort by move potential (highest first)
        sorted_signals = sorted(signals, key=lambda x: x.get('move_potential_score', 0), reverse=True)
        
        filtered = []
        for signal in sorted_signals:
            symbol = signal.get('symbol', '')
            
            # Check correlation with already selected signals
            is_correlated = False
            for selected in filtered:
                corr = self.get_correlation(symbol, selected.get('symbol', ''))
                if corr > self.max_correlation:
                    is_correlated = True
                    break
            
            if not is_correlated:
                filtered.append(signal)
        
        return filtered


# ============================================
# 3. ADVANCED SMC DETECTION
# ============================================

class AdvancedSMCDetector:
    """
    Improved Smart Money Concepts detection.
    Based on research from GitHub repos.
    """
    
    def __init__(self):
        self.lookback = 20
    
    def detect_order_blocks(self, df: pd.DataFrame) -> List[Dict]:
        """
        Detect institutional order blocks.
        
        Bullish OB: Bearish candle followed by 2+ strong bullish candles
        Bearish OB: Bullish candle followed by 2+ strong bearish candles
        """
        if len(df) < 5:
            return []
        
        obs = []
        
        for i in range(len(df) - 3):
            # Current and next candles
            c1 = df.iloc[i]   # Potential OB candle
            c2 = df.iloc[i+1] # First reaction
            c3 = df.iloc[i+2] # Second reaction
            
            # Bullish Order Block
            if (c1['Close'] < c1['Open'] and  # Bearish candle
                c2['Close'] > c2['Open'] and  # Bullish
                c3['Close'] > c3['Open'] and  # Bullish
                c2['Close'] > c1['High'] and  # Strong follow-through
                c3['Close'] > c2['High']):
                
                obs.append({
                    'type': 'bullish_ob',
                    'price': c1['Low'],
                    'high': c1['High'],
                    'index': i,
                    'strength': (c3['Close'] - c1['Low']) / c1['Low'] * 100
                })
            
            # Bearish Order Block
            elif (c1['Close'] > c1['Open'] and  # Bullish candle
                  c2['Close'] < c2['Open'] and  # Bearish
                  c3['Close'] < c3['Open'] and  # Bearish
                  c2['Close'] < c1['Low'] and   # Strong follow-through
                  c3['Close'] < c2['Low']):
                
                obs.append({
                    'type': 'bearish_ob',
                    'price': c1['High'],
                    'low': c1['Low'],
                    'index': i,
                    'strength': (c1['High'] - c3['Close']) / c1['High'] * 100
                })
        
        return obs
    
    def detect_fvg(self, df: pd.DataFrame) -> List[Dict]:
        """
        Detect Fair Value Gaps (imbalances).
        Price often returns to fill these gaps.
        """
        if len(df) < 3:
            return []
        
        fvgs = []
        
        for i in range(1, len(df) - 1):
            prev = df.iloc[i-1]
            curr = df.iloc[i]
            
            # Bullish FVG: Current low > Previous high
            if curr['Low'] > prev['High']:
                gap_size = (curr['Low'] - prev['High']) / prev['High'] * 100
                if gap_size > 0.5:  # Significant gap
                    fvgs.append({
                        'type': 'bullish_fvg',
                        'top': curr['Low'],
                        'bottom': prev['High'],
                        'size': gap_size,
                        'index': i
                    })
            
            # Bearish FVG: Current high < Previous low
            elif curr['High'] < prev['Low']:
                gap_size = (prev['Low'] - curr['High']) / prev['Low'] * 100
                if gap_size > 0.5:
                    fvgs.append({
                        'type': 'bearish_fvg',
                        'top': prev['Low'],
                        'bottom': curr['High'],
                        'size': gap_size,
                        'index': i
                    })
        
        return fvgs
    
    def detect_liquidity_sweeps(self, df: pd.DataFrame) -> List[Dict]:
        """
        Detect liquidity sweeps (stop hunts).
        Wick beyond swing point then close back inside.
        """
        if len(df) < 10:
            return []
        
        sweeps = []
        
        # Find swing highs/lows
        for i in range(5, len(df) - 5):
            current = df.iloc[i]
            
            # Check if this is a swing high
            is_swing_high = all(
                current['High'] >= df.iloc[j]['High']
                for j in range(i-3, i+3) if j != i
            )
            
            # Check if this is a swing low
            is_swing_low = all(
                current['Low'] <= df.iloc[j]['Low']
                for j in range(i-3, i+3) if j != i
            )
            
            # Check next candles for sweep
            if is_swing_high:
                for j in range(i+1, min(i+4, len(df))):
                    candle = df.iloc[j]
                    # Wick above swing high, close below
                    if (candle['High'] > current['High'] and 
                        candle['Close'] < current['High']):
                        sweeps.append({
                            'type': 'bullish_sweep',
                            'level': current['High'],
                            'wick': candle['High'],
                            'close': candle['Close'],
                            'index': j
                        })
            
            if is_swing_low:
                for j in range(i+1, min(i+4, len(df))):
                    candle = df.iloc[j]
                    # Wick below swing low, close above
                    if (candle['Low'] < current['Low'] and 
                        candle['Close'] > current['Low']):
                        sweeps.append({
                            'type': 'bearish_sweep',
                            'level': current['Low'],
                            'wick': candle['Low'],
                            'close': candle['Close'],
                            'index': j
                        })
        
        return sweeps
    
    def analyze(self, df: pd.DataFrame) -> Dict:
        """Run all SMC analyses"""
        obs = self.detect_order_blocks(df)
        fvgs = self.detect_fvg(df)
        sweeps = self.detect_liquidity_sweeps(df)
        
        # Calculate SMC score
        score = 0
        signals = []
        
        if obs:
            score += min(20, len(obs) * 10)
            signals.extend([f"{'🟢' if ob['type'] == 'bullish_ob' else '🔴'} {ob['type'].replace('_', ' ').title()} @ ${ob['price']:.2f}" for ob in obs[-2:]])
        
        if fvgs:
            score += min(15, len(fvgs) * 5)
            signals.extend([f"📈 FVG {fvg['size']:.1f}%" for fvg in fvgs[-2:]])
        
        if sweeps:
            score += min(15, len(sweeps) * 5)
            signals.extend([f"💨 {sweep['type'].replace('_', ' ').title()}" for sweep in sweeps[-2:]])
        
        return {
            'score': score,
            'order_blocks': obs,
            'fvgs': fvgs,
            'sweeps': sweeps,
            'signals': signals
        }


# ============================================
# 4. SIMPLE BACKTESTER
# ============================================

class SimpleBacktester:
    """
    Lightweight backtester for validating signals.
    Tests signals on historical data.
    """
    
    def __init__(self, initial_cash: float = 10000):
        self.initial_cash = initial_cash
        self.results = []
    
    def backtest_signal(
        self,
        symbol: str,
        signal_date: datetime,
        direction: str,
        entry_price: float,
        stop_price: float,
        target_price: float,
        price_history: List[float],
        max_days: int = 7
    ) -> Dict:
        """
        Simulate a single trade.
        
        Returns:
            {
                'pnl': Profit/loss amount,
                'pnl_pct': P/L percentage,
                'exit_price': Price exited at,
                'exit_reason': 'stop', 'target', or 'timeout',
                'days_held': Days in trade
            }
        """
        if not price_history or len(price_history) < 2:
            return {'error': 'Insufficient price data'}
        
        # Find entry index
        entry_idx = 0
        
        # Simulate forward
        for i in range(entry_idx + 1, min(entry_idx + max_days + 1, len(price_history))):
            current_price = price_history[i]
            
            if direction == 'CALL':
                # Check stop loss
                if current_price <= stop_price:
                    return {
                        'pnl': stop_price - entry_price,
                        'pnl_pct': (stop_price - entry_price) / entry_price * 100,
                        'exit_price': stop_price,
                        'exit_reason': 'stop',
                        'days_held': i - entry_idx,
                        'result': 'loss'
                    }
                # Check target
                if current_price >= target_price:
                    return {
                        'pnl': target_price - entry_price,
                        'pnl_pct': (target_price - entry_price) / entry_price * 100,
                        'exit_price': target_price,
                        'exit_reason': 'target',
                        'days_held': i - entry_idx,
                        'result': 'win'
                    }
            
            else:  # PUT
                # Check stop loss (price went up)
                if current_price >= stop_price:
                    return {
                        'pnl': entry_price - stop_price,
                        'pnl_pct': (entry_price - stop_price) / entry_price * 100,
                        'exit_price': stop_price,
                        'exit_reason': 'stop',
                        'days_held': i - entry_idx,
                        'result': 'loss'
                    }
                # Check target (price went down)
                if current_price <= target_price:
                    return {
                        'pnl': entry_price - target_price,
                        'pnl_pct': (entry_price - target_price) / entry_price * 100,
                        'exit_price': target_price,
                        'exit_reason': 'target',
                        'days_held': i - entry_idx,
                        'result': 'win'
                    }
        
        # Timeout - exit at last price
        final_price = price_history[-1]
        pnl = final_price - entry_price if direction == 'CALL' else entry_price - final_price
        
        return {
            'pnl': pnl,
            'pnl_pct': pnl / entry_price * 100,
            'exit_price': final_price,
            'exit_reason': 'timeout',
            'days_held': len(price_history) - entry_idx - 1,
            'result': 'win' if pnl > 0 else 'loss'
        }
    
    def calculate_stats(self, results: List[Dict]) -> Dict:
        """Calculate performance statistics"""
        if not results:
            return {}
        
        wins = sum(1 for r in results if r.get('result') == 'win')
        losses = len(results) - wins
        win_rate = wins / len(results) if results else 0
        
        pnls = [r.get('pnl_pct', 0) for r in results]
        avg_pnl = np.mean(pnls) if pnls else 0
        
        winning_trades = [p for p in pnls if p > 0]
        losing_trades = [p for p in pnls if p < 0]
        
        avg_win = np.mean(winning_trades) if winning_trades else 0
        avg_loss = np.mean(losing_trades) if losing_trades else 0
        
        # Profit factor
        gross_profit = sum(winning_trades)
        gross_loss = abs(sum(losing_trades))
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')
        
        # Expectancy
        expectancy = (win_rate * avg_win) - ((1 - win_rate) * abs(avg_loss))
        
        return {
            'total_trades': len(results),
            'wins': wins,
            'losses': losses,
            'win_rate': win_rate,
            'avg_pnl_pct': avg_pnl,
            'avg_win_pct': avg_win,
            'avg_loss_pct': avg_loss,
            'profit_factor': profit_factor,
            'expectancy': expectancy,
            'total_return_pct': sum(pnls)
        }


# ============================================
# 5. MARKET REGIME DETECTOR
# ============================================

class MarketRegimeDetector:
    """
    Detect market regime (bull/bear/sideways) based on VIX and trend.
    """
    
    def __init__(self):
        self.regimes = {
            'CREEP': {'vix_range': (0, 15), 'action': 'SELL_PREMIUM'},
            'NORMAL': {'vix_range': (15, 25), 'action': 'DIRECTIONAL'},
            'ELEVATED': {'vix_range': (25, 35), 'action': 'REDUCE_SIZE'},
            'CHAOS': {'vix_range': (35, 999), 'action': 'DAY_TRADE_ONLY'}
        }
    
    def detect_regime(self, vix: float, spy_trend: str = 'neutral') -> Dict:
        """
        Detect current market regime.
        
        Args:
            vix: Current VIX level
            spy_trend: SPY trend (bullish/bearish/neutral)
        """
        for regime, params in self.regimes.items():
            if params['vix_range'][0] <= vix < params['vix_range'][1]:
                return {
                    'regime': regime,
                    'vix': vix,
                    'action': params['action'],
                    'spy_trend': spy_trend,
                    'recommendation': self._get_recommendation(regime, spy_trend)
                }
        
        return {'regime': 'UNKNOWN', 'vix': vix, 'action': 'CAUTION'}
    
    def _get_recommendation(self, regime: str, trend: str) -> str:
        """Get strategy recommendation"""
        recommendations = {
            'CREEP': {
                'bullish': 'Iron Condors, Covered Calls',
                'bearish': 'Cash Secured Puts',
                'neutral': 'Iron Condors'
            },
            'NORMAL': {
                'bullish': 'Long Calls, Debit Spreads',
                'bearish': 'Long Puts, Credit Spreads',
                'neutral': 'Calendar Spreads'
            },
            'ELEVATED': {
                'bullish': 'Reduce size, wide stops',
                'bearish': 'Reduce size, wide stops',
                'neutral': 'Wait for VIX crush'
            },
            'CHAOS': {
                'bullish': '0DTE only, small size',
                'bearish': '0DTE only, small size',
                'neutral': 'Stay in cash'
            }
        }
        
        return recommendations.get(regime, {}).get(trend, 'Proceed with caution')


# Export all classes
__all__ = [
    'KellyPositionSizer',
    'CorrelationFilter',
    'AdvancedSMCDetector',
    'SimpleBacktester',
    'MarketRegimeDetector'
]
