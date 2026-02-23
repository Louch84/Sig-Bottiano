#!/usr/bin/env python3
"""
$5 Scanner - Cheap Options Finder
Finds options under $5 per contract (0.05 or less per share)
Perfect for lottery ticket plays with massive upside potential
"""

import sys
sys.path.insert(0, '/Users/sigbotti/.openclaw/workspace')
sys.path.insert(0, '/Users/sigbotti/.openclaw/workspace/agents/options-trading')

import yfinance as yf
import pandas as pd
from datetime import datetime
from typing import List, Dict, Optional

class FiveDollarScanner:
    """
    Scanner for options under $5 per contract
    Finds lottery ticket plays with high ROI potential
    """
    
    def __init__(self):
        # Watchlist of stocks to scan
        self.watchlist = [
            # Meme/Momentum
            'AMC', 'GME', 'BB', 'BBBY',
            # EV/Growth
            'RIVN', 'LCID', 'SOFI', 'PLTR',
            # Value/Dividend
            'NOK', 'F', 'BAC', 'T',
            # Energy
            'KMI', 'XOM', 'CVX', 'OXY', 'MPC', 'VLO', 'PSX',
            # Biotech/Pharma
            'ABBV', 'BIIB', 'GILD', 'JNJ', 'LLY', 'MRK', 'PFE', 'REGN',
            # Recovery
            'AAL', 'CCL', 'NCLH', 'UBER'
        ]
        
        self.max_contract_cost = 5.00  # $5 or less
        self.max_dte = 14  # Weekly options only
    
    def scan_cheap_options(self) -> List[Dict]:
        """
        Scan all watchlist stocks for cheap options under $5
        """
        cheap_plays = []
        
        print('='*90)
        print('🔥 $5 SCANNER - CHEAP OPTIONS FINDER')
        print('='*90)
        print(f'Scanning for options under ${self.max_contract_cost} per contract...')
        print()
        
        for symbol in self.watchlist:
            try:
                play = self._analyze_symbol(symbol)
                if play:
                    cheap_plays.append(play)
                    print(f'✅ {symbol}: ${play["contract_cost"]:.2f}/contract')
            except Exception as e:
                continue
        
        # Sort by contract cost
        cheap_plays.sort(key=lambda x: x['contract_cost'])
        
        return cheap_plays
    
    def _analyze_symbol(self, symbol: str) -> Optional[Dict]:
        """Analyze a single symbol for cheap options"""
        ticker = yf.Ticker(symbol)
        expirations = ticker.options
        
        if not expirations:
            return None
        
        # Get weekly expiration
        today = datetime.now()
        weekly_exps = []
        
        for exp in expirations:
            exp_date = datetime.strptime(exp, '%Y-%m-%d')
            days_to_exp = (exp_date - today).days
            if 0 <= days_to_exp <= self.max_dte:
                weekly_exps.append((exp, days_to_exp))
        
        if not weekly_exps:
            return None
        
        weekly_exps.sort(key=lambda x: x[1])
        exp, dte = weekly_exps[0]
        
        # Get options chain
        chain = ticker.option_chain(exp)
        info = ticker.info
        current = info.get('currentPrice', 0)
        
        if current == 0:
            return None
        
        # Find cheap calls ($0.05 or less per share = $5 or less per contract)
        calls = chain.calls
        max_price_per_share = self.max_contract_cost / 100  # $0.05
        
        cheap_calls = calls[calls['lastPrice'] <= max_price_per_share]
        cheap_calls = cheap_calls[cheap_calls['lastPrice'] > 0]  # Must have price
        
        if cheap_calls.empty:
            return None
        
        # Get the best one (closest to ATM but OTM)
        cheap_calls['distance_to_price'] = cheap_calls['strike'] - current
        # Filter for OTM only (strike > current)
        otm_calls = cheap_calls[cheap_calls['strike'] > current]
        
        if otm_calls.empty:
            return None
        
        best = otm_calls.sort_values('strike').iloc[0]  # Closest OTM
        
        contract_cost = best['lastPrice'] * 100
        breakeven = best['strike'] + best['lastPrice']
        
        # Calculate scenarios
        distance_pct = ((best['strike'] - current) / current) * 100
        upside_to_breakeven = ((breakeven - current) / current) * 100
        
        # If stock moves 10%
        target_price = current * 1.10
        option_value_at_target = max(0, target_price - best['strike'])
        profit_at_target = (option_value_at_target - best['lastPrice']) * 100
        roi = (profit_at_target / contract_cost) * 100 if contract_cost > 0 else 0
        
        # If stock moves 20%
        target_20 = current * 1.20
        option_at_20 = max(0, target_20 - best['strike'])
        profit_at_20 = (option_at_20 - best['lastPrice']) * 100
        roi_20 = (profit_at_20 / contract_cost) * 100 if contract_cost > 0 else 0
        
        return {
            'symbol': symbol,
            'current': current,
            'strike': best['strike'],
            'price_per_share': best['lastPrice'],
            'contract_cost': contract_cost,
            'breakeven': breakeven,
            'dte': dte,
            'expiration': exp,
            'volume': int(best['volume']) if not pd.isna(best['volume']) else 0,
            'oi': int(best['openInterest']) if not pd.isna(best['openInterest']) else 0,
            'iv': best['impliedVolatility'] * 100 if best['impliedVolatility'] else 0,
            'distance_pct': distance_pct,
            'upside_to_breakeven': upside_to_breakeven,
            'profit_10pct': profit_at_target,
            'roi_10pct': roi,
            'profit_20pct': profit_at_20,
            'roi_20pct': roi_20
        }
    
    def print_results(self, plays: List[Dict]):
        """Pretty print the results"""
        if not plays:
            print('No cheap options found under $5.')
            return
        
        print()
        print('='*90)
        print(f'🎯 TOP {len(plays)} CHEAP OPTIONS PLAYS (Under $5/contract)')
        print('='*90)
        print()
        
        for i, play in enumerate(plays, 1):
            print(f'{i}. 📈 {play["symbol"]}')
            print(f'   Current: ${play["current"]:.2f} | Strike: ${play["strike"]:.2f} (+{play["distance_pct"]:.1f}% OTM)')
            print(f'   💰 Cost: ${play["price_per_share"]:.3f}/share = ${play["contract_cost"]:.2f}/contract')
            print(f'   📅 Expires: {play["expiration"]} ({play["dte"]} DTE)')
            print(f'   📊 Volume: {play["volume"]} | OI: {play["oi"]} | IV: {play["iv"]:.1f}%')
            print(f'   🎯 Breakeven: ${play["breakeven"]:.2f} (need {play["upside_to_breakeven"]:+.1f}%)')
            print()
            print(f'   📈 SCENARIOS:')
            print(f'      If stock +10%: Profit ${play["profit_10pct"]:.0f} ({play["roi_10pct"]:.0f}% ROI)')
            if play["roi_10pct"] > 1000:
                print(f'         🔥 10-BAGGER POTENTIAL!')
            print(f'      If stock +20%: Profit ${play["profit_20pct"]:.0f} ({play["roi_20pct"]:.0f}% ROI)')
            print()
        
        print('='*90)
        print('💡 STRATEGY:')
        print('   • These are lottery ticket plays - high risk, high reward')
        print('   • Risk 100% of small amount ($3-5) for potential 1000%+ gains')
        print('   • Only trade what you can afford to lose completely')
        print('   • Best for stocks with catalysts or momentum building')
        print('='*90)
    
    def run(self):
        """Run the full scan"""
        plays = self.scan_cheap_options()
        self.print_results(plays)
        return plays


if __name__ == "__main__":
    scanner = FiveDollarScanner()
    scanner.run()
