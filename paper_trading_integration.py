#!/usr/bin/env python3
"""
Paper Trading Integration
Connect scanner signals to Alpaca paper trading + backtesting
"""

import sys
sys.path.insert(0, '/Users/sigbotti/.openclaw/workspace')
sys.path.insert(0, '/Users/sigbotti/.openclaw/workspace/agents/options-trading')

from scanner_alert_integration import ScannerAlertBridge
from alpaca_paper_trader import AlpacaPaperTrader, get_paper_trader
from pattern_backtester import PatternBacktester, backtest_watchlist
from advanced_options_scanner import OptionsSignal
from typing import List, Dict
from datetime import datetime
import os

class PaperTradingIntegration:
    """
    Full integration: Scanner → Backtest → Paper Trade → Track Results
    """
    
    def __init__(self):
        self.bridge = ScannerAlertBridge()
        self.backtester = PatternBacktester()
        self.paper_trades: List[Dict] = []
        
        # Try to initialize Alpaca
        self.alpaca_available = self._check_alpaca()
    
    def _check_alpaca(self) -> bool:
        """Check if Alpaca credentials are available"""
        return bool(os.getenv('ALPACA_API_KEY') and os.getenv('ALPACA_SECRET_KEY'))
    
    def validate_signal(self, signal: OptionsSignal) -> Dict:
        """
        Full validation pipeline for a signal:
        1. Backtest the pattern on this symbol
        2. If pattern has edge, create paper trade
        3. Track for outcome analysis
        """
        symbol = signal.symbol
        strategy = signal.strategy
        
        validation = {
            'signal': signal,
            'symbol': symbol,
            'validated': False,
            'reasons': [],
            'backtest_result': None,
            'paper_trade': None,
            'recommendation': 'SKIP'
        }
        
        # Step 1: Backtest the pattern
        print(f"\n📊 Validating {symbol} {signal.direction} ({strategy})...")
        
        if 'low_conviction' in strategy.lower():
            backtest = self.backtester.backtest_low_conviction(symbol, period="1y")
        else:
            # For other strategies, use generic backtest
            backtest = {'error': f'No backtest for {strategy}'}
        
        # Step 2: Evaluate backtest results
        if 'result' in backtest:
            result = backtest['result']
            validation['backtest_result'] = result
            
            print(f"   Backtest: {result.total_signals} signals, {result.win_rate}% win rate")
            print(f"   Avg return: {result.avg_return}%, Profit factor: {result.profit_factor}")
            
            # Decision rules
            if result.win_rate >= 50 and result.profit_factor >= 1.5:
                validation['validated'] = True
                validation['recommendation'] = 'TRADE'
                validation['reasons'].append(f"Strong edge: {result.win_rate}% win rate")
            elif result.win_rate >= 40 and result.expectancy > 0:
                validation['validated'] = True
                validation['recommendation'] = 'TRADE_SMALL'
                validation['reasons'].append(f"Marginal edge: {result.win_rate}% win rate")
            else:
                validation['reasons'].append(f"No edge: {result.win_rate}% win rate, {result.profit_factor} PF")
        else:
            # No backtest available - be conservative
            validation['reasons'].append("No backtest data available")
            if signal.confidence >= 85:  # Only trade very high confidence without backtest
                validation['validated'] = True
                validation['recommendation'] = 'TRADE_SMALL'
        
        # Step 3: Create paper trade if validated
        if validation['validated'] and self.alpaca_available:
            try:
                trader = get_paper_trader()
                paper_result = trader.validate_signal_with_paper(signal)
                validation['paper_trade'] = paper_result
                print(f"   ✅ Paper trade created: {paper_result['option_symbol']}")
            except Exception as e:
                print(f"   ⚠️  Could not create paper trade: {e}")
        
        return validation
    
    def scan_and_validate(self, watchlist: List[str] = None) -> List[Dict]:
        """
        Run scanner and validate all signals
        """
        if watchlist is None:
            watchlist = ['NOK', 'T', 'BAC', 'F', 'SOFI', 'KMI', 'PLTR']
        
        print("="*70)
        print(f"🔍 SCAN + VALIDATE - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print("="*70)
        print(f"Scanning {len(watchlist)} symbols...")
        print()
        
        # Run scanner
        signals = self.bridge.scan_and_alert(watchlist)
        
        if not signals:
            print("❌ No signals found")
            return []
        
        print(f"\n📝 Validating {len(signals)} signals...")
        print()
        
        # Validate each signal
        validated_signals = []
        for signal in signals:
            if signal.confidence >= 60:  # Only validate decent signals
                validation = self.validate_signal(signal)
                validated_signals.append(validation)
                
                # Print summary
                rec = validation['recommendation']
                status = "✅" if rec.startswith('TRADE') else "❌"
                print(f"\n   {status} {signal.symbol} {signal.direction}: {rec}")
                for reason in validation['reasons']:
                    print(f"      → {reason}")
        
        # Summary
        print()
        print("="*70)
        print("VALIDATION SUMMARY")
        print("="*70)
        
        tradeable = [v for v in validated_signals if v['recommendation'].startswith('TRADE')]
        print(f"Total signals: {len(validated_signals)}")
        print(f"Tradeable: {len(tradeable)}")
        print(f"Skipped: {len(validated_signals) - len(tradeable)}")
        
        return validated_signals
    
    def get_trade_recommendations(self, validated_signals: List[Dict]) -> List[Dict]:
        """Get only the tradeable recommendations"""
        return [v for v in validated_signals if v['recommendation'].startswith('TRADE')]


# Convenience functions
def validate_and_trade(watchlist: List[str] = None):
    """Quick function to scan, validate, and paper trade"""
    integration = PaperTradingIntegration()
    return integration.scan_and_validate(watchlist)

def setup_alpaca_keys():
    """Interactive setup for Alpaca API keys"""
    print("="*70)
    print("📈 ALPACA PAPER TRADING SETUP")
    print("="*70)
    print()
    print("To use Alpaca paper trading:")
    print("1. Go to https://alpaca.markets")
    print("2. Sign up for free account")
    print("3. Enable 'Paper Trading'")
    print("4. Go to 'Your API Keys' and generate new keys")
    print()
    
    api_key = input("Enter your Alpaca API Key: ").strip()
    secret_key = input("Enter your Alpaca Secret Key: ").strip()
    
    if api_key and secret_key:
        # Save to .env file
        with open('.env', 'a') as f:
            f.write(f"\nALPACA_API_KEY={api_key}\n")
            f.write(f"ALPACA_SECRET_KEY={secret_key}\n")
        
        # Set for current session
        os.environ['ALPACA_API_KEY'] = api_key
        os.environ['ALPACA_SECRET_KEY'] = secret_key
        
        print("\n✅ Keys saved to .env file")
        print("Testing connection...")
        
        from alpaca_paper_trader import test_alpaca_connection
        if test_alpaca_connection():
            print("\n🎉 Alpaca paper trading is ready!")
        else:
            print("\n❌ Connection failed - check your keys")
    else:
        print("\n⏭️  Setup skipped")


# Demo
if __name__ == "__main__":
    print("="*70)
    print("🔗 PAPER TRADING INTEGRATION")
    print("="*70)
    print()
    
    # Check Alpaca status
    has_alpaca = bool(os.getenv('ALPACA_API_KEY'))
    
    if not has_alpaca:
        print("❌ Alpaca API keys not found")
        print()
        setup = input("Would you like to set up Alpaca now? (y/n): ").lower()
        if setup == 'y':
            setup_alpaca_keys()
        else:
            print("\nContinuing with backtesting only...")
            print("(Set ALPACA_API_KEY and ALPACA_SECRET_KEY for paper trading)")
    else:
        from alpaca_paper_trader import test_alpaca_connection
        if test_alpaca_connection():
            print("✅ Alpaca paper trading connected")
        else:
            print("⚠️  Alpaca keys found but connection failed")
    
    print()
    print("Usage:")
    print("  from paper_trading_integration import validate_and_trade")
    print("  results = validate_and_trade(['NOK', 'T', 'BAC'])")
    print()
    print("Or run full scan:")
    print("  python3 paper_trading_integration.py")
