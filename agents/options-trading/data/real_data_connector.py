"""
Real Data Connector
Connects to live APIs for earnings, flow, prices, and economic data
"""

import os
import json
import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import pandas as pd

@dataclass
class LiveCatalyst:
    type: str
    description: str
    impact: str
    timing: str
    direction: str
    source: str  # API source
    raw_data: Dict

class DataConfig:
    """Configuration for API keys and endpoints"""
    
    def __init__(self):
        # Load from environment or config file
        self.ALPHA_VANTAGE_KEY = os.getenv("ALPHA_VANTAGE_API_KEY", "")
        self.POLYGON_KEY = os.getenv("POLYGON_API_KEY", "")
        self.FINNHUB_KEY = os.getenv("FINNHUB_API_KEY", "")
        self.UNUSUAL_WHALES_KEY = os.getenv("UNUSUAL_WHALES_API_KEY", "")
        self.BENZINGA_KEY = os.getenv("BENZINGA_API_KEY", "")
        
        # Check which APIs are configured
        self.available_apis = []
        if self.ALPHA_VANTAGE_KEY:
            self.available_apis.append("alpha_vantage")
        if self.POLYGON_KEY:
            self.available_apis.append("polygon")
        if self.FINNHUB_KEY:
            self.available_apis.append("finnhub")
        if self.UNUSUAL_WHALES_KEY:
            self.available_apis.append("unusual_whales")
        if self.BENZINGA_KEY:
            self.available_apis.append("benzinga")
    
    def is_configured(self) -> bool:
        """Check if at least one API is configured"""
        return len(self.available_apis) > 0
    
    def print_status(self):
        """Print API configuration status"""
        print("📡 API Configuration Status:")
        print(f"   Alpha Vantage: {'✅' if self.ALPHA_VANTAGE_KEY else '❌'}")
        print(f"   Polygon: {'✅' if self.POLYGON_KEY else '❌'}")
        print(f"   Finnhub: {'✅' if self.FINNHUB_KEY else '❌'}")
        print(f"   Unusual Whales: {'✅' if self.UNUSUAL_WHALES_KEY else '❌'}")
        print(f"   Benzinga: {'✅' if self.BENZINGA_KEY else '❌'}")
        print()

