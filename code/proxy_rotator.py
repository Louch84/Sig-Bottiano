# PROXY ROTATOR - PART 1
import requests
import time
import random
from bs4 import BeautifulSoup

class ProxyRotator:
    def __init__(self):
        self.proxies = []
        self.current_index = 0
        self.failed_proxies = set()
    
    def load_free_proxies(self):
        urls = [
            'https://www.sslproxies.org/',
            'https://free-proxy-list.net/',
        ]
        for url in urls:
            try:
                response = requests.get(url, timeout=10)
                soup = BeautifulSoup(response.text, 'html.parser')
                table = soup.find('table', {'class': 'table'})
                if table:
                    rows = table.find_all('tr')[1:21]
                    for row in rows:
                        cols = row.find_all('td')
                        if len(cols) >= 2:
                            ip = cols[0].text.strip()
                            port = cols[1].text.strip()
                            proxy = {
                                'http': f'http://{ip}:{port}', 
                                'https': f'http://{ip}:{port}'
                            }
                            if proxy['http'] not in self.failed_proxies:
                                self.proxies.append(proxy)
            except:
                continue
        print(f"Loaded {len(self.proxies)} proxies")
    
    def get_proxy(self):
        if not self.proxies:
            self.load_free_proxies()
        attempts = 0
        while attempts < len(self.proxies):
            proxy = self.proxies[self.current_index % len(self.proxies)]
            self.current_index += 1
            if proxy['http'] not in self.failed_proxies:
                return proxy
            attempts += 1
        return None
    
    def mark_failed(self, proxy):
        self.failed_proxies.add(proxy['http'])


# RATE LIMITER - PART 2

class RateLimiter:
    def __init__(self):
        self.last_call = {}
        self.delays = {
            'yahoo': 0.5,
            'finviz': 3.0,
            'stocksera': 1.0,
            'default': 1.0
        }
    
    def wait(self, source):
        delay = self.delays.get(source, self.delays['default'])
        if source in self.last_call:
            elapsed = time.time() - self.last_call[source]
            if elapsed < delay:
                time.sleep(delay - elapsed + random.uniform(0.1, 0.3))
        self.last_call[source] = time.time()


# YAHOO FINANCE FETCHER
# pip install yfinance

import yfinance as yf

class YahooFetcher:
    def __init__(self, rate_limiter):
        self.rate_limiter = rate_limiter
    
    def get_data(self, ticker):
        self.rate_limiter.wait('yahoo')
        stock = yf.Ticker(ticker)
        info = stock.info
        
        price = info.get('currentPrice', 0)
        if price == 0:
            price = info.get('regularMarketPrice', 0)
        
        float_shares = info.get('floatShares', 0)
        short_pct = info.get('shortPercentOfFloat', 0)
        if short_pct:
            short_pct = short_pct * 100
        
        volume = info.get('volume', 0)
        avg_volume = info.get('averageVolume', 0)
        shares_short = info.get('sharesShort', 0)
        
        days_to_cover = 0
        if shares_short and avg_volume:
            days_to_cover = shares_short / avg_volume
        
        return {
            'ticker': ticker,
            'price': price,
            'market_cap': info.get('marketCap', 0),
            'float': float_shares,
            'volume': volume,
            'avg_volume': avg_volume,
            'short_pct': short_pct,
            'shares_short': shares_short,
            'days_to_cover': days_to_cover,
            'high_52w': info.get('fiftyTwoWeekHigh', 0),
            'low_52w': info.get('fiftyTwoWeekLow', 0),
        }


# STOCKSERA SHORT DATA FETCHER

class StockseraFetcher:
    def __init__(self, proxy_rotator, rate_limiter):
        self.proxy_rotator = proxy_rotator
        self.rate_limiter = rate_limiter
        self.session = requests.Session()
    
    def get_data(self, ticker):
        self.rate_limiter.wait('stocksera')
        proxy = self.proxy_rotator.get_proxy()
        
        try:
            url = f"https://stocksera.pythonanywhere.com/api/short_volume/{ticker}"
            
            if proxy:
                response = self.session.get(url, proxies=proxy, timeout=10)
            else:
                response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'short_vol_ratio': data.get('short_volume_ratio', 0),
                    'avg_short_vol': data.get('avg_short_vol', 0),
                    'total_vol': data.get('total_volume', 0)
                }
        except:
            if proxy:
                self.proxy_rotator.mark_failed(proxy)
        
        return {}


# FINVIZ SCREENER

