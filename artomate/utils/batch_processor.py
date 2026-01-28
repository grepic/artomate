"""Batch processing system for efficient job execution."""

import asyncio
from typing import List, Callable, Any, Optional, TypeVar, Generic
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime

from loguru import logger

from artomate.utils.monitoring import MetricsCollector, Timer


T = TypeVar('T')
R = TypeVar('R')


@dataclass
class BatchResult(Generic[T, R]):
    """Result of batch processing."""
    successful: List[tuple[T, R]]
    failed: List[tuple[T, Exception]]
    total_count: int
    success_count: int
    failure_count: int
    duration_seconds: float
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate."""
        if self.total_count == 0:
            return 0.0
        return (self.success_count / self.total_count) * 100


class BatchProcessor:
    """Process items in batches with concurrency control."""
    
    def __init__(
        self,
        max_workers: int = 5,
        batch_size: int = 10,
        continue_on_error: bool = True
    ):
        """
        Initialize batch processor.
        
        Args:
            max_workers: Maximum concurrent workers
            batch_size: Number of items per batch
            continue_on_error: Continue processing if an item fails
        """
        self.max_workers = max_workers
        self.batch_size = batch_size
        self.continue_on_error = continue_on_error
    
    def process_batch(
        self,
        items: List[T],
        process_func: Callable[[T], R],
        context: Optional[str] = None
    ) -> BatchResult[T, R]:
        """
        Process a batch of items with threading.
        
        Args:
            items: List of items to process
            process_func: Function to process each item
            context: Context name for logging/metrics
            
        Returns:
            BatchResult with processing results
        """
        start_time = datetime.utcnow()
        successful = []
        failed = []
        
        ctx_name = context or process_func.__name__
        
        logger.info(
            f"Starting batch processing: {ctx_name}",
            item_count=len(items),
            max_workers=self.max_workers
        )
        
        with Timer(f"batch_process.{ctx_name}"):
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                # Submit all tasks
                future_to_item = {
                    executor.submit(process_func, item): item
                    for item in items
                }
                
                # Process results as they complete
                for future in as_completed(future_to_item):
                    item = future_to_item[future]
                    try:
                        result = future.result()
                        successful.append((item, result))
                        
                        metrics = MetricsCollector()
                        metrics.increment_counter(
                            f"batch.{ctx_name}.success",
                            tags={"status": "success"}
                        )
                        
                    except Exception as e:
                        failed.append((item, e))
                        logger.error(
                            f"Batch item failed: {ctx_name}",
                            item=str(item)[:100],
                            error=str(e)
                        )
                        
                        metrics = MetricsCollector()
                        metrics.increment_counter(
                            f"batch.{ctx_name}.failed",
                            tags={"status": "failed"}
                        )
                        
                        if not self.continue_on_error:
                            raise
        
        duration = (datetime.utcnow() - start_time).total_seconds()
        
        result = BatchResult(
            successful=successful,
            failed=failed,
            total_count=len(items),
            success_count=len(successful),
            failure_count=len(failed),
            duration_seconds=duration
        )
        
        logger.info(
            f"Batch processing completed: {ctx_name}",
            total=result.total_count,
            successful=result.success_count,
            failed=result.failure_count,
            success_rate=f"{result.success_rate:.1f}%",
            duration_seconds=duration
        )
        
        return result
    
    async def process_batch_async(
        self,
        items: List[T],
        process_func: Callable[[T], Any],
        context: Optional[str] = None
    ) -> BatchResult[T, R]:
        """
        Process a batch of items asynchronously.
        
        Args:
            items: List of items to process
            process_func: Async function to process each item
            context: Context name for logging/metrics
            
        Returns:
            BatchResult with processing results
        """
        start_time = datetime.utcnow()
        successful = []
        failed = []
        
        ctx_name = context or process_func.__name__
        
        logger.info(
            f"Starting async batch processing: {ctx_name}",
            item_count=len(items)
        )
        
        # Create tasks
        tasks = [process_func(item) for item in items]
        
        # Process with semaphore for concurrency control
        semaphore = asyncio.Semaphore(self.max_workers)
        
        async def process_with_semaphore(item, coro):
            async with semaphore:
                try:
                    result = await coro
                    return item, result, None
                except Exception as e:
                    return item, None, e
        
        # Execute all tasks
        results = await asyncio.gather(
            *[process_with_semaphore(item, task) for item, task in zip(items, tasks)],
            return_exceptions=False
        )
        
        # Separate successful and failed
        for item, result, error in results:
            if error is None:
                successful.append((item, result))
            else:
                failed.append((item, error))
                logger.error(
                    f"Async batch item failed: {ctx_name}",
                    item=str(item)[:100],
                    error=str(error)
                )
        
        duration = (datetime.utcnow() - start_time).total_seconds()
        
        result = BatchResult(
            successful=successful,
            failed=failed,
            total_count=len(items),
            success_count=len(successful),
            failure_count=len(failed),
            duration_seconds=duration
        )
        
        logger.info(
            f"Async batch processing completed: {ctx_name}",
            total=result.total_count,
            successful=result.success_count,
            failed=result.failure_count,
            success_rate=f"{result.success_rate:.1f}%",
            duration_seconds=duration
        )
        
        return result
    
    def process_in_chunks(
        self,
        items: List[T],
        process_func: Callable[[T], R],
        context: Optional[str] = None
    ) -> List[BatchResult[T, R]]:
        """
        Process items in smaller chunks.
        
        Args:
            items: List of items to process
            process_func: Function to process each item
            context: Context name for logging/metrics
            
        Returns:
            List of BatchResult for each chunk
        """
        results = []
        
        # Split into chunks
        for i in range(0, len(items), self.batch_size):
            chunk = items[i:i + self.batch_size]
            logger.info(
                f"Processing chunk {i // self.batch_size + 1}",
                chunk_size=len(chunk)
            )
            
            result = self.process_batch(chunk, process_func, context)
            results.append(result)
        
        return results


class JobQueue:
    """Simple in-memory job queue for batch processing."""
    
    def __init__(self, max_size: int = 1000):
        """
        Initialize job queue.
        
        Args:
            max_size: Maximum queue size
        """
        self.queue = asyncio.Queue(maxsize=max_size)
        self.results = {}
        self._processing = False
    
    async def add_job(self, job_id: str, job_data: Any):
        """Add job to queue."""
        await self.queue.put((job_id, job_data))
        logger.debug(f"Job added to queue: {job_id}")
    
    async def process_queue(
        self,
        process_func: Callable,
        workers: int = 5
    ):
        """
        Process jobs from queue with multiple workers.
        
        Args:
            process_func: Function to process each job
            workers: Number of worker coroutines
        """
        self._processing = True
        
        async def worker(worker_id: int):
            logger.info(f"Worker {worker_id} started")
            
            while self._processing:
                try:
                    # Get job with timeout
                    job_id, job_data = await asyncio.wait_for(
                        self.queue.get(),
                        timeout=1.0
                    )
                    
                    try:
                        logger.debug(
                            f"Worker {worker_id} processing job {job_id}"
                        )
                        result = await process_func(job_data)
                        self.results[job_id] = {
                            "status": "success",
                            "result": result
                        }
                    except Exception as e:
                        logger.error(
                            f"Job {job_id} failed",
                            error=str(e),
                            exc_info=True
                        )
                        self.results[job_id] = {
                            "status": "failed",
                            "error": str(e)
                        }
                    finally:
                        self.queue.task_done()
                        
                except asyncio.TimeoutError:
                    continue
            
            logger.info(f"Worker {worker_id} stopped")
        
        # Start workers
        workers_tasks = [
            asyncio.create_task(worker(i))
            for i in range(workers)
        ]
        
        # Wait for all jobs to complete
        await self.queue.join()
        
        # Stop workers
        self._processing = False
        await asyncio.gather(*workers_tasks)
    
    def get_stats(self) -> dict:
        """Get queue statistics."""
        return {
            "queue_size": self.queue.qsize(),
            "completed_jobs": len(self.results),
            "processing": self._processing
        }


# Usage examples:
#
# 1. Simple batch processing:
#    processor = BatchProcessor(max_workers=5)
#    result = processor.process_batch(
#        items=[1, 2, 3, 4, 5],
#        process_func=lambda x: x * 2
#    )
#    print(f"Success rate: {result.success_rate}%")
#
# 2. Async batch processing:
#    async def process_item(item):
#        await asyncio.sleep(1)
#        return item * 2
#    
#    result = await processor.process_batch_async(
#        items=[1, 2, 3, 4, 5],
#        process_func=process_item
#    )
#
# 3. Process in chunks:
#    processor = BatchProcessor(batch_size=10)
#    results = processor.process_in_chunks(
#        items=range(100),
#        process_func=lambda x: x * 2
#    )
#
# 4. Job queue:
#    queue = JobQueue()
#    await queue.add_job("job1", {"data": "test"})
#    await queue.process_queue(process_func=my_async_function, workers=5)
