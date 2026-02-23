"""
Parallel Processing Optimizations
Uses asyncio for maximum efficiency
Free performance gains
"""

import asyncio
import time
from typing import List, Callable, TypeVar, Any, Optional
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import functools

T = TypeVar('T')
R = TypeVar('R')

class ParallelOptimizer:
    """
    Optimized parallel processing for trading operations
    All free, uses Python's built-in capabilities
    """
    
    def __init__(self, max_workers: int = 10):
        self.max_workers = max_workers
        self.semaphore = asyncio.Semaphore(max_workers)
        self.thread_pool = ThreadPoolExecutor(max_workers=max_workers)
    
    async def parallel_map(
        self,
        func: Callable[[T], R],
        items: List[T],
        use_threads: bool = False
    ) -> List[R]:
        """
        Map function over items in parallel
        
        Args:
            func: Function to apply
            items: List of items
            use_threads: True for CPU-bound, False for IO-bound
        """
        if not items:
            return []
        
        if use_threads:
            # Use thread pool for CPU-bound tasks
            loop = asyncio.get_event_loop()
            tasks = [
                loop.run_in_executor(self.thread_pool, func, item)
                for item in items
            ]
            return await asyncio.gather(*tasks)
        else:
            # Use asyncio for IO-bound tasks
            tasks = [self._bounded_task(func, item) for item in items]
            return await asyncio.gather(*tasks)
    
    async def _bounded_task(self, func: Callable[[T], R], item: T) -> R:
        """Execute task with semaphore control"""
        async with self.semaphore:
            if asyncio.iscoroutinefunction(func):
                return await func(item)
            else:
                return func(item)
    
    async def parallel_fetch(
        self,
        urls: List[str],
        fetch_func: Callable[[str], Any],
        timeout: float = 10.0
    ) -> List[Any]:
        """
        Fetch multiple URLs in parallel
        
        Args:
            urls: List of URLs to fetch
            fetch_func: Async function to fetch single URL
            timeout: Max time per fetch
        """
        async def fetch_with_timeout(url: str) -> Any:
            try:
                return await asyncio.wait_for(
                    fetch_func(url),
                    timeout=timeout
                )
            except asyncio.TimeoutError:
                return {'error': f'Timeout fetching {url}'}
            except Exception as e:
                return {'error': str(e)}
        
        tasks = [fetch_with_timeout(url) for url in urls]
        return await asyncio.gather(*tasks, return_exceptions=True)
    
    def batch_process(
        self,
        items: List[T],
        func: Callable[[T], R],
        batch_size: int = 100
    ) -> List[R]:
        """
        Process items in batches to control memory
        
        Args:
            items: Large list of items
            func: Processing function
            batch_size: Items per batch
        """
        results = []
        
        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]
            batch_results = [func(item) for item in batch]
            results.extend(batch_results)
        
        return results
    
    async def pipeline_process(
        self,
        items: List[T],
        stages: List[Callable[[Any], Any]]
    ) -> List[Any]:
        """
        Process items through pipeline of stages
        
        Args:
            items: Input items
            stages: List of processing functions
        """
        current = items
        
        for stage in stages:
            # Process current batch through stage
            if asyncio.iscoroutinefunction(stage):
                tasks = [stage(item) for item in current]
                current = await asyncio.gather(*tasks)
            else:
                current = [stage(item) for item in current]
        
        return current
    
    @staticmethod
    def memoize_async(func: Callable) -> Callable:
        """
        Memoization decorator for async functions
        Caches results to avoid redundant computation
        """
        cache = {}
        
        @functools.wraps(func)
        async def wrapper(*args):
            # Create cache key from args
            key = str(args)
            
            if key not in cache:
                cache[key] = await func(*args)
            
            return cache[key]
        
        return wrapper
    
    @staticmethod
    def timed_execution(func: Callable) -> Callable:
        """
        Decorator to time function execution
        Helps identify bottlenecks
        """
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            start = time.time()
            result = await func(*args, **kwargs)
            elapsed = time.time() - start
            print(f"⏱️  {func.__name__}: {elapsed:.2f}s")
            return result
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            start = time.time()
            result = func(*args, **kwargs)
            elapsed = time.time() - start
            print(f"⏱️  {func.__name__}: {elapsed:.2f}s")
            return result
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper


