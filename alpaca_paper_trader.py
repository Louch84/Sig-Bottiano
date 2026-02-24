#!/usr/bin/env python3
"""
Alpaca Paper Trading Integration
Test options strategies without risking real money
"""

import os
import sys
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import requests

# Alpaca API endpoints
ALPACA_PAPER_BASE = "https://paper-api.alpaca.markets"
ALPACA_DATA_BASE = "https://data.alpaca.markets"

@dataclass
class PaperTrade:
    """A paper trade record"""
    symbol: str
    side: str  # buy or sell
    qty: int
    entry_price: float
    exit_price: Optional[float]
    entry_time: str
    exit_time: Optional[str]
    pnl: Optional[float]
    status: str  # open, closed
    strategy: str
    notes: str

class AlpacaPaperTrader:
    """
    Paper trading integration with Alpaca
    Test strategies before going live
    """
    
    def __init__(self, api_key: str = None, secret_key: str = None):
        self.api_key = api_key or os.getenv('ALPACA_API_KEY')
        self.secret_key = secret_key or os.getenv('ALPACA_SECRET_KEY')
        
        if not self.api_key or not self.secret_key:
            raise ValueError("Alpaca API keys required. Set ALPACA_API_KEY and ALPACA_SECRET_KEY env vars.")
        
        self.headers = {
            'APCA-API-KEY-ID': self.api_key,
            'APCA-API-SECRET-KEY': self.secret_key
        }
        
        self.trade_history: List[PaperTrade] = []
        self.account_info = None
    
    def get_account(self) -> Dict:
        """Get paper trading account info"""
        url = f"{ALPACA_PAPER_BASE}/v2/account"
        response = requests.get(url, headers=self.headers, timeout=10)
        
        if response.status_code == 200:
            self.account_info = response.json()
            return self.account_info
        else:
            return {'error': response.text, 'status_code': response.status_code}
    
    def get_buying_power(self) -> float:
        """Get current buying power"""
        account = self.get_account()
        if 'buying_power' in account:
            return float(account['buying_power'])
        return 0.0
    
    def get_positions(self) -> List[Dict]:
        """Get current positions"""
        url = f"{ALPACA_PAPER_BASE}/v2/positions"
        response = requests.get(url, headers=self.headers, timeout=10)
        
        if response.status_code == 200:
            return response.json()
        return []
    
    def place_order(self, symbol: str, qty: int, side: str, 
                    order_type: str = 'market', limit_price: float = None) -> Dict:
        """
        Place a paper order
        
        Note: Alpaca paper trading supports stocks/ETFs, not options directly.
        For options, we'll simulate by tracking in our own system.
        """
        url = f"{ALPACA_PAPER_BASE}/v2/orders"
        
        payload = {
            'symbol': symbol,
            'qty': qty,
            'side': side,
            'type': order_type,
            'time_in_force': 'day'
        }
        
        if order_type == 'limit' and limit_price:
            payload['limit_price'] = limit_price
        
        response = requests.post(url, json=payload, headers=self.headers, timeout=10)
        return response.json() if response.status_code == 200 else {'error': response.text}
    
    def simulate_options_trade(self, underlying: str, option_symbol: str, 
                               quantity: int, entry_price: float, 
                               strategy: str, signal_confidence: float) -> PaperTrade:
        """
        Simulate an options trade (since Alpaca paper doesn't support options directly)
        We track it in our system and use stock position as proxy
        """
        # Create paper trade record
        trade = PaperTrade(
            symbol=option_symbol,
            side='buy',
            qty=quantity,
            entry_price=entry_price,
            exit_price=None,
            entry_time=datetime.now().isoformat(),
            exit_time=None,
            pnl=None,
            status='open',
            strategy=strategy,
            notes=f"Signal confidence: {signal_confidence}% | Underlying: {underlying}"
        )
        
        self.trade_history.append(trade)
        
        # Also place small stock position as proxy (optional)
        try:
            # Buy 1 share of underlying as proxy for tracking
            stock_order = self.place_order(underlying, 1, 'buy')
            print(f"   Proxy stock position: {underlying} (paper)")
        except Exception as e:
            print(f"   Note: Could not place proxy position: {e}")
        
        return trade
    
    def close_paper_trade(self, trade_index: int, exit_price: float) -> PaperTrade:
        """Close an open paper trade and calculate P&L"""
        if trade_index >= len(self.trade_history):
            raise ValueError("Invalid trade index")
        
        trade = self.trade_history[trade_index]
        
        if trade.status != 'open':
            raise ValueError("Trade already closed")
        
        # Calculate P&L
        cost_basis = trade.entry_price * trade.qty * 100  # Options are 100 shares
        exit_value = exit_price * trade.qty * 100
        pnl = exit_value - cost_basis
        
        # Update trade
        trade.exit_price = exit_price
        trade.exit_time = datetime.now().isoformat()
        trade.pnl = pnl
        trade.status = 'closed'
        
        return trade
    
    def get_performance_summary(self) -> Dict:
        """Get paper trading performance summary"""
        closed_trades = [t for t in self.trade_history if t.status == 'closed']
        open_trades = [t for t in self.trade_history if t.status == 'open']
        
        if not closed_trades:
            return {
                'total_trades': 0,
                'win_rate': 0,
                'total_pnl': 0,
                'avg_pnl': 0,
                'open_positions': len(open_trades)
            }
        
        total_pnl = sum(t.pnl for t in closed_trades)
        winning_trades = sum(1 for t in closed_trades if t.pnl > 0)
        win_rate = (winning_trades / len(closed_trades)) * 100
        
        return {
            'total_trades': len(closed_trades),
            'win_rate': round(win_rate, 2),
            'total_pnl': round(total_pnl, 2),
            'avg_pnl': round(total_pnl / len(closed_trades), 2),
            'open_positions': len(open_trades),
            'best_trade': max(t.pnl for t in closed_trades),
            'worst_trade': min(t.pnl for t in closed_trades)
        }
    
    def validate_signal_with_paper(self, signal) -> Dict:
        """
        Take a scanner signal and paper trade it
        Returns the paper trade details
        """
        from advanced_options_scanner import OptionsSignal
        
        if not isinstance(signal, OptionsSignal):
            return {'error': 'Invalid signal type'}
        
        # Build option symbol (simplified)
        # Format: Ticker + YYMMDD + C/P + Strike
        exp_date = signal.expiration.replace('-', '')[2:]  # YYMMDD
        option_type = 'C' if signal.direction == 'CALL' else 'P'
        strike = str(int(signal.suggested_strike * 1000)).zfill(8)  # 8 digits
        option_symbol = f"{signal.symbol}{exp_date}{option_type}{strike}"
        
        # Calculate position size (max $100 per trade for paper testing)
        max_cost = 100
        qty = max(1, int(max_cost / (signal.option_cost * 100)))
        
        # Simulate the trade
        trade = self.simulate_options_trade(
            underlying=signal.symbol,
            option_symbol=option_symbol,
            quantity=qty,
            entry_price=signal.option_cost,
            strategy=signal.strategy,
            signal_confidence=signal.confidence
        )
        
        return {
            'trade': trade,
            'option_symbol': option_symbol,
            'total_cost': signal.option_cost * qty * 100,
            'stop_loss': signal.stop_loss,
            'target': signal.target_price,
            'notes': f"Paper trade based on {signal.strategy} signal"
        }


