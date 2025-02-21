import unittest
import asyncio
import sys
import os
import time
import coverage
from typing import List, Type

# Add main directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import test modules
from test_query import TestQueryLLM
from test_memory_manager import TestMemoryManager
from test_execute_response import TestExecuteResponse

class AsyncioTestRunner:
    """Custom test runner for asynchronous tests"""
    def __init__(self, test_cases: List[Type[unittest.TestCase]]):
        self.test_cases = test_cases
        self.start_time = None
        self.cov = coverage.Coverage(
            branch=True,
            source=['utils'],
            omit=['*/__init__.py']
        )

    def run_tests(self, verbosity: int = 2, failfast: bool = False) -> unittest.TestResult:
        """Run tests and return results"""
        self.start_time = time.time()
        
        # Start coverage measurement
        self.cov.start()

        # Create test suite
        loader = unittest.TestLoader()
        suite = unittest.TestSuite()

        for test_case in self.test_cases:
            suite.addTests(loader.loadTestsFromTestCase(test_case))

        # Configure test runner
        runner = unittest.TextTestRunner(
            verbosity=verbosity,
            failfast=failfast
        )

        # Initial information
        total_tests = suite.countTestCases()
        print(f"\n{'='*60}")
        print(f"Running {total_tests} tests")
        print(f"{'='*60}\n")

        # Run tests
        result = runner.run(suite)

        # End coverage measurement
        self.cov.stop()
        self.cov.save()

        # Report results
        self._print_results(result)
        
        return result

    def _print_results(self, result: unittest.TestResult) -> None:
        """Report test results in detail"""
        elapsed_time = time.time() - self.start_time
        
        print(f"\n{'='*60}")
        print("TEST RESULTS")
        print(f"{'='*60}")
        print(f"Total time: {elapsed_time:.2f} seconds")
        print(f"Tests run: {result.testsRun}")
        print(f"Successful tests: {result.testsRun - len(result.failures) - len(result.errors)}")
        print(f"Failed tests: {len(result.failures)}")
        print(f"Error tests: {len(result.errors)}")
        print(f"Skipped tests: {len(result.skipped)}")
        
        # Failed test details
        if result.failures:
            print(f"\n{'='*60}")
            print("FAILED TESTS")
            print(f"{'='*60}")
            for failure in result.failures:
                print(f"\n{failure[0]}")
                print(f"{'-'*60}")
                print(failure[1])

        # Error test details
        if result.errors:
            print(f"\n{'='*60}")
            print("ERROR TESTS")
            print(f"{'='*60}")
            for error in result.errors:
                print(f"\n{error[0]}")
                print(f"{'-'*60}")
                print(error[1])

        # Coverage report
        print(f"\n{'='*60}")
        print("COVERAGE REPORT")
        print(f"{'='*60}")
        self.cov.report()

def run_tests(
    verbosity: int = 2,
    failfast: bool = False,
    pattern: str = 'test*.py'
) -> None:
    """
    Main test running function
    
    Args:
        verbosity: Test output detail level (1-3)
        failfast: Stop on first failure option
        pattern: Test file matching pattern
    """
    # Define test classes
    test_cases = [
        TestQueryLLM,
        TestMemoryManager,
        TestExecuteResponse
    ]

    # Create and run test runner
    runner = AsyncioTestRunner(test_cases)
    result = runner.run_tests(
        verbosity=verbosity,
        failfast=failfast
    )

    # Exit on failure
    if not result.wasSuccessful():
        sys.exit(1)

if __name__ == '__main__':
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description='Test runner')
    parser.add_argument('-v', '--verbosity', type=int, default=2,
                      help='Output detail level (1-3)')
    parser.add_argument('-f', '--failfast', action='store_true',
                      help='Stop on first failure')
    parser.add_argument('-p', '--pattern', default='test*.py',
                      help='Test file matching pattern')
    
    args = parser.parse_args()
    
    # Run tests
    run_tests(
        verbosity=args.verbosity,
        failfast=args.failfast,
        pattern=args.pattern
    )