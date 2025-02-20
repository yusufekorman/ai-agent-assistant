import unittest
import asyncio
import sys
import os
import time
import coverage
from typing import List, Type

# Ana dizini Python path'ine ekle
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Test modüllerini import et
from test_query import TestQueryLLM
from test_memory_manager import TestMemoryManager
from test_execute_response import TestExecuteResponse

class AsyncioTestRunner:
    """Asenkron testler için özel test koşucusu"""
    def __init__(self, test_cases: List[Type[unittest.TestCase]]):
        self.test_cases = test_cases
        self.start_time = None
        self.cov = coverage.Coverage(
            branch=True,
            source=['utils'],
            omit=['*/__init__.py']
        )

    def run_tests(self, verbosity: int = 2, failfast: bool = False) -> unittest.TestResult:
        """Testleri çalıştır ve sonuçları döndür"""
        self.start_time = time.time()
        
        # Coverage ölçümünü başlat
        self.cov.start()

        # Test suite'i oluştur
        loader = unittest.TestLoader()
        suite = unittest.TestSuite()

        for test_case in self.test_cases:
            suite.addTests(loader.loadTestsFromTestCase(test_case))

        # Test runner'ı yapılandır
        runner = unittest.TextTestRunner(
            verbosity=verbosity,
            failfast=failfast
        )

        # Başlangıç bilgisi
        total_tests = suite.countTestCases()
        print(f"\n{'='*60}")
        print(f"Toplam {total_tests} test çalıştırılacak")
        print(f"{'='*60}\n")

        # Testleri çalıştır
        result = runner.run(suite)

        # Coverage ölçümünü sonlandır
        self.cov.stop()
        self.cov.save()

        # Sonuçları raporla
        self._print_results(result)
        
        return result

    def _print_results(self, result: unittest.TestResult) -> None:
        """Test sonuçlarını detaylı olarak raporla"""
        elapsed_time = time.time() - self.start_time
        
        print(f"\n{'='*60}")
        print("TEST SONUÇLARI")
        print(f"{'='*60}")
        print(f"Toplam süre: {elapsed_time:.2f} saniye")
        print(f"Çalıştırılan testler: {result.testsRun}")
        print(f"Başarılı testler: {result.testsRun - len(result.failures) - len(result.errors)}")
        print(f"Başarısız testler: {len(result.failures)}")
        print(f"Hatalı testler: {len(result.errors)}")
        print(f"Atlanan testler: {len(result.skipped)}")
        
        # Başarısız testlerin detayları
        if result.failures:
            print(f"\n{'='*60}")
            print("BAŞARISIZ TESTLER")
            print(f"{'='*60}")
            for failure in result.failures:
                print(f"\n{failure[0]}")
                print(f"{'-'*60}")
                print(failure[1])

        # Hatalı testlerin detayları
        if result.errors:
            print(f"\n{'='*60}")
            print("HATALI TESTLER")
            print(f"{'='*60}")
            for error in result.errors:
                print(f"\n{error[0]}")
                print(f"{'-'*60}")
                print(error[1])

        # Coverage raporu
        print(f"\n{'='*60}")
        print("KAPSAM RAPORU")
        print(f"{'='*60}")
        self.cov.report()

def run_tests(
    verbosity: int = 2,
    failfast: bool = False,
    pattern: str = 'test*.py'
) -> None:
    """
    Ana test çalıştırma fonksiyonu
    
    Args:
        verbosity: Test çıktı detay seviyesi (1-3)
        failfast: İlk hatada durma seçeneği
        pattern: Test dosyası eşleşme kalıbı
    """
    # Test sınıflarını tanımla
    test_cases = [
        TestQueryLLM,
        TestMemoryManager,
        TestExecuteResponse
    ]

    # Test koşucusunu oluştur ve çalıştır
    runner = AsyncioTestRunner(test_cases)
    result = runner.run_tests(
        verbosity=verbosity,
        failfast=failfast
    )

    # Başarısızlık durumunda programı sonlandır
    if not result.wasSuccessful():
        sys.exit(1)

if __name__ == '__main__':
    # Komut satırı argümanlarını işle
    import argparse
    parser = argparse.ArgumentParser(description='Test koşucusu')
    parser.add_argument('-v', '--verbosity', type=int, default=2,
                      help='Çıktı detay seviyesi (1-3)')
    parser.add_argument('-f', '--failfast', action='store_true',
                      help='İlk hatada dur')
    parser.add_argument('-p', '--pattern', default='test*.py',
                      help='Test dosyası eşleşme kalıbı')
    
    args = parser.parse_args()
    
    # Testleri çalıştır
    run_tests(
        verbosity=args.verbosity,
        failfast=args.failfast,
        pattern=args.pattern
    )