# Convenience functions
trader = None

def get_paper_trader() -> AlpacaPaperTrader:
    """Get or create paper trader singleton"""
    global trader
    if trader is None:
        trader = AlpacaPaperTrader()
    return trader

def test_alpaca_connection() -> bool:
    """Test if Alpaca connection works"""
    try:
        trader = get_paper_trader()
        account = trader.get_account()
        if 'buying_power' in account:
            print(f"✅ Alpaca paper account connected")
            print(f"   Buying Power: ${float(account['buying_power']):,.2f}")
            print(f"   Account Status: {account.get('status', 'unknown')}")
            return True
        else:
            print(f"❌ Connection failed: {account.get('error', 'Unknown error')}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


# Demo
if __name__ == "__main__":
    print("="*70)
    print("📈 ALPACA PAPER TRADING")
    print("="*70)
    print()
    
    # Check for API keys
    api_key = os.getenv('ALPACA_API_KEY')
    secret_key = os.getenv('ALPACA_SECRET_KEY')
    
    if not api_key or not secret_key:
        print("❌ Alpaca API keys not found!")
        print()
        print("To get your API keys:")
        print("1. Go to https://alpaca.markets")
        print("2. Sign up for a free account")
        print("3. Go to 'Paper Trading' section")
        print("4. Generate API keys")
        print()
        print("Then set environment variables:")
        print("  export ALPACA_API_KEY='your_key_here'")
        print("  export ALPACA_SECRET_KEY='your_secret_here'")
        print()
        print("Or create a .env file with these variables")
        sys.exit(1)
    
    # Test connection
    if test_alpaca_connection():
        print()
        print("Paper trading is ready!")
        print()
        print("Usage in your code:")
        print("  from alpaca_paper_trader import get_paper_trader")
        print("  trader = get_paper_trader()")
        print("  result = trader.validate_signal_with_paper(signal)")
    else:
        print()
        print("Check your API keys and try again")
