#!/usr/bin/env python3
"""
Trade Tracker & Outcome Logger
Track actual trades from Robinhood (manual entry) or any broker
Learn from outcomes to improve signals
"""

import json
import os
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import pandas as pd

@dataclass
class TradeRecord:
    """A recorded trade"""
    # Trade ID
    trade_id: str
    timestamp: str
    
    # Symbol & Direction
    ticker: str
    direction: str  # CALL or PUT
    strategy: str   # low_conviction, gamma_squeeze, etc.
    
    # Entry
    entry_date: str
    entry_price: float
    strike: float
    expiration: str
    contracts: int
    entry_cost: float
    
    # Exit (filled later)
    exit_date: Optional[str] = None
    exit_price: Optional[float] = None
    exit_value: Optional[float] = None
    
    # Calculated
    pnl: Optional[float] = None
    pnl_percent: Optional[float] = None
    
    # Analysis
    signal_confidence: float = 0
    exit_reason: Optional[str] = None  # target_hit, stop_loss, time_decay, manual
    
    # Notes
    entry_notes: str = ""
    exit_notes: str = ""
    lessons: str = ""


class TradeTracker:
    """
    Track trades and learn from outcomes
    """
    
    def __init__(self, data_file: str = "trade_history.json"):
        self.data_file = data_file
        self.trades: List[TradeRecord] = []
        self.load_trades()
    
    def load_trades(self):
        """Load trade history from file"""
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r') as f:
                data = json.load(f)
                self.trades = [TradeRecord(**t) for t in data]
    
    def save_trades(self):
        """Save trade history to file"""
        data = [asdict(t) for t in self.trades]
        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def record_entry(self, ticker: str, direction: str, strategy: str,
                     strike: float, expiration: str, contracts: int,
                     entry_price: float, signal_confidence: float = 0,
                     notes: str = "") -> TradeRecord:
        """
        Record when you enter a trade
        """
        trade_id = f"{ticker}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        trade = TradeRecord(
            trade_id=trade_id,
            timestamp=datetime.now().isoformat(),
            ticker=ticker,
            direction=direction,
            strategy=strategy,
            entry_date=datetime.now().strftime('%Y-%m-%d'),
            entry_price=entry_price,
            strike=strike,
            expiration=expiration,
            contracts=contracts,
            entry_cost=entry_price * contracts * 100,  # 100 shares per contract
            signal_confidence=signal_confidence,
            entry_notes=notes
        )
        
        self.trades.append(trade)
        self.save_trades()
        
        print(f"✅ Trade recorded: {trade_id}")
        print(f"   {ticker} {direction} {contracts} contracts @ ${entry_price}")
        print(f"   Total cost: ${trade.entry_cost:.2f}")
        
        return trade
    
    def record_exit(self, trade_id: str, exit_price: float, 
                    exit_reason: str = "manual", notes: str = ""):
        """
        Record when you exit a trade
        """
        trade = self.get_trade(trade_id)
        if not trade:
            print(f"❌ Trade {trade_id} not found")
            return None
        
        trade.exit_date = datetime.now().strftime('%Y-%m-%d')
        trade.exit_price = exit_price
        trade.exit_value = exit_price * trade.contracts * 100
        trade.exit_reason = exit_reason
        trade.exit_notes = notes
        
        # Calculate P&L
        trade.pnl = trade.exit_value - trade.entry_cost
        trade.pnl_percent = (trade.pnl / trade.entry_cost) * 100
        
        self.save_trades()
        
        emoji = "🟢" if trade.pnl > 0 else "🔴"
        print(f"{emoji} Exit recorded: {trade_id}")
        print(f"   Sold @ ${exit_price} | P&L: ${trade.pnl:.2f} ({trade.pnl_percent:.1f}%)")
        
        return trade
    
    def get_trade(self, trade_id: str) -> Optional[TradeRecord]:
        """Get a specific trade by ID"""
        for trade in self.trades:
            if trade.trade_id == trade_id:
                return trade
        return None
    
    def get_open_trades(self) -> List[TradeRecord]:
        """Get all open trades"""
        return [t for t in self.trades if t.exit_date is None]
    
    def get_closed_trades(self) -> List[TradeRecord]:
        """Get all closed trades"""
        return [t for t in self.trades if t.exit_date is not None]
    
    def get_performance_summary(self) -> Dict:
        """Get overall performance stats"""
        closed = self.get_closed_trades()
        
        if not closed:
            return {
                'total_trades': 0,
                'open_trades': len(self.get_open_trades()),
                'win_rate': 0,
                'total_pnl': 0,
                'avg_trade_pnl': 0
            }
        
        winning = [t for t in closed if t.pnl > 0]
        losing = [t for t in closed if t.pnl <= 0]
        
        total_pnl = sum(t.pnl for t in closed)
        
        return {
            'total_trades': len(closed),
            'open_trades': len(self.get_open_trades()),
            'winning_trades': len(winning),
            'losing_trades': len(losing),
            'win_rate': round(len(winning) / len(closed) * 100, 1),
            'total_pnl': round(total_pnl, 2),
            'avg_trade_pnl': round(total_pnl / len(closed), 2),
            'avg_win': round(sum(t.pnl for t in winning) / len(winning), 2) if winning else 0,
            'avg_loss': round(sum(t.pnl for t in losing) / len(losing), 2) if losing else 0,
            'best_trade': round(max(t.pnl for t in closed), 2),
            'worst_trade': round(min(t.pnl for t in closed), 2)
        }
    
    def get_strategy_performance(self) -> pd.DataFrame:
        """Get performance breakdown by strategy"""
        closed = self.get_closed_trades()
        
        if not closed:
            return pd.DataFrame()
        
        strategies = {}
        for trade in closed:
            strat = trade.strategy
            if strat not in strategies:
                strategies[strat] = {'trades': [], 'wins': 0, 'total_pnl': 0}
            
            strategies[strat]['trades'].append(trade)
            if trade.pnl > 0:
                strategies[strat]['wins'] += 1
            strategies[strat]['total_pnl'] += trade.pnl
        
        rows = []
        for strat, data in strategies.items():
            rows.append({
                'Strategy': strat,
                'Trades': len(data['trades']),
                'Win_Rate': round(data['wins'] / len(data['trades']) * 100, 1),
                'Total_PnL': round(data['total_pnl'], 2),
                'Avg_PnL': round(data['total_pnl'] / len(data['trades']), 2)
            })
        
        return pd.DataFrame(rows).sort_values('Total_PnL', ascending=False)
    
    def print_portfolio(self):
        """Print current portfolio status"""
        open_trades = self.get_open_trades()
        summary = self.get_performance_summary()
        
        print("="*70)
        print("📊 PORTFOLIO STATUS")
        print("="*70)
        print()
        print(f"Open Positions: {len(open_trades)}")
        print(f"Closed Trades: {summary['total_trades']}")
        print(f"Win Rate: {summary['win_rate']}%")
        print(f"Total P&L: ${summary['total_pnl']:.2f}")
        print(f"Avg per Trade: ${summary['avg_trade_pnl']:.2f}")
        print()
        
        if open_trades:
            print("OPEN POSITIONS:")
            print("-"*70)
            for t in open_trades:
                print(f"  {t.ticker} {t.direction} {t.contracts} @ ${t.entry_price} (since {t.entry_date})")
            print()
        
        if summary['total_trades'] > 0:
            print("PERFORMANCE BY STRATEGY:")
            print("-"*70)
            print(self.get_strategy_performance().to_string(index=False))
            print()
        
        print("="*70)
    
    def export_to_csv(self, filename: str = "trade_history.csv"):
        """Export trades to CSV for analysis"""
        if not self.trades:
            print("No trades to export")
            return
        
        data = [asdict(t) for t in self.trades]
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False)
        print(f"✅ Exported {len(data)} trades to {filename}")