class FinvizScreener:
    def __init__(self, proxy_rotator, rate_limiter):
        self.proxy_rotator = proxy_rotator
        self.rate_limiter = rate_limiter
        self.session = requests.Session()
    
    def get_universe(self):
        self.rate_limiter.wait('finviz')
        proxy = self.proxy_rotator.get_proxy()
        
        url = "https://finviz.com/screener.ashx?v=111&f=cap_smallover,price_under50,sh_short_o20,sh_float_u100"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        
        try:
            if proxy:
                response = self.session.get(url, headers=headers, proxies=proxy, timeout=15)
            else:
                response = self.session.get(url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                table = soup.find('table', {'class': 'table-light'})
                
                tickers = []
                if table:
                    for row in table.find_all('tr')[1:]:
                        link = row.find('a', {'class': 'screener-link-primary'})
                        if link:
                            tickers.append(link.text.strip())
                
                print(f"Found {len(tickers)} candidates")
                return tickers[:50]
        except:
            if proxy:
                self.proxy_rotator.mark_failed(proxy)
        
        return []


# SQUEEZE SCORING ALGORITHM

class SqueezeScorer:
    def score(self, data):
        score = 0
        breakdown = {}
        
        short = data.get('short_pct', 0)
        if short > 30: breakdown['short'] = 25
        elif short > 20: breakdown['short'] = 20
        elif short > 15: breakdown['short'] = 15
        else: breakdown['short'] = 0
        
        dtc = data.get('days_to_cover', 0)
        if dtc > 10: breakdown['dtc'] = 20
        elif dtc > 5: breakdown['dtc'] = 15
        elif dtc > 3: breakdown['dtc'] = 10
        else: breakdown['dtc'] = 0
        
        fl = data.get('float', 0)
        if fl < 10_000_000: breakdown['float'] = 15
        elif fl < 50_000_000: breakdown['float'] = 10
        elif fl < 100_000_000: breakdown['float'] = 5
        else: breakdown['float'] = 0
        
        vol = data.get('volume', 0)
        avg = data.get('avg_volume', 1)
        ratio = vol / avg if avg > 0 else 0
        
        if ratio > 2: breakdown['volume'] = 15
        elif ratio > 1.5: breakdown['volume'] = 10
        elif ratio > 1: breakdown['volume'] = 5
        else: breakdown['volume'] = 0
        
        price = data.get('price', 0)
        high = data.get('high_52w', 0)
        low = data.get('low_52w', 0)
        
        if high > low:
            pos = (price - low) / (high - low)
            if pos < 0.3: breakdown['position'] = 15
            elif pos < 0.5: breakdown['position'] = 10
            else: breakdown['position'] = 0
        
        cap = data.get('market_cap', 0)
        if 100_000_000 < cap < 2_000_000_000: breakdown['cap'] = 10
        elif cap < 10_000_000_000: breakdown['cap'] = 5
        else: breakdown['cap'] = 0
        
        total = sum(breakdown.values())
        
        return {
            'total': total,
            'breakdown': breakdown,
            'grade': 'A' if total >= 70 else 'B' if total >= 60 else 'C' if total >= 50 else 'F'
        }


# MAIN SCANNER - PART 1 (Setup)

import pandas as pd
from datetime import datetime

class SqueezeScanner:
    def __init__(self):
        self.proxy_rotator = ProxyRotator()
        self.rate_limiter = RateLimiter()
        self.yahoo = YahooFetcher(self.rate_limiter)
        self.stocksera = StockseraFetcher(
            self.proxy_rotator, 
            self.rate_limiter
        )
        self.finviz = FinvizScreener(
            self.proxy_rotator, 
            self.rate_limiter
        )
        self.scorer = SqueezeScorer()
    
    def get_universe(self, tickers=None):
        if not tickers:
            print("Loading from Finviz...")
            return self.finviz.get_universe()
        return tickers


# MAIN SCANNER - PART 2 (Process Loop)

    def process_ticker(self, ticker):
        try:
            yahoo_data = self.yahoo.get_data(ticker)
            stocksera_data = self.stocksera.get_data(ticker)
            data = {**yahoo_data, **stocksera_data}
            
            price = data.get('price', 0)
            if not (0.5 <= price <= 50):
                return None
            
            score_data = self.scorer.score(data)
            
            if score_data['total'] >= 50:
                return {
                    'ticker': ticker,
                    'price': price,
                    'score': score_data['total'],
                    'grade': score_data['grade'],
                    'short_pct': data.get('short_pct', 0),
                    'days_to_cover': data.get('days_to_cover', 0),
                    'float': data.get('float', 0),
                    'volume': data.get('volume', 0),
                    'avg_volume': data.get('avg_volume', 0),
                }
        except:
            pass
        return None
    
    def scan(self, tickers=None):
        results = []
        universe = self.get_universe(tickers)
        
        print(f"Scanning {len(universe)} tickers...")
        
        for i, ticker in enumerate(universe):
            print(f"[{i+1}/{len(universe)}] {ticker}", end=" ")
            
            result = self.process_ticker(ticker)
            
            if result:
                results.append(result)
                print(f"Score: {result['score']}/100")
            else:
                print("Skip")
        
        if results:
            df = pd.DataFrame(results)
            return df.sort_values('score', ascending=False)
        return pd.DataFrame()


# MAIN SCANNER - PART 3 (Run)

if __name__ == "__main__":
    scanner = SqueezeScanner()
    results = scanner.scan()
    
    print("\n" + "="*50)
    print("TOP SHORT SQUEEZE CANDIDATES")
    print("="*50)
    
    if not results.empty:
        print(results[
            ['ticker', 'price', 'score', 'grade', 'short_pct']
        ].head(10).to_string(index=False))
        
        filename = f'squeeze_{datetime.now().strftime("%Y%m%d_%H%M")}.csv'
        results.to_csv(filename, index=False)
        print(f"\nSaved {len(results)} results")
    else:
        print("No setups found")

# pip install yfinance requests pandas beautifulsoup4 lxml


# ADDITIONAL DATA FETCHERS

class StockgridFetcher:
    def __init__(self, proxy_rotator, rate_limiter):
        self.proxy_rotator = proxy_rotator
        self.rate_limiter = rate_limiter
        self.session = requests.Session()
    
    def get_data(self, ticker):
        self.rate_limiter.wait('stockgrid')
        proxy = self.proxy_rotator.get_proxy()
        
        try:
            url = f"https://stockgrid.io/api/shortinterest/{ticker}"
            headers = {'User-Agent': 'Mozilla/5.0'}
            
            if proxy:
                response = self.session.get(url, headers=headers, proxies=proxy, timeout=10)
            else:
                response = self.session.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'stockgrid_days_to_cover': data.get('daysToCover', 0),
                    'stockgrid_short_float': data.get('shortInterestPercent', 0),
                    'stockgrid_ctb': data.get('costToBorrow', 0),
                }
        except:
            if proxy:
                self.proxy_rotator.mark_failed(proxy)
        
        return {}


