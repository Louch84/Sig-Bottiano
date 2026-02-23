"""
Browser Automation System
Free implementation using Playwright
Control web browsers programmatically for trading
"""

import asyncio
from typing import Optional, Dict, List, Any
from dataclasses import dataclass
from datetime import datetime
import json

@dataclass
class BrowserAction:
    """Represents a browser action"""
    action: str  # click, type, screenshot, navigate, etc.
    selector: Optional[str] = None
    text: Optional[str] = None
    url: Optional[str] = None
    description: str = ""

class BrowserAutomation:
    """
    Browser automation for web-based trading
    Uses Playwright (free, open source)
    """
    
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.browser = None
        self.context = None
        self.page = None
        self.playwright = None
    
    async def start(self):
        """Start browser instance"""
        try:
            from playwright.async_api import async_playwright
            
            self.playwright = await async_playwright().start()
            
            # Launch browser
            self.browser = await self.playwright.chromium.launch(
                headless=self.headless,
                args=['--disable-blink-features=AutomationControlled']
            )
            
            # Create context with realistic viewport
            self.context = await self.browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
            
            # Create page
            self.page = await self.context.new_page()
            
            print("✅ Browser started")
            return True
            
        except ImportError:
            print("❌ Playwright not installed")
            print("   Install: pip install playwright && playwright install chromium")
            return False
        except Exception as e:
            print(f"❌ Failed to start browser: {e}")
            return False
    
    async def navigate(self, url: str, wait_for: str = None):
        """Navigate to URL"""
        if not self.page:
            print("❌ Browser not started")
            return False
        
        try:
            await self.page.goto(url, wait_until='networkidle')
            
            if wait_for:
                await self.page.wait_for_selector(wait_for, timeout=10000)
            
            print(f"✅ Navigated to {url}")
            return True
            
        except Exception as e:
            print(f"❌ Navigation failed: {e}")
            return False
    
    async def click(self, selector: str, description: str = ""):
        """Click element"""
        try:
            await self.page.click(selector)
            print(f"✅ Clicked: {description or selector}")
            return True
        except Exception as e:
            print(f"❌ Click failed: {e}")
            return False
    
    async def type(self, selector: str, text: str, description: str = ""):
        """Type text into input"""
        try:
            await self.page.fill(selector, text)
            print(f"✅ Typed '{text}' into: {description or selector}")
            return True
        except Exception as e:
            print(f"❌ Type failed: {e}")
            return False
    
    async def screenshot(self, path: str = None) -> Optional[bytes]:
        """Take screenshot"""
        try:
            if path:
                await self.page.screenshot(path=path, full_page=True)
                print(f"✅ Screenshot saved: {path}")
                return None
            else:
                return await self.page.screenshot()
        except Exception as e:
            print(f"❌ Screenshot failed: {e}")
            return None
    
    async def get_text(self, selector: str) -> str:
        """Get text content of element"""
        try:
            element = await self.page.query_selector(selector)
            if element:
                return await element.inner_text()
            return ""
        except:
            return ""
    
    async def wait_for_element(self, selector: str, timeout: int = 10000):
        """Wait for element to appear"""
        try:
            await self.page.wait_for_selector(selector, timeout=timeout)
            return True
        except:
            return False
    
    async def execute_sequence(self, actions: List[BrowserAction]) -> List[bool]:
        """Execute a sequence of browser actions"""
        results = []
        
        for action in actions:
            if action.action == "navigate":
                result = await self.navigate(action.url)
            elif action.action == "click":
                result = await self.click(action.selector, action.description)
            elif action.action == "type":
                result = await self.type(action.selector, action.text, action.description)
            elif action.action == "screenshot":
                result = await self.screenshot(action.text) is not None
            elif action.action == "wait":
                result = await self.wait_for_element(action.selector)
            else:
                result = False
            
            results.append(result)
            
            # Small delay between actions
            await asyncio.sleep(0.5)
        
        return results
    
    async def close(self):
        """Close browser"""
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        print("✅ Browser closed")