class RateLimiter:
    """
    Rate limiting for API calls
    Prevents hitting rate limits, saves costs
    """
    
    def __init__(self, calls_per_second: float = 1.0):
        self.min_interval = 1.0 / calls_per_second
        self.last_call = 0
        self.lock = asyncio.Lock()
    
    async def acquire(self):
        """Wait if necessary to maintain rate limit"""
        async with self.lock:
            now = time.time()
            elapsed = now - self.last_call
            
            if elapsed < self.min_interval:
                wait_time = self.min_interval - elapsed
                await asyncio.sleep(wait_time)
            
            self.last_call = time.time()


class ConnectionPool:
    """
    Reuse HTTP connections for better performance
    """
    
    def __init__(self, max_connections: int = 20):
        self.max_connections = max_connections
        self.session = None
    
    async def get_session(self):
        """Get or create aiohttp session"""
        if self.session is None:
            import aiohttp
            connector = aiohttp.TCPConnector(limit=self.max_connections)
            self.session = aiohttp.ClientSession(connector=connector)
        return self.session
    
    async def close(self):
        """Close all connections"""
        if self.session:
            await self.session.close()
            self.session = None


# Trading-specific optimizations
class TradingParallelizer:
    """
    Optimized parallel processing for trading operations
    """
    
    def __init__(self):
        self.optimizer = ParallelOptimizer(max_workers=20)
        self.rate_limiter = RateLimiter(calls_per_second=2.0)  # 2 API calls/sec
        self.connection_pool = ConnectionPool(max_connections=20)
    
    async def fetch_stock_data_parallel(
        self,
        symbols: List[str],
        fetch_func: Callable[[str], dict]
    ) -> List[dict]:
        """
        Fetch data for multiple stocks in parallel
        With rate limiting to respect API limits
        """
        async def fetch_with_limit(symbol: str) -> dict:
            await self.rate_limiter.acquire()
            return await fetch_func(symbol)
        
        return await self.optimizer.parallel_map(fetch_with_limit, symbols)
    
    async def analyze_signals_parallel(
        self,
        signals: List[dict],
        analyze_func: Callable[[dict], dict]
    ) -> List[dict]:
        """
        Analyze multiple signals in parallel
        """
        return await self.optimizer.parallel_map(analyze_func, signals)
    
    def batch_backtest(
        self,
        strategies: List[dict],
        historical_data: dict,
        backtest_func: Callable
    ) -> List[dict]:
        """
        Run backtests in batches
        """
        return self.optimizer.batch_process(
            strategies,
            lambda s: backtest_func(s, historical_data),
            batch_size=10
        )


# Global instance
trading_parallelizer = TradingParallelizer()

# Example usage
async def demo():
    """Demonstrate parallel processing"""
    print("="*70)
    print("⚡ PARALLEL PROCESSING DEMO")
    print("="*70)
    print()
    
    optimizer = ParallelOptimizer(max_workers=5)
    
    # Simulate fetching stock data
    symbols = ["AAPL", "TSLA", "AMC", "GME", "NVDA"]
    
    async def fetch_stock(symbol: str) -> dict:
        # Simulate API call
        await asyncio.sleep(0.5)  # 500ms delay
        return {
            'symbol': symbol,
            'price': 100 + hash(symbol) % 100,
            'fetched': True
        }
    
    print(f"Fetching {len(symbols)} stocks...")
    start = time.time()
    
    results = await optimizer.parallel_map(fetch_stock, symbols)
    
    elapsed = time.time() - start
    print(f"✅ Fetched {len(results)} stocks in {elapsed:.2f}s")
    print(f"   Sequential would take: ~{len(symbols) * 0.5:.1f}s")
    print(f"   Speedup: {len(symbols) * 0.5 / elapsed:.1f}x")
    
    for r in results:
        print(f"   {r['symbol']}: ${r['price']}")

if __name__ == "__main__":
    asyncio.run(demo())
