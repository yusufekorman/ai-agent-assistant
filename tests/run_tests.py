import unittest
import asyncio
import sys
import os

# Ana dizini Python path'ine ekle
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Test modüllerini import et
from test_query import TestQueryLMStudio
from test_memory_manager import TestMemoryManager
from test_execute_response import TestExecuteResponse

def run_tests():
    """Tüm test suitlerini çalıştır"""
    # Test loader oluştur
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Test sınıflarını ekle
    test_cases = [
        TestQueryLMStudio,
        TestMemoryManager,
        TestExecuteResponse
    ]

    for test_case in test_cases:
        suite.addTests(loader.loadTestsFromTestCase(test_case))

    # Test sonuçları için runner oluştur
    runner = unittest.TextTestRunner(verbosity=2)
    
    print("=== Başlangıç Test Sonuçları ===")
    result = runner.run(suite)
    print("=== Test Sonuçları ===")
    print(f"Çalıştırılan testler: {result.testsRun}")
    print(f"Başarısız: {len(result.failures)}")
    print(f"Hatalar: {len(result.errors)}")
    print("========================")

    # Hata varsa programı hata koduyla sonlandır
    if not result.wasSuccessful():
        sys.exit(1)

if __name__ == '__main__':
    run_tests()