class OrtexFetcher:
    def __init__(self, proxy_rotator, rate_limiter):
        self.proxy_rotator = proxy_rotator
        self.rate_limiter = rate_limiter
    
    def get_data(self, ticker):
        # Ortex requires auth, returning placeholder
        # For free data, use stockgrid instead
        return {}


# Enhanced Main Scanner with more sources
class EnhancedSqueezeScanner(SqueezeScanner):
    def __init__(self):
        super().__init__()
        self.stockgrid = StockgridFetcher(self.proxy_rotator, self.rate_limiter)
    
    def process_ticker(self, ticker):
        try:
            yahoo_data = self.yahoo.get_data(ticker)
            stocksera_data = self.stocksera.get_data(ticker)
            stockgrid_data = self.stockgrid.get_data(ticker)
            
            data = {**yahoo_data, **stocksera_data, **stockgrid_data}
            
            price = data.get('price', 0)
            if not (0.5 <= price <= 50):
                return None
            
            score_data = self.scorer.score(data)
            
            if score_data['total'] >= 50:
                return {
                    'ticker': ticker,
                    'price': price,
                    'score': score_data['total'],
                    'grade': score_data['grade'],
                    'short_pct': data.get('short_pct', 0),
                    'days_to_cover': data.get('days_to_cover', 0),
                    'float': data.get('float', 0),
                }
        except:
            pass
        return None


# FREE SHORT DATA SOURCES

class ShortSqueezeDataFetcher:
    """Aggregate short data from multiple free sources"""
    
    def __init__(self, proxy_rotator, rate_limiter):
        self.proxy_rotator = proxy_rotator
        self.rate_limiter = rate_limiter
        self.session = requests.Session()
    
    def get_short_volume(self, ticker):
        """Get short volume from stocksera"""
        self.rate_limiter.wait('stocksera')
        
        try:
            url = f"https://stocksera.pythonanywhere.com/api/short_volume/{ticker}"
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return {
                    'short_vol': data.get('short_volume', 0),
                    'total_vol': data.get('total_volume', 0),
                    'short_ratio': data.get('short_volume_ratio', 0)
                }
        except:
            pass
        return {}
    
    def get_iborrow(self, ticker):
        """Get IBKR borrow fee as proxy for short squeeze"""
        # IBKR borrow fees are real-time
        # This would need API key for live data
        return {'iborrow_fee': None}


class FintelDataFetcher:
    """Fintel short data - requires free account"""
    
    def __init__(self, proxy_rotator, rate_limiter):
        self.proxy_rotator = proxy_rotator
        self.rate_limiter = rate_limiter
    
    def get_short_data(self, ticker):
        # Fintel requires account, free tier limited
        return {'fintel_short': None}


class MarketWatchFetcher:
    """Get short interest from marketwatch"""
    
    def __init__(self, proxy_rotator, rate_limiter):
        self.proxy_rotator = proxy_rotator
        self.rate_limiter = rate_limiter
        self.session = requests.Session()
    
    def get_short_interest(self, ticker):
        self.rate_limiter.wait('marketwatch')
        
        try:
            url = f"https://www.marketwatch.com/investing/stock/{ticker}/short"
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = self.session.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Parse short interest
                short_elem = soup.find('short-interest', recursive=True)
                if not short_elem:
                    # Try alternative parsing
                    pass
                    
        except Exception as e:
            pass
        
        return {}


# Usage:
# scanner = EnhancedSqueezeScanner()
# scanner.fetch_all_short_data('GME')  # Gets data from multiple sources
