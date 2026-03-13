"""
Rumor to Scanner Integration
Flow: Twitter/Options Flow → Extract Tickers → Squeeze Scanner → Entry Signal
"""

import re
import yfinance as yf
import pandas as pd
from datetime import datetime

# From rumor_sources.yaml
TWITTER_ACCOUNTS = [
    'unusual_whales', 'SpotGamma', 'InvestorsLive', 'BreakoutStocks',
    'Benzinga', 'DeItaone', 'FirstSquawk', 'ForexLive', 'LiveSquawk',
    'MarketCurrents', 'OptionAlert', 'Trade_The_Break', 'StockDweebs',
    'ChartingProdigy', 'StockTwits'
]

KEYWORDS = [
    'rumor', 'speculation', 'reportedly', 'sources say', 'considering',
    'exploring', 'potential', 'upcoming', 'exclusive', 'breaking',
    'merger', 'acquisition', 'buyout', 'partnership', 'FDA approval',
    'earnings beat', 'guidance raise'
]

# Scanner criteria
ENTRY_CRITERIA = {
    'min_short_pct': 15,
    'min_vol_ratio': 1.2,
    'max_price': 50,
    'min_price': 0.5,
    'max_float_m': 100,
}

# Twitter API Integration
import os

class TwitterFetcher:
    """Fetch tweets from financial accounts"""
    
    def __init__(self, bearer_token: str = None):
        self.bearer_token = bearer_token or os.environ.get('TWITTER_BEARER_TOKEN')
        self.base_url = "https://api.twitter.com/2"
    
    def get_tweets(self, usernames: list, max_results: int = 10) -> list:
        """Get recent tweets from specified accounts"""
        # Would need Twitter API v2
        # Placeholder for now - returns empty list
        # Real implementation would use tweepy or requests
        return []
    
    def search_tweets(self, query: str, max_results: int = 100) -> list:
        """Search tweets with keywords"""
        # Placeholder - would connect to Twitter API
        return []


class OptionsFlowFetcher:
    """Fetch options flow data"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get('UNUSUAL_WHALES_API_KEY')
    
    def get_flow(self, min_premium: int = 100000) -> list:
        """Get unusual options flow"""
        # Placeholder - would connect to Unusual Whales API
        return []

class RumorScanner:
    """Scan Twitter/Options flow for tickers, validate with squeeze scanner"""
    
    def __init__(self):
        pass
        
    def extract_tickers(self, text: str) -> list:
        """Extract $TICKERS from text"""
        pattern = r'\$([A-Z]{1,5})'
        return list(set(re.findall(pattern, text)))
    
    def scan_ticker(self, ticker: str) -> dict:
        """Run ticker through squeeze scanner criteria"""
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            price = info.get('currentPrice', 0) or info.get('regularMarketPrice', 0)
            if not price or not (ENTRY_CRITERIA['min_price'] <= price <= ENTRY_CRITERIA['max_price']):
                return None
            
            short_pct = (info.get('shortPercentOfFloat', 0) or 0) * 100
            float_shares = info.get('floatShares', 0) or 0
            volume = info.get('volume', 0) or 0
            avg_vol = info.get('averageVolume', 0) or 1
            
            vol_ratio = volume / avg_vol if avg_vol > 0 else 0
            
            # Score the setup
            score = 0
            if short_pct >= ENTRY_CRITERIA['min_short_pct']:
                score += 25
            if vol_ratio >= ENTRY_CRITERIA['min_vol_ratio']:
                score += 20
            if float_shares < ENTRY_CRITERIA['max_float_m'] * 1_000_000:
                score += 15
            if price < 15:
                score += 5
            
            if score >= 40:
                return {
                    'ticker': ticker,
                    'price': price,
                    'short_pct': short_pct,
                    'vol_ratio': vol_ratio,
                    'float_m': float_shares / 1e6,
                    'score': score,
                    'pass': short_pct >= ENTRY_CRITERIA['min_short_pct'] and vol_ratio >= ENTRY_CRITERIA['min_vol_ratio']
                }
        except:
            pass
        return None
    
    def process_rumor(self, tweet_text: str, source: str) -> dict:
        """Process a rumor tweet and return scanner results"""
        tickers = self.extract_tickers(tweet_text)
        
        results = []
        for t in tickers:
            scan_result = self.scan_ticker(t)
            if scan_result:
                results.append(scan_result)
        
        # Filter for passing setups
        passing = [r for r in results if r['pass']]
        
        return {
            'timestamp': datetime.now().isoformat(),
            'source': source,
            'tickers_found': tickers,
            'scanned': results,
            'passing': passing,
            'action': 'BUY' if passing else 'WATCH'
        }


# Example usage
if __name__ == "__main__":
    scanner = RumorScanner()
    
    # Test with sample rumor
    test_tweet = "Breaking: $AAPL rumored to be acquiring $RIVN at premium"
    
    result = scanner.process_rumor(test_tweet, 'test_source')
    
    print(f"Found: {result['tickers_found']}")
    print(f"Passing: {result['passing']}")


# Full Pipeline: Fetch → Extract → Scan → Alert

import requests

DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1473406205081817260/PaNG9cz9NWMpXWXPjKnS6k2qKB8q3WNLkZ8rVhqYvXqNK"

def send_discord_alert(result: dict):
    """Send passing setups to Discord"""
    if not result['passing']:
        return
    
    msg = "🚨 **RUMOR SCAN - PASSING SETUP**\n\n"
    
    for setup in result['passing']:
        msg += f"**${setup['ticker']}** - ${setup['price']}\n"
        msg += f"   Short: {setup['short_pct']:.1f}% | Vol: {setup['vol_ratio']:.1f}x | Score: {setup['score']}\n\n"
    
    msg += f"Source: {result['source']}\n"
    msg += f"Time: {result['timestamp']}"
    
    try:
        requests.post(DISCORD_WEBHOOK, json={"content": msg}, timeout=10)
    except:
        pass


class RumorPipeline:
    """Full rumor to trade pipeline"""
    
    def __init__(self):
        self.twitter = TwitterFetcher()
        self.options = OptionsFlowFetcher()
        self.scanner = RumorScanner()
    
    def run(self):
        """Run full pipeline"""
        results = []
        
        # 1. Get tweets from financial accounts
        tweets = self.twitter.get_tweets(TWITTER_ACCOUNTS)
        
        # 2. Search for keyword tweets
        keyword_tweets = self.twitter.search_tweets(' OR '.join(KEYWORDS))
        tweets.extend(keyword_tweets)
        
        # 3. Get options flow
        flows = self.options.get_flow()
        
        # 4. Process each
        for tweet in tweets:
            result = self.scanner.process_rumor(tweet['text'], tweet['username'])
            if result['passing']:
                results.append(result)
                send_discord_alert(result)  # Alert to Discord
        
        return results


# To enable, add to .env:
# TWITTER_BEARER_TOKEN=your_token_here
# UNUSUAL_WHALES_API_KEY=your_key_here

if __name__ == "__main__":
    # Example manual test
    scanner = RumorScanner()
    
    # Simulate a tweet
    tweet = "Breaking: $MARA rumored to be in merger talks $BTC"
    result = scanner.process_rumor(tweet, 'unusual_whales')
    
    print("=" * 50)
    print("RUMOR SCAN RESULT")
    print("=" * 50)
    print(f"Tweet: {tweet}")
    print(f"Tickers: {result['tickers_found']}")
    print(f"Passing: {result['passing']}")
    print(f"Action: {result['action']}")