# Convenience functions
tracker = None

def get_tracker() -> TradeTracker:
    """Get or create tracker singleton"""
    global tracker
    if tracker is None:
        tracker = TradeTracker()
    return tracker

def enter_trade(ticker: str, direction: str, strategy: str,
                strike: float, expiration: str, contracts: int,
                entry_price: float, **kwargs):
    """Quick function to record entry"""
    t = get_tracker()
    return t.record_entry(ticker, direction, strategy, strike, expiration,
                          contracts, entry_price, **kwargs)

def exit_trade(trade_id: str, exit_price: float, **kwargs):
    """Quick function to record exit"""
    t = get_tracker()
    return t.record_exit(trade_id, exit_price, **kwargs)

def portfolio():
    """Show portfolio status"""
    get_tracker().print_portfolio()


# Demo
if __name__ == "__main__":
    print("="*70)
    print("📈 TRADE TRACKER")
    print("="*70)
    print()
    print("Usage:")
    print("  from trade_tracker import enter_trade, exit_trade, portfolio")
    print()
    print("  # When you buy")
    print("  trade = enter_trade(")
    print("      ticker='NOK', direction='CALL', strategy='low_conviction',")
    print("      strike=8.0, expiration='2025-03-07', contracts=2,")
    print("      entry_price=0.11, signal_confidence=85)")
    print()
    print("  # When you sell")
    print("  exit_trade(trade.trade_id, exit_price=0.25, exit_reason='target_hit')")
    print()
    print("  # Check status")
    print("  portfolio()")
    print()
    print("="*70)
    
    # Show current status if trades exist
    portfolio()
