#!/usr/bin/env python3
"""
Advanced Options Scanner
Integrates: flow, unusual activity, catalysts, news, biotech phases, momentum, 
analyst ratings, gap patterns, and options chain filtering
"""

import sys
sys.path.insert(0, '/Users/sigbotti/.openclaw/workspace')
sys.path.insert(0, '/Users/sigbotti/.openclaw/workspace/agents/options-trading')

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

@dataclass
class OptionsSignal:
    """Complete options trading signal"""
    symbol: str
    strategy: str  # 'momentum', 'catalyst', 'gap_fill', 'biotech', 'flow'
    direction: str  # 'CALL' or 'PUT'
    confidence: float
    
    # Price data
    current_price: float
    entry_price: float
    target_price: float
    stop_loss: float
    
    # Options specific
    suggested_strike: float
    option_cost: float
    expiration: str
    days_to_expiration: int
    
    # Analysis
    catalyst: Optional[str]
    news_sentiment: str
    analyst_rating: str
    analyst_target: float
    phase3_drug: Optional[str]
    
    # Technical
    gap_status: str
    momentum_score: float
    volume_spike: bool
    unusual_options_activity: bool
    
    # Risk
    max_loss: float
    max_gain: float
    risk_reward: float


class NewsAnalyzer:
    """Fetch and analyze news sentiment"""
    
    def __init__(self):
        self.news_cache = {}
        
    def get_news(self, symbol: str) -> List[Dict]:
        """Fetch recent news for symbol"""
        try:
            ticker = yf.Ticker(symbol)
            news = ticker.news
            return news if news else []
        except:
            return []
    
    def analyze_sentiment(self, news_items: List[Dict]) -> str:
        """Simple sentiment analysis based on keywords"""
        if not news_items:
            return "neutral"
        
        bullish_keywords = ['beat', 'growth', 'partnership', 'approval', 'buy', 'upgrade', 'strong']
        bearish_keywords = ['miss', 'loss', 'lawsuit', 'sell', 'downgrade', 'weak', 'delay']
        
        bullish_count = 0
        bearish_count = 0
        
        for item in news_items[:5]:  # Check last 5 news items
            title = item.get('title', '').lower() + ' ' + item.get('summary', '').lower()
            
            for word in bullish_keywords:
                if word in title:
                    bullish_count += 1
            for word in bearish_keywords:
                if word in title:
                    bearish_count += 1
        
        if bullish_count > bearish_count * 1.5:
            return "bullish"
        elif bearish_count > bullish_count * 1.5:
            return "bearish"
        return "neutral"


class BiotechScanner:
    """Track biotech stocks with Phase 3 trials"""
    
    # Known biotech stocks with active Phase 3 programs
    PHASE3_PIPELINE = {
        'ABBV': {'drug': 'Skyrizi expansion', 'indication': 'Crohns', ' catalyst_date': '2026'},
        'BIIB': {'drug': 'Leqembi', 'indication': 'Alzheimers', 'catalyst_date': 'ongoing'},
        'GILD': {'drug': 'Trodelvy', 'indication': 'Breast cancer', 'catalyst_date': '2026'},
        'JNJ': {'drug': 'Spravato', 'indication': 'Depression', 'catalyst_date': '2026'},
        'LLY': {'drug': 'Donanemab', 'indication': 'Alzheimers', 'catalyst_date': '2026'},
        'MRK': {'drug': 'Keytruda expansions', 'indication': 'Multiple cancers', 'catalyst_date': 'ongoing'},
        'PFE': {'drug': 'Ponsegromab', 'indication': 'Cachexia', 'catalyst_date': '2026'},
        'REGN': {'drug': 'Dupixent expansion', 'indication': 'COPD', 'catalyst_date': '2026'},
        'VRTX': {'drug': 'Casgevy', 'indication': 'Sickle cell', 'catalyst_date': 'ongoing'},
        'VXRT': {'drug': 'VXA-CoV2', 'indication': 'COVID vaccine', 'catalyst_date': '2026'},
    }
    
    def check_phase3(self, symbol: str) -> Optional[Dict]:
        """Check if stock has active Phase 3 trials"""
        return self.PHASE3_PIPELINE.get(symbol)


