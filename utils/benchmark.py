import asyncio
import time
from typing import List, Any, Callable, Dict
import statistics
from utils.logger import get_logger
from utils.memory_manager import MemoryManager
from utils.query import query_lm_studio
from utils.execute_response import execute_response

logger = get_logger()

class Benchmark:
    def __init__(self):
        self.results: Dict[str, List[float]] = {}

    async def measure_async(self, name: str, coroutine: Callable[..., Any], *args, **kwargs) -> float:
        """Measure async function performance"""
        start_time = time.time()
        try:
            await coroutine(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {name}: {e}")
        
        elapsed_time = time.time() - start_time
        if name not in self.results:
            self.results[name] = []
        self.results[name].append(elapsed_time)
        return elapsed_time

    async def memory_benchmark(self, sample_size: int = 100):
        """Memory Manager performance test"""
        memory_manager = MemoryManager(batch_size=10, max_vectors=1000)
        test_input = "Test memory vector for benchmarking"

        # Vector addition test
        logger.info("Testing addMemoryVector...")
        for _ in range(sample_size):
            await self.measure_async(
                "addMemoryVector",
                memory_manager.addMemoryVector,
                test_input
            )

        # Vector search test
        logger.info("Testing searchInMemoryVector...")
        for _ in range(sample_size):
            await self.measure_async(
                "searchInMemoryVector",
                memory_manager.searchInMemoryVector,
                test_input
            )

        # Database save test
        logger.info("Testing saveToSQLite...")
        await self.measure_async(
            "saveToSQLite",
            memory_manager.saveToSQLite
        )

    async def query_benchmark(self, sample_size: int = 10):
        """LM Studio query performance test"""
        config = {
            "lm_studio_completions_url": "http://localhost:1234/v1/chat/completions",
            "temperature": 0.7,
            "max_tokens": 100
        }
        test_prompt = "Hello, how are you?"

        logger.info("Testing LM Studio queries...")
        for _ in range(sample_size):
            await self.measure_async(
                "query_lm_studio",
                query_lm_studio,
                prompt=test_prompt,
                config=config
            )

    async def response_benchmark(self, sample_size: int = 10):
        """Execute response performance test"""
        test_response = {
            "response": "Test response",
            "need": "weather_forecast:London",
            "commands": "cmd:echo test"
        }
        context = {
            "secrets": {
                "weather_api_key": "test_key"
            },
            "system_ip": "127.0.0.1"
        }

        logger.info("Testing response execution...")
        for _ in range(sample_size):
            await self.measure_async(
                "execute_response",
                execute_response,
                response_text=test_response,
                user_input="test input",
                context=context
            )

    def print_results(self):
        """Print test results"""
        logger.info("\nBenchmark Results:")
        logger.info("=" * 50)
        
        for name, times in self.results.items():
            avg_time = statistics.mean(times)
            min_time = min(times)
            max_time = max(times)
            stddev = statistics.stdev(times) if len(times) > 1 else 0
            
            logger.info(f"\n{name}:")
            logger.info(f"  Average Time: {avg_time:.4f} seconds")
            logger.info(f"  Min Time: {min_time:.4f} seconds")
            logger.info(f"  Max Time: {max_time:.4f} seconds")
            logger.info(f"  Standard Deviation: {stddev:.4f}")
            logger.info(f"  Sample Size: {len(times)}")

async def run_benchmarks():
    """Run all benchmark tests"""
    benchmark = Benchmark()
    
    logger.info("Starting benchmark tests...")
    
    # Memory Manager tests
    await benchmark.memory_benchmark()
    
    # Query tests
    await benchmark.query_benchmark()
    
    # Response tests
    await benchmark.response_benchmark()
    
    # Print results
    benchmark.print_results()

if __name__ == "__main__":
    asyncio.run(run_benchmarks())