class TradingPlatformController:
    """
    Specific controller for trading platforms
    Abstracts common trading operations
    """
    
    def __init__(self, browser: BrowserAutomation):
        self.browser = browser
    
    async def login_webull(self, username: str, password: str):
        """Login to Webull (example)"""
        actions = [
            BrowserAction("navigate", url="https://app.webull.com", description="Open Webull"),
            BrowserAction("wait", selector="[data-testid='login-button']", description="Wait for login"),
            BrowserAction("click", selector="[data-testid='login-button']", description="Click login"),
            BrowserAction("type", selector="input[name='username']", text=username, description="Enter username"),
            BrowserAction("type", selector="input[name='password']", text=password, description="Enter password"),
            BrowserAction("click", selector="button[type='submit']", description="Submit login"),
            BrowserAction("wait", selector="[data-testid='portfolio']", description="Wait for portfolio"),
        ]
        
        return await self.browser.execute_sequence(actions)
    
    async def check_position(self, symbol: str) -> Dict:
        """Check current position for symbol"""
        # Navigate to positions
        await self.browser.navigate("https://app.webull.com/trade")
        
        # Search for symbol
        await self.browser.type("input[placeholder='Search']", symbol)
        await asyncio.sleep(1)
        
        # Get position info
        position_text = await self.browser.get_text(".position-row")
        
        return {
            'symbol': symbol,
            'raw_text': position_text,
            'timestamp': datetime.now().isoformat()
        }
    
    async def place_option_order(
        self,
        symbol: str,
        option_type: str,  # CALL or PUT
        strike: float,
        expiration: str,
        action: str,  # BUY or SELL
        quantity: int,
        order_type: str = "MARKET"
    ) -> bool:
        """
        Place option order
        
        ⚠️ WARNING: This is for demonstration. Test thoroughly before using real money.
        """
        actions = [
            BrowserAction("navigate", url=f"https://app.webull.com/trade/options/{symbol}"),
            BrowserAction("wait", selector=".option-chain", description="Wait for options"),
            
            # Select expiration
            BrowserAction("click", selector=f"[data-expiration='{expiration}']", description=f"Select {expiration}"),
            
            # Select strike
            BrowserAction("click", selector=f"[data-strike='{strike}']", description=f"Select ${strike}"),
            
            # Select direction
            BrowserAction("click", selector=f"[data-type='{option_type.lower()}']", description=f"Select {option_type}"),
            
            # Enter quantity
            BrowserAction("type", selector="input[name='quantity']", text=str(quantity), description="Enter quantity"),
            
            # Review order
            BrowserAction("click", selector="[data-testid='review-order']", description="Review order"),
            
            # Screenshot for confirmation
            BrowserAction("screenshot", text=f"/tmp/order_{symbol}_{datetime.now().strftime('%H%M%S')}.png"),
        ]
        
        results = await self.browser.execute_sequence(actions)
        return all(results)


class MarketDataScraper:
    """
    Scrape market data from free web sources
    """
    
    def __init__(self, browser: BrowserAutomation):
        self.browser = browser
    
    async def get_unusual_volume(self) -> List[Dict]:
        """Scrape unusual volume from Finviz (free)"""
        await self.browser.navigate("https://finviz.com/screener.ashx?v=111&s=ta_unusualvolume")
        await asyncio.sleep(2)
        
        # Get table data
        rows = await self.browser.page.query_selector_all(".screener-table tr")
        
        stocks = []
        for row in rows[1:11]:  # Skip header, get top 10
            cells = await row.query_selector_all("td")
            if len(cells) >= 2:
                symbol = await cells[1].inner_text()
                stocks.append({'symbol': symbol.strip()})
        
        return stocks
    
    async def get_short_interest(self, symbol: str) -> Dict:
        """Scrape short interest from ShortSqueeze (free)"""
        await self.browser.navigate(f"https://shortsqueeze.com/?symbol={symbol}")
        await asyncio.sleep(2)
        
        # Extract short interest data
        text = await self.browser.get_text("body")
        
        # Parse short interest from text
        import re
        short_match = re.search(r'Short Interest[\s:]+([\d,]+)', text)
        float_match = re.search(r'Float[\s:]+([\d,]+)', text)
        
        return {
            'symbol': symbol,
            'short_interest': short_match.group(1) if short_match else 'N/A',
            'float': float_match.group(1) if float_match else 'N/A'
        }


# Demo
async def demo():
    """Demonstrate browser automation"""
    print("="*60)
    print("🌐 BROWSER AUTOMATION DEMO")
    print("="*60)
    print()
    
    browser = BrowserAutomation(headless=True)
    
    if await browser.start():
        # Example: Navigate to Yahoo Finance
        await browser.navigate("https://finance.yahoo.com/quote/AMC")
        
        # Take screenshot
        await browser.screenshot("/tmp/amc_yahoo.png")
        
        # Get price
        price = await browser.get_text("[data-symbol='AMC'] [data-field='regularMarketPrice']")
        print(f"AMC Price from Yahoo: {price}")
        
        # Close
        await browser.close()
        
        print("\n✅ Demo complete")
        print("📸 Screenshot saved: /tmp/amc_yahoo.png")
    else:
        print("\n❌ Install Playwright to use browser automation:")
        print("   pip install playwright")
        print("   playwright install chromium")

if __name__ == "__main__":
    asyncio.run(demo())