class AlphaVantageConnector:
    """Alpha Vantage API for fundamentals and earnings"""
    
    BASE_URL = "https://www.alphavantage.co/query"
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.session = None
    
    async def connect(self):
        self.session = aiohttp.ClientSession()
    
    async def close(self):
        if self.session:
            await self.session.close()
    
    async def get_earnings_calendar(self, symbol: str) -> Optional[Dict]:
        """Get earnings calendar for a symbol"""
        params = {
            "function": "EARNINGS",
            "symbol": symbol,
            "apikey": self.api_key
        }
        
        try:
            async with self.session.get(self.BASE_URL, params=params) as response:
                data = await response.json()
                return data
        except Exception as e:
            print(f"Error fetching earnings for {symbol}: {e}")
            return None
    
    async def get_quote(self, symbol: str) -> Optional[Dict]:
        """Get real-time quote"""
        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": symbol,
            "apikey": self.api_key
        }
        
        try:
            async with self.session.get(self.BASE_URL, params=params) as response:
                data = await response.json()
                quote = data.get("Global Quote", {})
                return {
                    "symbol": symbol,
                    "price": float(quote.get("05. price", 0)),
                    "change": float(quote.get("09. change", 0)),
                    "change_percent": quote.get("10. change percent", "0%"),
                    "volume": int(quote.get("06. volume", 0)),
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            print(f"Error fetching quote for {symbol}: {e}")
            return None

class FinnhubConnector:
    """Finnhub API for earnings, news, and fundamentals"""
    
    BASE_URL = "https://finnhub.io/api/v1"
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.session = None
    
    async def connect(self):
        self.session = aiohttp.ClientSession()
    
    async def close(self):
        if self.session:
            await self.session.close()
    
    async def get_earnings_calendar(self, symbol: str) -> List[Dict]:
        """Get upcoming earnings for symbol"""
        from_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        to_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        
        url = f"{self.BASE_URL}/calendar/earnings"
        params = {
            "symbol": symbol,
            "from": from_date,
            "to": to_date,
            "token": self.api_key
        }
        
        try:
            async with self.session.get(url, params=params) as response:
                data = await response.json()
                return data.get("earningsCalendar", [])
        except Exception as e:
            print(f"Error fetching Finnhub earnings for {symbol}: {e}")
            return []
    
    async def get_quote(self, symbol: str) -> Optional[Dict]:
        """Get real-time quote"""
        url = f"{self.BASE_URL}/quote"
        params = {"symbol": symbol, "token": self.api_key}
        
        try:
            async with self.session.get(url, params=params) as response:
                data = await response.json()
                return {
                    "symbol": symbol,
                    "price": data.get("c", 0),  # Current price
                    "change": data.get("d", 0),
                    "change_percent": data.get("dp", 0),
                    "high": data.get("h", 0),
                    "low": data.get("l", 0),
                    "open": data.get("o", 0),
                    "previous_close": data.get("pc", 0),
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            print(f"Error fetching Finnhub quote for {symbol}: {e}")
            return None
    
    async def get_company_profile(self, symbol: str) -> Optional[Dict]:
        """Get company profile"""
        url = f"{self.BASE_URL}/stock/profile2"
        params = {"symbol": symbol, "token": self.api_key}
        
        try:
            async with self.session.get(url, params=params) as response:
                return await response.json()
        except Exception as e:
            print(f"Error fetching profile for {symbol}: {e}")
            return None

class PolygonConnector:
    """Polygon.io API for real-time quotes and options data"""
    
    BASE_URL = "https://api.polygon.io/v2"
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.session = None
    
    async def connect(self):
        self.session = aiohttp.ClientSession()
    
    async def close(self):
        if self.session:
            await self.session.close()
    
    async def get_quote(self, symbol: str) -> Optional[Dict]:
        """Get last trade quote"""
        url = f"{self.BASE_URL}/last/trade/{symbol}"
        params = {"apiKey": self.api_key}
        
        try:
            async with self.session.get(url, params=params) as response:
                data = await response.json()
                result = data.get("results", {})
                return {
                    "symbol": symbol,
                    "price": result.get("p", 0),  # Price
                    "size": result.get("s", 0),   # Size
                    "timestamp": result.get("t", ""),
                    "exchange": result.get("x", "")
                }
        except Exception as e:
            print(f"Error fetching Polygon quote for {symbol}: {e}")
            return None
    
    async def get_options_chain(self, symbol: str) -> List[Dict]:
        """Get options chain (requires paid subscription)"""
        url = f"https://api.polygon.io/v3/reference/options/contracts"
        params = {
            "underlying_ticker": symbol,
            "apiKey": self.api_key
        }
        
        try:
            async with self.session.get(url, params=params) as response:
                data = await response.json()
                return data.get("results", [])
        except Exception as e:
            print(f"Error fetching options for {symbol}: {e}")
            return []

class UnusualWhalesConnector:
    """Unusual Whales API for options flow"""
    
    BASE_URL = "https://api.unusualwhales.com/api"
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.session = None
    
    async def connect(self):
        self.session = aiohttp.ClientSession(
            headers={"Authorization": f"Bearer {self.api_key}"}
        )
    
    async def close(self):
        if self.session:
            await self.session.close()
    
    async def get_flow(self, symbol: str) -> List[Dict]:
        """Get recent options flow for symbol"""
        url = f"{self.BASE_URL}/stock/{symbol}/option-trades"
        
        try:
            async with self.session.get(url) as response:
                data = await response.json()
                return data.get("data", [])
        except Exception as e:
            print(f"Error fetching flow for {symbol}: {e}")
            return []
    
    async def get_unusual_flow(self, min_premium: int = 100000) -> List[Dict]:
        """Get unusual options flow across market"""
        url = f"{self.BASE_URL}/flow"
        params = {"min_premium": min_premium}
        
        try:
            async with self.session.get(url, params=params) as response:
                data = await response.json()
                return data.get("data", [])
        except Exception as e:
            print(f"Error fetching unusual flow: {e}")
            return []

class YahooFinanceScraper:
    """Scrape free data from Yahoo Finance (fallback)"""
    
    async def get_quote(self, symbol: str) -> Optional[Dict]:
        """Get quote from Yahoo Finance"""
        import yfinance as yf
        
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            hist = ticker.history(period="1d")
            
            if hist.empty:
                return None
            
            latest = hist.iloc[-1]
            
            return {
                "symbol": symbol,
                "price": latest["Close"],
                "open": latest["Open"],
                "high": latest["High"],
                "low": latest["Low"],
                "volume": int(latest["Volume"]),
                "change": latest["Close"] - latest["Open"],
                "change_percent": ((latest["Close"] - latest["Open"]) / latest["Open"]) * 100,
                "timestamp": datetime.now().isoformat(),
                "market_cap": info.get("marketCap"),
                "pe_ratio": info.get("trailingPE"),
                "short_ratio": info.get("shortRatio"),
                "float_shares": info.get("floatShares"),
                "shares_short": info.get("sharesShort"),
                "short_percent_float": info.get("shortPercentOfFloat")
            }
        except Exception as e:
            print(f"Error fetching Yahoo data for {symbol}: {e}")
            return None
    
    async def get_options_chain(self, symbol: str) -> Dict:
        """Get options chain from Yahoo"""
        import yfinance as yf
        
        try:
            ticker = yf.Ticker(symbol)
            # Get next expiration
            expirations = ticker.options
            if not expirations:
                return {}
            
            chain = ticker.option_chain(expirations[0])
            
            return {
                "expiration": expirations[0],
                "calls": chain.calls.to_dict('records'),
                "puts": chain.puts.to_dict('records')
            }
        except Exception as e:
            print(f"Error fetching options for {symbol}: {e}")
            return {}

class RealDataManager:
    """Manager class that orchestrates all data sources"""
    
    def __init__(self):
        self.config = DataConfig()
        self.connectors = {}
        
        # Initialize available connectors
        if self.config.ALPHA_VANTAGE_KEY:
            self.connectors["alpha_vantage"] = AlphaVantageConnector(self.config.ALPHA_VANTAGE_KEY)
        if self.config.FINNHUB_KEY:
            self.connectors["finnhub"] = FinnhubConnector(self.config.FINNHUB_KEY)
        if self.config.POLYGON_KEY:
            self.connectors["polygon"] = PolygonConnector(self.config.POLYGON_KEY)
        if self.config.UNUSUAL_WHALES_KEY:
            self.connectors["unusual_whales"] = UnusualWhalesConnector(self.config.UNUSUAL_WHALES_KEY)
        
        # Always have Yahoo as fallback
        self.connectors["yahoo"] = YahooFinanceScraper()
    
    async def connect_all(self):
        """Connect to all available APIs"""
        tasks = []
        for name, connector in self.connectors.items():
            if hasattr(connector, 'connect'):
                tasks.append(connector.connect())
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def close_all(self):
        """Close all connections"""
        tasks = []
        for name, connector in self.connectors.items():
            if hasattr(connector, 'close'):
                tasks.append(connector.close())
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def get_best_quote(self, symbol: str) -> Optional[Dict]:
        """Get best available quote from any source"""
        
        # Try Polygon first (fastest real-time)
        if "polygon" in self.connectors:
            quote = await self.connectors["polygon"].get_quote(symbol)
            if quote and quote.get("price"):
                return {**quote, "source": "polygon"}
        
        # Try Finnhub
        if "finnhub" in self.connectors:
            quote = await self.connectors["finnhub"].get_quote(symbol)
            if quote and quote.get("price"):
                return {**quote, "source": "finnhub"}
        
        # Try Alpha Vantage
        if "alpha_vantage" in self.connectors:
            quote = await self.connectors["alpha_vantage"].get_quote(symbol)
            if quote and quote.get("price"):
                return {**quote, "source": "alpha_vantage"}
        
        # Fallback to Yahoo
        quote = await self.connectors["yahoo"].get_quote(symbol)
        if quote:
            return {**quote, "source": "yahoo"}
        
        return None
    
    async def get_earnings_data(self, symbol: str) -> List[Dict]:
        """Get earnings data from best available source"""
        
        # Try Finnhub first (most reliable for earnings)
        if "finnhub" in self.connectors:
            earnings = await self.connectors["finnhub"].get_earnings_calendar(symbol)
            if earnings:
                return [{**e, "source": "finnhub"} for e in earnings]
        
        # Try Alpha Vantage
        if "alpha_vantage" in self.connectors:
            data = await self.connectors["alpha_vantage"].get_earnings_calendar(symbol)
            if data:
                return [{**data, "source": "alpha_vantage"}]
        
        return []
    
    async def get_unusual_flow(self, symbol: str) -> List[Dict]:
        """Get unusual options flow"""
        
        if "unusual_whales" in self.connectors:
            flow = await self.connectors["unusual_whales"].get_flow(symbol)
            if flow:
                return [{**f, "source": "unusual_whales"} for f in flow]
        
        # Fallback: try to detect from Yahoo options data
        return await self._detect_flow_from_yahoo(symbol)
    
    async def _detect_flow_from_yahoo(self, symbol: str) -> List[Dict]:
        """Detect unusual flow using Yahoo options data"""
        chain = await self.connectors["yahoo"].get_options_chain(symbol)
        
        if not chain:
            return []
        
        flow_signals = []
        
        # Look for unusual volume in options
        for option_type in ["calls", "puts"]:
            options = chain.get(option_type, [])
            for opt in options:
                volume = opt.get("volume", 0)
                oi = opt.get("openInterest", 1)
                
                # Unusual if volume > 2x OI (and OI > 0 to avoid div by zero)
                if oi > 0 and volume > oi * 2 and volume > 100:
                    flow_signals.append({
                        "strike": opt.get("strike"),
                        "type": option_type[:-1],  # 'call' or 'put'
                        "volume": volume,
                        "oi": oi,
                        "volume_ratio": round(volume / oi, 1),
                        "source": "yahoo_volume_scan",
                        "premium": opt.get("lastPrice", 0) * volume * 100
                    })
        
        return sorted(flow_signals, key=lambda x: x["volume_ratio"], reverse=True)[:5]
    
    async def get_short_interest(self, symbol: str) -> Optional[Dict]:
        """Get short interest data"""
        
        # Yahoo has short interest in company info
        quote = await self.connectors["yahoo"].get_quote(symbol)
        
        if quote and quote.get("short_percent_float"):
            return {
                "symbol": symbol,
                "short_percent_float": quote["short_percent_float"],
                "shares_short": quote.get("shares_short"),
                "float_shares": quote.get("float_shares"),
                "short_ratio": quote.get("short_ratio"),
                "source": "yahoo"
            }
        
        return None
    
    async def batch_quotes(self, symbols: List[str]) -> Dict[str, Dict]:
        """Get quotes for multiple symbols"""
        tasks = [self.get_best_quote(sym) for sym in symbols]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        quotes = {}
        for symbol, result in zip(symbols, results):
            if isinstance(result, Exception):
                print(f"Error fetching {symbol}: {result}")
            elif result:
                quotes[symbol] = result
        
        return quotes

def setup_instructions():
    """Print setup instructions for user"""
    print("""
╔════════════════════════════════════════════════════════════╗
║  REAL DATA API SETUP                                       ║
╚════════════════════════════════════════════════════════════╝

To get real market data, you need API keys from these providers:

🥇 RECOMMENDED (Free Tiers Available):

1. FINNHUB (Free: 60 calls/minute)
   Website: https://finnhub.io
   Get Key: Sign up → Dashboard → API Key
   Export: export FINNHUB_API_KEY="your_key"

2. ALPHA VANTAGE (Free: 25 calls/day)
   Website: https://www.alphavantage.co
   Get Key: Sign up → Support → API Key
   Export: export ALPHA_VANTAGE_API_KEY="your_key"

🥈 PREMIUM (Better real-time data):

3. POLYGON (Free trial, then $49/month)
   Website: https://polygon.io
   Best for: Real-time quotes, options chains

4. UNUSUAL WHALES (Premium flow data)
   Website: https://unusualwhales.com
   Best for: Options flow, dark pool prints

🥉 FALLBACK (Always works, slightly delayed):

YAHOO FINANCE (Free, no key needed)
   - Used automatically if no APIs configured
   - 15-20 min delayed quotes
   - Includes short interest data

════════════════════════════════════════════════════════════

QUICK SETUP:

1. Get Finnhub API key (free, takes 2 minutes)
2. Add to your shell profile (~/.zshrc or ~/.bashrc):

   export FINNHUB_API_KEY="your_actual_key_here"

3. Reload: source ~/.zshrc
4. Test: python3 real_data_test.py

════════════════════════════════════════════════════════════
""")

# Test function
async def test_data_connections():
    """Test all data connections"""
    print("Testing Real Data Connections...\n")
    
    manager = RealDataManager()
    manager.config.print_status()
    
    if not manager.config.is_configured():
        setup_instructions()
        return
    
    await manager.connect_all()
    
    # Test with a few symbols
    test_symbols = ["AAPL", "TSLA", "AMC", "GME"]
    
    print(f"\nFetching quotes for: {', '.join(test_symbols)}\n")
    
    quotes = await manager.batch_quotes(test_symbols)
    
    for symbol, quote in quotes.items():
        print(f"✅ {symbol}: ${quote['price']:.2f} (via {quote['source']})")
        
        # Get additional data
        earnings = await manager.get_earnings_data(symbol)
        if earnings:
            print(f"   📅 Earnings: {len(earnings)} events found")
        
        short = await manager.get_short_interest(symbol)
        if short:
            print(f"   🩳 Short: {short['short_percent_float']*100:.1f}% of float")
    
    await manager.close_all()
    
    print("\n✅ Data connections test complete!")

if __name__ == "__main__":
    asyncio.run(test_data_connections())