class AnalystRatingFetcher:
    """Fetch analyst ratings and price targets"""
    
    def get_rating(self, symbol: str) -> Dict:
        """Get analyst recommendations"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # Get recommendation trends if available
            try:
                recs = ticker.recommendations
                if recs is not None and not recs.empty:
                    latest = recs.iloc[-1]
                    return {
                        'rating': latest.get('To Grade', 'Hold'),
                        'target': info.get('targetMeanPrice', info.get('currentPrice', 0)),
                        'upside': ((info.get('targetMeanPrice', 0) / info.get('currentPrice', 1)) - 1) * 100
                    }
            except:
                pass
            
            # Fallback to info
            return {
                'rating': info.get('recommendationKey', 'hold').upper(),
                'target': info.get('targetMeanPrice', info.get('currentPrice', 0)),
                'upside': ((info.get('targetMeanPrice', 0) / info.get('currentPrice', 1)) - 1) * 100 if info.get('currentPrice') else 0
            }
        except:
            return {'rating': 'UNKNOWN', 'target': 0, 'upside': 0}


class GapAnalyzer:
    """Analyze gap down and consolidation patterns"""
    
    def analyze(self, df: pd.DataFrame) -> Dict:
        """Check for gapped down and consolidated pattern"""
        if len(df) < 20:
            return {'gapped_down': False, 'consolidated': False, 'pattern': 'none'}
        
        # Check for gap down (current open significantly below previous close)
        recent = df.tail(20)
        gap_down_days = []
        
        for i in range(1, len(recent)):
            prev_close = recent.iloc[i-1]['Close']
            curr_open = recent.iloc[i]['Open']
            gap_pct = (curr_open - prev_close) / prev_close
            
            if gap_pct < -0.05:  # 5% gap down
                gap_down_days.append(i)
        
        has_gap = len(gap_down_days) > 0
        
        # Check for consolidation (tight trading range after gap)
        if has_gap:
            last_10 = recent.tail(10)
            high = last_10['High'].max()
            low = last_10['Low'].min()
            range_pct = (high - low) / last_10['Close'].mean()
            
            consolidated = range_pct < 0.08  # Less than 8% range = consolidation
            
            return {
                'gapped_down': True,
                'consolidated': consolidated,
                'pattern': 'gap_and_consolidate' if consolidated else 'gap_down',
                'days_since_gap': len(recent) - gap_down_days[-1],
                'consolidation_range': range_pct
            }
        
        return {'gapped_down': False, 'consolidated': False, 'pattern': 'none'}


class LowConvictionPattern:
    """
    Detect 'Low Conviction Rally' pattern - perfect for cheap options
    Pattern: Price up + Volume extremely low + Above SMAs + Near resistance
    This suggests stealth accumulation before potential explosive move
    """
    
    def detect(self, df: pd.DataFrame, info: Dict) -> Dict:
        """
        Detect low conviction rally pattern
        Returns pattern details if found
        """
        if len(df) < 20:
            return {'pattern_found': False}
        
        try:
            # Get current data
            current_price = info.get('currentPrice', info.get('regularMarketPrice', 0))
            prev_close = info.get('previousClose', 0)
            today_volume = info.get('volume', info.get('regularMarketVolume', 0))
            
            if current_price == 0 or today_volume == 0:
                return {'pattern_found': False}
            
            # Calculate price change
            price_change = ((current_price - prev_close) / prev_close * 100) if prev_close else 0
            
            # Calculate RVOL (Relative Volume)
            avg_volume_20d = df['Volume'].tail(20).mean()
            rvol = today_volume / avg_volume_20d if avg_volume_20d > 0 else 1
            
            # Check moving averages
            closes = df['Close'].values
            sma20 = pd.Series(closes).rolling(20).mean().iloc[-1]
            sma50 = pd.Series(closes).rolling(50).mean().iloc[-1] if len(closes) >= 50 else None
            
            # Check if near highs
            high_20d = df['High'].tail(20).max()
            distance_to_high = ((high_20d - current_price) / current_price * 100)
            
            # PATTERN CRITERIA:
            # 1. Price up (> 0.5%)
            # 2. Volume extremely low (RVOL < 0.3x)
            # 3. Above 20 SMA (trend intact)
            # 4. Near recent highs (< 3% from 20d high)
            
            criteria_met = 0
            checks = {
                'price_up': price_change > 0.5,
                'low_volume': rvol < 0.3,
                'above_sma20': current_price > sma20,
                'near_highs': distance_to_high < 3.0
            }
            
            for check, passed in checks.items():
                if passed:
                    criteria_met += 1
            
            # Pattern confirmed if 3+ criteria met
            pattern_found = criteria_met >= 3
            
            return {
                'pattern_found': pattern_found,
                'pattern_name': 'low_conviction_rally',
                'confidence': (criteria_met / 4) * 100,
                'price_change': round(price_change, 2),
                'rvol': round(rvol, 2),
                'above_sma20': checks['above_sma20'],
                'above_sma50': current_price > sma50 if sma50 else False,
                'distance_to_20d_high': round(distance_to_high, 2),
                'criteria_met': criteria_met,
                'checks': checks,
                'interpretation': self._interpret(checks, price_change, rvol)
            }
            
        except Exception as e:
            return {'pattern_found': False, 'error': str(e)}
    
    def _interpret(self, checks: Dict, price_change: float, rvol: float) -> str:
        """Generate interpretation of the pattern"""
        if not checks['price_up']:
            return "Price not moving up - pattern invalid"
        
        if not checks['low_volume']:
            return "Volume too high - not a quiet rally"
        
        interpretations = []
        
        if checks['price_up'] and checks['low_volume']:
            interpretations.append("Quiet accumulation detected")
        
        if checks['above_sma20']:
            interpretations.append("Trend remains bullish")
        
        if checks['near_highs']:
            interpretations.append("Testing resistance with stealth")
        
        if len(interpretations) >= 3:
            return "🎯 PRIME SETUP: Stealth breakout building. Low volume = cheap options. Explosive move likely when volume returns."
        elif len(interpretations) == 2:
            return "⚠️ DECENT SETUP: Some quiet accumulation. Watch for volume spike."
        else:
            return "➖ WEAK SETUP: Pattern present but not ideal"


class MomentumCalculator:
    """Calculate price momentum indicators"""
    
    def calculate(self, df: pd.DataFrame) -> Dict:
        """Calculate momentum score"""
        if len(df) < 20:
            return {'score': 50, 'trend': 'neutral'}
        
        closes = df['Close'].values
        
        # Price change over different periods
        change_5d = (closes[-1] - closes[-5]) / closes[-5] if len(closes) >= 5 else 0
        change_10d = (closes[-1] - closes[-10]) / closes[-10] if len(closes) >= 10 else 0
        change_20d = (closes[-1] - closes[-20]) / closes[-20] if len(closes) >= 20 else 0
        
        # Volume trend
        volumes = df['Volume'].values
        vol_avg = np.mean(volumes[-10:])
        vol_recent = np.mean(volumes[-3:])
        vol_spike = vol_recent > vol_avg * 1.5
        
        # Calculate momentum score (0-100)
        momentum = 50
        momentum += change_5d * 200  # 1% move = 2 points
        momentum += change_10d * 100
        momentum += change_20d * 50
        
        if vol_spike:
            momentum += 10 if change_5d > 0 else -10
        
        momentum = max(0, min(100, momentum))
        
        trend = 'bullish' if momentum > 60 else 'bearish' if momentum < 40 else 'neutral'
        
        return {
            'score': momentum,
            'trend': trend,
            'change_5d': change_5d,
            'change_20d': change_20d,
            'volume_spike': vol_spike
        }


class OptionsChainFilter:
    """Filter options chain for criteria"""
    
    def find_cheap_options(self, symbol: str, max_cost: float = 10.0) -> Optional[Dict]:
        """Find options under $10, ATM or 1 strike above - WEEKLIES ONLY (0-14 DTE)"""
        try:
            ticker = yf.Ticker(symbol)
            expirations = ticker.options
            
            if not expirations:
                return None
            
            # Filter for weekly options only (0-7 DTE = this week, 7-14 DTE = next week)
            today = datetime.now()
            weekly_exps = []
            
            for exp in expirations:
                exp_date = datetime.strptime(exp, '%Y-%m-%d')
                days_to_exp = (exp_date - today).days
                
                # Only include 0-14 DTE (this week and next week)
                if 0 <= days_to_exp <= 14:
                    weekly_exps.append((exp, days_to_exp))
            
            # Sort by days to expiration
            weekly_exps.sort(key=lambda x: x[1])
            
            if not weekly_exps:
                return None
            
            # Prefer 0-7 DTE (this week), fallback to 7-14 DTE (next week)
            this_week = [e for e in weekly_exps if e[1] <= 7]
            next_week = [e for e in weekly_exps if 7 < e[1] <= 14]
            
            if this_week:
                exp, dte = this_week[0]
                exp_label = f"{exp} (This Week - {dte} DTE)"
            elif next_week:
                exp, dte = next_week[0]
                exp_label = f"{exp} (Next Week - {dte} DTE)"
            else:
                return None
            chain = ticker.option_chain(exp)
            
            info = ticker.info
            current = info.get('currentPrice', info.get('regularMarketPrice', 0))
            
            # Find ATM and 1 strike above
            calls = chain.calls
            puts = chain.puts
            
            # ATM strike
            atm_strike = round(current, 1) if current < 100 else round(current, 0)
            
            # Get ATM call
            atm_call = calls[calls['strike'] == atm_strike]
            if atm_call.empty:
                atm_call = calls[calls['strike'] >= current].head(1)
            
            # Get 1 strike above
            higher_call = calls[calls['strike'] > current].head(1)
            
            result = {
                'symbol': symbol,
                'current_price': current,
                'expiration': exp_label,
                'dte': dte,
                'atm_option': None,
                'above_option': None
            }
            
            if not atm_call.empty:
                row = atm_call.iloc[0]
                cost = row['lastPrice'] if row['lastPrice'] > 0 else (row['bid'] + row['ask']) / 2
                if cost <= max_cost and cost > 0:
                    result['atm_option'] = {
                        'strike': row['strike'],
                        'cost': cost,
                        'iv': row['impliedVolatility'] * 100 if row['impliedVolatility'] else 0,
                        'volume': int(row['volume']) if not pd.isna(row['volume']) else 0,
                        'oi': int(row['openInterest']) if not pd.isna(row['openInterest']) else 0
                    }
            
            if not higher_call.empty:
                row = higher_call.iloc[0]
                cost = row['lastPrice'] if row['lastPrice'] > 0 else (row['bid'] + row['ask']) / 2
                if cost <= max_cost and cost > 0:
                    result['above_option'] = {
                        'strike': row['strike'],
                        'cost': cost,
                        'iv': row['impliedVolatility'] * 100 if row['impliedVolatility'] else 0,
                        'volume': int(row['volume']) if not pd.isna(row['volume']) else 0,
                        'oi': int(row['openInterest']) if not pd.isna(row['openInterest']) else 0
                    }
            
            return result
            
        except Exception as e:
            return None


class UnusualActivityDetector:
    """Detect unusual options flow"""
    
    def detect(self, symbol: str) -> Dict:
        """Detect unusual options activity - WEEKLIES ONLY"""
        try:
            ticker = yf.Ticker(symbol)
            expirations = ticker.options
            
            if not expirations:
                return {'unusual': False}
            
            # Filter for weekly expirations only (0-14 DTE)
            today = datetime.now()
            weekly_exps = []
            
            for exp in expirations:
                exp_date = datetime.strptime(exp, '%Y-%m-%d')
                days_to_exp = (exp_date - today).days
                if 0 <= days_to_exp <= 14:
                    weekly_exps.append(exp)
            
            if not weekly_exps:
                return {'unusual': False}
            
            # Check the nearest weekly expiration
            chain = ticker.option_chain(weekly_exps[0])
            
            total_call_vol = chain.calls['volume'].sum()
            total_put_vol = chain.puts['volume'].sum()
            total_call_oi = chain.calls['openInterest'].sum()
            total_put_oi = chain.puts['openInterest'].sum()
            
            # Calculate metrics
            pc_ratio = total_put_vol / total_call_vol if total_call_vol > 0 else 1
            
            # Find high volume strikes (unusual activity)
            avg_call_vol = chain.calls['volume'].mean()
            high_vol_calls = chain.calls[chain.calls['volume'] > avg_call_vol * 3]
            
            unusual = {
                'unusual': len(high_vol_calls) > 0 or pc_ratio < 0.5 or pc_ratio > 2,
                'pc_ratio': pc_ratio,
                'total_call_volume': int(total_call_vol),
                'total_put_volume': int(total_put_vol),
                'call_oi': int(total_call_oi),
                'put_oi': int(total_put_oi),
                'sentiment': 'bullish' if pc_ratio < 0.7 else 'bearish' if pc_ratio > 1.3 else 'neutral',
                'high_activity_strikes': high_vol_calls[['strike', 'volume', 'openInterest']].to_dict('records')[:3] if not high_vol_calls.empty else []
            }
            
            return unusual
            
        except:
            return {'unusual': False}


class AdvancedOptionsScanner:
    """
    Master scanner combining all features:
    - Options flow (B)
    - Unusual activity alerts (C)
    - Catalyst check
    - News sentiment
    - Medical Phase 3
    - Momentum
    - Analyst ratings
    - Gap patterns
    - Cheap options filter ($10 or less)
    """
    
    def __init__(self, account_value: float = 10000):
        self.account_value = account_value
        self.news_analyzer = NewsAnalyzer()
        self.biotech_scanner = BiotechScanner()
        self.analyst_fetcher = AnalystRatingFetcher()
        self.gap_analyzer = GapAnalyzer()
        self.momentum_calc = MomentumCalculator()
        self.options_filter = OptionsChainFilter()
        self.activity_detector = UnusualActivityDetector()
        self.low_conviction = LowConvictionPattern()
        
        # Watchlist
        self.watchlist = [
            # Meme/Momentum
            'AMC', 'GME', 'BB', 'BBBY',
            # EV/Growth
            'RIVN', 'LCID', 'SOFI', 'PLTR',
            # Value/Dividend
            'NOK', 'F', 'BAC', 'T',
            # Biotech/Pharma
            'ABBV', 'BIIB', 'GILD', 'JNJ', 'LLY', 'MRK', 'PFE', 'REGN',
            # Recovery
            'AAL', 'CCL', 'NCLH', 'UBER',
            # Energy (for low conviction pattern)
            'KMI', 'XOM', 'CVX', 'OXY', 'MPC', 'VLO', 'PSX'
        ]
    
    def scan_stock(self, symbol: str) -> Optional[OptionsSignal]:
        """Complete scan of a single stock"""
        try:
            # Fetch data
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="1mo")
            
            if hist.empty:
                return None
            
            info = ticker.info
            current = info.get('currentPrice', info.get('regularMarketPrice', 0))
            
            # 1. News & Catalysts
            news = self.news_analyzer.get_news(symbol)
            sentiment = self.news_analyzer.analyze_sentiment(news)
            
            # 2. Biotech Phase 3
            phase3 = self.biotech_scanner.check_phase3(symbol)
            
            # 3. Analyst Rating
            analyst = self.analyst_fetcher.get_rating(symbol)
            
            # 4. Gap Analysis
            gap = self.gap_analyzer.analyze(hist)
            
            # 5. Momentum
            momentum = self.momentum_calc.calculate(hist)
            
            # 6. Options Chain ($10 or less)
            options = self.options_filter.find_cheap_options(symbol, max_cost=10.0)
            
            # 7. Unusual Activity
            unusual = self.activity_detector.detect(symbol)
            
            # 8. Low Conviction Pattern (NEW)
            low_conviction_pattern = self.low_conviction.detect(hist, info)
            
            # Determine best strategy
            strategy = self._determine_strategy(
                symbol, phase3, gap, momentum, unusual, sentiment, analyst, low_conviction_pattern
            )
            
            if not strategy:
                return None
            
            # Build signal
            signal = self._build_signal(
                symbol, current, strategy, momentum, gap, phase3, 
                analyst, sentiment, options, unusual, news, low_conviction_pattern
            )
            
            return signal
            
        except Exception as e:
            print(f"Error scanning {symbol}: {e}")
            return None
    
    def _determine_strategy(self, symbol, phase3, gap, momentum, unusual, sentiment, analyst, low_conviction_pattern) -> Optional[str]:
        """Determine which strategy fits best"""
        
        # Priority 1: Low Conviction Pattern (NEW - Cheap Options Opportunity)
        if low_conviction_pattern.get('pattern_found') and low_conviction_pattern.get('confidence', 0) >= 75:
            return 'low_conviction'
        
        # Priority 2: Biotech Phase 3
        if phase3:
            return 'biotech'
        
        # Priority 3: Gap and Consolidate
        if gap['gapped_down'] and gap['consolidated']:
            return 'gap_fill'
        
        # Priority 4: Unusual Options Flow
        if unusual.get('unusual') and unusual.get('pc_ratio', 1) < 0.5:
            return 'flow'
        
        # Priority 5: Strong Momentum + Catalyst
        if momentum['score'] > 65 and sentiment == 'bullish':
            return 'momentum'
        
        # Priority 6: Analyst Upgrade + Momentum
        if analyst['rating'] in ['STRONG_BUY', 'BUY'] and analyst['upside'] > 10:
            return 'catalyst'
        
        return None
    
    def _build_signal(self, symbol, current, strategy, momentum, gap, phase3, 
                     analyst, sentiment, options, unusual, news, low_conviction_pattern=None) -> OptionsSignal:
        """Build complete signal"""
        
        # Determine direction
        direction = 'CALL' if momentum['trend'] == 'bullish' else 'PUT'
        
        # Select option
        selected_option = None
        if options:
            if options.get('atm_option'):
                selected_option = options['atm_option']
            elif options.get('above_option'):
                selected_option = options['above_option']
        
        # Calculate targets
        if direction == 'CALL':
            target = current * 1.10  # 10% upside
            stop = current * 0.95    # 5% stop
        else:
            target = current * 0.90  # 10% downside
            stop = current * 1.05    # 5% stop
        
        # Build signal
        return OptionsSignal(
            symbol=symbol,
            strategy=strategy,
            direction=direction,
            confidence=min(85, 50 + momentum['score'] / 2),
            current_price=current,
            entry_price=current,
            target_price=round(target, 2),
            stop_loss=round(stop, 2),
            suggested_strike=selected_option['strike'] if selected_option else round(current, 1),
            option_cost=selected_option['cost'] if selected_option else 0,
            expiration=options['expiration'] if options else '',
            days_to_expiration=options['dte'] if options else 0,
            catalyst=phase3['drug'] if phase3 else (news[0].get('title', '')[:50] if news else None),
            news_sentiment=sentiment,
            analyst_rating=analyst['rating'],
            analyst_target=analyst['target'],
            phase3_drug=phase3['drug'] if phase3 else None,
            gap_status=f"{gap['pattern']} ({gap.get('days_since_gap', 0)}d ago)" if gap['gapped_down'] else 'none',
            momentum_score=momentum['score'],
            volume_spike=momentum['volume_spike'],
            unusual_options_activity=unusual.get('unusual', False),
            max_loss=selected_option['cost'] * 100 if selected_option else 0,
            max_gain=selected_option['cost'] * 100 * 2 if selected_option else 0,
            risk_reward=2.0
        )
    
    def scan_watchlist(self) -> List[OptionsSignal]:
        """Scan entire watchlist"""
        signals = []
        
        print("="*80)
        print("🔥 ADVANCED OPTIONS SCANNER")
        print("Features: Flow | Unusual Activity | Catalysts | Phase 3 | Momentum | Analyst Ratings | Gap Patterns | <$10 Options")
        print("="*80)
        print()
        
        for symbol in self.watchlist:
            print(f"Scanning {symbol}...", end=" ")
            signal = self.scan_stock(symbol)
            if signal:
                signals.append(signal)
                print(f"✅ {signal.strategy.upper()}")
            else:
                print("➖ No setup")
        
        print()
        print("="*80)
        print(f"📊 Found {len(signals)} trade setups")
        print("="*80)
        
        return signals
    
    def print_signals(self, signals: List[OptionsSignal]):
        """Pretty print signals"""
        if not signals:
            print("No signals found.")
            return
        
        # Sort by confidence
        signals.sort(key=lambda x: x.confidence, reverse=True)
        
        for i, s in enumerate(signals, 1):
            print()
            print(f"#{i} {s.symbol} - {s.strategy.upper()}")
            print("-"*80)
            print(f"  Strategy: {s.strategy} | Direction: {s.direction} | Confidence: {s.confidence:.0f}%")
            print(f"  Price: ${s.current_price:.2f} → Target: ${s.target_price:.2f} | Stop: ${s.stop_loss:.2f}")
            print(f"  Option: ${s.suggested_strike} strike @ ${s.option_cost:.2f} ({s.days_to_expiration} DTE)")
            print(f"  Analyst: {s.analyst_rating} | Target: ${s.analyst_target:.2f}")
            print(f"  Momentum: {s.momentum_score:.0f}/100 | Gap: {s.gap_status}")
            if s.phase3_drug:
                print(f"  🧬 Phase 3: {s.phase3_drug}")
            if s.unusual_options_activity:
                print(f"  ⚡ Unusual Options Activity Detected")
            print(f"  Max Risk: ${s.max_loss:.2f} | Potential: ${s.max_gain:.2f}")
            print(f"  Catalyst: {s.catalyst}")


    def scan_cheap_options(self, max_contract_cost: float = 5.00) -> List[Dict]:
        """
        $5 SCANNER - Find cheap options under $5 per contract
        Lottery ticket plays with massive ROI potential
        """
        cheap_plays = []
        
        print("="*80)
        print(f"💰 $5 SCANNER - CHEAP OPTIONS FINDER (Under ${max_contract_cost}/contract)")
        print("="*80)
        print()
        
        for symbol in self.watchlist:
            try:
                ticker = yf.Ticker(symbol)
                expirations = ticker.options
                
                if not expirations:
                    continue
                
                # Get weekly expiration
                today = datetime.now()
                weekly_exps = []
                
                for exp in expirations:
                    exp_date = datetime.strptime(exp, '%Y-%m-%d')
                    days_to_exp = (exp_date - today).days
                    if 0 <= days_to_exp <= 14:
                        weekly_exps.append((exp, days_to_exp))
                
                if not weekly_exps:
                    continue
                
                weekly_exps.sort(key=lambda x: x[1])
                exp, dte = weekly_exps[0]
                
                # Get options chain
                chain = ticker.option_chain(exp)
                info = ticker.info
                current = info.get('currentPrice', 0)
                
                if current == 0:
                    continue
                
                # Find cheap calls and puts
                calls = chain.calls
                puts = chain.puts
                max_price_per_share = max_contract_cost / 100
                
                # Process CALLS
                cheap_calls = calls[calls['lastPrice'] <= max_price_per_share]
                cheap_calls = cheap_calls[cheap_calls['lastPrice'] > 0]
                
                if not cheap_calls.empty:
                    # Get closest OTM call
                    otm_calls = cheap_calls[cheap_calls['strike'] > current]
                    if not otm_calls.empty:
                        best = otm_calls.sort_values('strike').iloc[0]
                        
                        contract_cost = best['lastPrice'] * 100
                        breakeven = best['strike'] + best['lastPrice']
                        
                        # Calculate scenarios
                        distance_pct = ((best['strike'] - current) / current) * 100
                        upside_to_breakeven = ((breakeven - current) / current) * 100
                        
                        # Calculate stock prices needed for target ROIs (100%, 200%, 500%, 1000%)
                        def calc_call_roi(target_roi):
                            """Calculate stock price and profit for target ROI on CALL"""
                            if contract_cost <= 0:
                                return 0, 0, 0
                            target_profit = contract_cost * (target_roi / 100)
                            target_option_value = (target_profit / 100) + best['lastPrice']
                            target_stock_price = best['strike'] + target_option_value
                            stock_move_pct = ((target_stock_price - current) / current) * 100
                            return target_stock_price, target_profit, stock_move_pct
                        
                        roi_100 = calc_call_roi(100)
                        roi_200 = calc_call_roi(200)
                        roi_500 = calc_call_roi(500)
                        roi_1000 = calc_call_roi(1000)
                        
                        # Get analyst data
                        analyst = self.analyst_fetcher.get_rating(symbol)
                        
                        cheap_plays.append({
                            'symbol': symbol,
                            'current': current,
                            'strike': best['strike'],
                            'option_type': 'CALL',
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
                            'roi_100': roi_100,
                            'roi_200': roi_200,
                            'roi_500': roi_500,
                            'roi_1000': roi_1000,
                            'analyst_rating': analyst['rating'],
                            'analyst_target': analyst['target']
                        })
                
                # Process PUTS
                cheap_puts = puts[puts['lastPrice'] <= max_price_per_share]
                cheap_puts = cheap_puts[cheap_puts['lastPrice'] > 0]
                
                if not cheap_puts.empty:
                    # Get closest OTM put (strike < current)
                    otm_puts = cheap_puts[cheap_puts['strike'] < current]
                    if not otm_puts.empty:
                        best = otm_puts.sort_values('strike', ascending=False).iloc[0]
                        
                        contract_cost = best['lastPrice'] * 100
                        breakeven = best['strike'] - best['lastPrice']
                        
                        # Calculate scenarios
                        distance_pct = ((current - best['strike']) / current) * 100
                        downside_to_breakeven = ((current - breakeven) / current) * 100
                        
                        # Calculate stock prices needed for target ROIs on PUT
                        def calc_put_roi(target_roi):
                            """Calculate stock price and profit for target ROI on PUT"""
                            if contract_cost <= 0:
                                return 0, 0, 0
                            target_profit = contract_cost * (target_roi / 100)
                            target_option_value = (target_profit / 100) + best['lastPrice']
                            target_stock_price = best['strike'] - target_option_value
                            stock_move_pct = ((target_stock_price - current) / current) * 100
                            return target_stock_price, target_profit, stock_move_pct
                        
                        roi_100 = calc_put_roi(100)
                        roi_200 = calc_put_roi(200)
                        roi_500 = calc_put_roi(500)
                        roi_1000 = calc_put_roi(1000)
                        
                        # Get analyst data
                        analyst = self.analyst_fetcher.get_rating(symbol)
                        
                        cheap_plays.append({
                            'symbol': symbol,
                            'current': current,
                            'strike': best['strike'],
                            'option_type': 'PUT',
                            'price_per_share': best['lastPrice'],
                            'contract_cost': contract_cost,
                            'breakeven': breakeven,
                            'dte': dte,
                            'expiration': exp,
                            'volume': int(best['volume']) if not pd.isna(best['volume']) else 0,
                            'oi': int(best['openInterest']) if not pd.isna(best['openInterest']) else 0,
                            'iv': best['impliedVolatility'] * 100 if best['impliedVolatility'] else 0,
                            'distance_pct': distance_pct,
                            'upside_to_breakeven': downside_to_breakeven,
                            'roi_100': roi_100,
                            'roi_200': roi_200,
                            'roi_500': roi_500,
                            'roi_1000': roi_1000,
                            'analyst_rating': analyst['rating'],
                            'analyst_target': analyst['target']
                        })
                
            except Exception as e:
                continue
        
        # Sort by contract cost
        cheap_plays.sort(key=lambda x: x['contract_cost'])
        
        return cheap_plays
    
    def print_cheap_options(self, plays: List[Dict]):
        """Print $5 scanner results with ROI scenarios"""
        if not plays:
            print("No cheap options found under $5.")
            return
        
        print()
        print("="*80)
        print(f"🎯 TOP {len(plays)} CHEAP OPTIONS PLAYS")
        print("="*80)
        print()
        
        for i, play in enumerate(plays[:15], 1):
            # Get option type from stored data
            option_type = play.get('option_type', 'CALL')
            emoji = "📈" if option_type == "CALL" else "📉"
            
            print(f"{i}. {emoji} {play['symbol']} - {option_type}")
            print(f"   Current: ${play['current']:.2f} | Strike: ${play['strike']:.2f} (+{play['distance_pct']:.1f}% OTM)")
            print(f"   💰 Cost: ${play['price_per_share']:.3f}/share = ${play['contract_cost']:.2f}/contract")
            print(f"   📅 Expires: {play['expiration']} ({play['dte']} DTE)")
            print(f"   📊 Volume: {play['volume']} | OI: {play['oi']} | IV: {play['iv']:.1f}%")
            print(f"   📊 Analyst: {play['analyst_rating']} | Target: ${play['analyst_target']:.2f}")
            print(f"   🎯 Breakeven: ${play['breakeven']:.2f} (need {play['upside_to_breakeven']:.1f}%)")
            print()
            print(f"   📈 ROI SCENARIOS (What stock price needed):")
            
            # 100% ROI (2x)
            sp_100, profit_100, move_100 = play['roi_100']
            print(f"      100% ROI (2x): Stock ${sp_100:.2f} (+{move_100:.1f}%) → Profit ${profit_100:.0f}")
            
            # 200% ROI (3x)
            sp_200, profit_200, move_200 = play['roi_200']
            if move_200 < 100:  # Only show if reasonable
                print(f"      200% ROI (3x): Stock ${sp_200:.2f} (+{move_200:.1f}%) → Profit ${profit_200:.0f}")
            
            # 500% ROI (6x)
            sp_500, profit_500, move_500 = play['roi_500']
            if move_500 < 200:
                print(f"      500% ROI (6x): Stock ${sp_500:.2f} (+{move_500:.1f}%) → Profit ${profit_500:.0f} 🔥")
            
            # 1000% ROI (11x)
            sp_1000, profit_1000, move_1000 = play['roi_1000']
            if move_1000 < 500:
                print(f"      1000% ROI (11x): Stock ${sp_1000:.2f} (+{move_1000:.1f}%) → Profit ${profit_1000:.0f} 🚀")
            
            print()
        
        print("="*80)
        print("💡 These are lottery ticket plays - risk $3-5 for potential 1000%+ gains")
        print("="*80)
    
    def run_full_scan(self, include_cheap: bool = True):
        """
        Run COMPLETE scan - both advanced signals AND cheap options
        """
        # Run advanced scanner
        signals = self.scan_watchlist()
        self.print_signals(signals)
        
        print()
        print()
        
        # Run $5 scanner
        if include_cheap:
            cheap_plays = self.scan_cheap_options(max_contract_cost=5.00)
            self.print_cheap_options(cheap_plays)
        
        return signals, cheap_plays


def print_legal_disclaimer():
    """Print legal disclaimer before any output"""
    print('╔' + '═'*88 + '╗')
    print('║' + ' '*20 + '⚠️  LEGAL DISCLAIMER  ⚠️' + ' '*43 + '║')
    print('╠' + '═'*88 + '╣')
    print('║  NOT FINANCIAL ADVICE                                                               ║')
    print('║  • This scanner is for EDUCATIONAL PURPOSES ONLY                                    ║')
    print('║  • I am NOT a licensed financial advisor                                            ║')
    print('║  • I am NOT registered with SEC/FINRA                                               ║')
    print('║  • These are NOT recommendations to buy or sell                                       ║')
    print('║                                                                                       ║')
    print('║  RISK WARNING                                                                         ║')
    print('║  • Options trading involves SUBSTANTIAL RISK of loss                                ║')
    print('║  • You can lose 100% of your investment                                             ║')
    print('║  • Past performance does NOT guarantee future results                               ║')
    print('║  • Always do your OWN RESEARCH before trading                                       ║')
    print('║                                                                                       ║')
    print('║  BY USING THIS INFORMATION, YOU AGREE:                                                ║')
    print('║  • To hold harmless from any losses                                                  ║')
    print('║  • To consult a licensed professional for financial advice                         ║')
    print('║  • That you are solely responsible for your trading decisions                      ║')
    print('╚' + '═'*88 + '╝')
    print()

def print_educational_footer():
    """Print educational reminder after output"""
    print('═'*90)
    print('⚠️  REMINDER: This is for EDUCATIONAL PURPOSES ONLY')
    print('⚠️  NOT financial advice. NOT a recommendation.')
    print('⚠️  You can lose 100% of your money trading options.')
    print('⚠️  Consult a licensed professional before trading.')
    print('═'*90)


# Run combined scanner
if __name__ == "__main__":
    print_legal_disclaimer()
    scanner = AdvancedOptionsScanner(account_value=10000)
    scanner.run_full_scan(include_cheap=True)
    print_educational_footer()
