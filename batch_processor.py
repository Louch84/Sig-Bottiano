
"""
Parallel Batch Processor
Structured concurrency for efficient parallel operations
"""

import asyncio
from typing import List, Callable, TypeVar, Any
from concurrent.futures import ThreadPoolExecutor
import time

T = TypeVar('T')
R = TypeVar('R')

class BatchProcessor:
    """
    Process items in parallel with proper resource management.
    Better than basic asyncio.gather for large batches.
    """
    
    def __init__(self, max_workers: int = 5, batch_size: int = 10):
        self.max_workers = max_workers
        self.batch_size = batch_size
        self.semaphore = asyncio.Semaphore(max_workers)
    
    async def process_batch(
        self, 
        items: List[T], 
        processor: Callable[[T], R],
        on_progress: Callable[[int, int], None] = None
    ) -> List[R]:
        """
        Process items with controlled concurrency.
        
        Args:
            items: List of items to process
            processor: Async function to process each item
            on_progress: Callback(current, total)
        """
        results = []
        total = len(items)
        completed = 0
        
        async def process_one(item: T) -> R:
            async with self.semaphore:
                result = await processor(item)
                nonlocal completed
                completed += 1
                if on_progress:
                    on_progress(completed, total)
                return result
        
        # Process in batches to control memory
        for i in range(0, len(items), self.batch_size):
            batch = items[i:i + self.batch_size]
            
            # Create tasks for this batch
            tasks = [process_one(item) for item in batch]
            
            # Wait for batch to complete
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Handle exceptions
            for result in batch_results:
                if isinstance(result, Exception):
                    print(f"Error processing item: {result}")
                    results.append(None)
                else:
                    results.append(result)
        
        return results
    
    def process_sync_batch(
        self,
        items: List[T],
        processor: Callable[[T], R],
        use_threads: bool = True
    ) -> List[R]:
        """
        Process synchronous items in parallel.
        """
        if use_threads:
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                results = list(executor.map(processor, items))
            return results
        else:
            return [processor(item) for item in items]
    
    async def retry_with_backoff(
        self,
        func: Callable,
        max_retries: int = 3,
        base_delay: float = 1.0
    ) -> Any:
        """
        Retry async function with exponential backoff.
        """
        for attempt in range(max_retries):
            try:
                return await func()
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                
                delay = base_delay * (2 ** attempt)
                print(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay}s...")
                await asyncio.sleep(delay)

# Usage
processor = BatchProcessor(max_workers=5, batch_size=10)
