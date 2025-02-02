import unittest
from utils.memory_manager import MemoryManager

class TestMemoryManager(unittest.TestCase):
    def setUp(self):
        """Her test öncesi çalışacak kurulum"""
        self.memory_manager = MemoryManager()
        self.test_input = "Test memory input"

    def tearDown(self):
        """Her test sonrası temizlik"""
        del self.memory_manager

    def test_add_memory_vector(self):
        """Belleğe vektör ekleme testleri"""
        # Vektör ekleme
        self.memory_manager.addMemoryVector(self.test_input)
        
        # Vektörleri ara
        results = self.memory_manager.searchInMemoryVector(self.test_input)
        
        # Test et
        self.assertIsNotNone(results)
        self.assertIsInstance(results, list)
        self.assertTrue(len(results) > 0)

    def test_search_memory_vector(self):
        """Bellek arama testleri"""
        # Test verilerini ekle
        test_inputs = [
            "First test memory",
            "Second test memory",
            "Third test memory"
        ]
        
        for input_text in test_inputs:
            self.memory_manager.addMemoryVector(input_text)
        
        # Arama yap
        results = self.memory_manager.searchInMemoryVector("test memory")
        
        # Testler
        self.assertIsNotNone(results)
        self.assertIsInstance(results, list)
        self.assertLessEqual(len(results), 5)  # En fazla 5 sonuç döndürmeli

    def test_empty_input(self):
        """Boş girdi testi"""
        with self.assertRaises(ValueError):
            self.memory_manager.addMemoryVector("")
        
        with self.assertRaises(ValueError):
            self.memory_manager.searchInMemoryVector("")

    def test_invalid_input_type(self):
        """Geçersiz girdi tipi testi"""
        invalid_inputs = [None, 123, [], {}]
        
        for invalid_input in invalid_inputs:
            with self.assertRaises(TypeError):
                self.memory_manager.addMemoryVector(invalid_input)
            
            with self.assertRaises(TypeError):
                self.memory_manager.searchInMemoryVector(invalid_input)

    def test_memory_limit(self):
        """Bellek limiti testi"""
        # Çok sayıda vektör ekle
        for i in range(1000):
            self.memory_manager.addMemoryVector(f"Test memory {i}")
        
        # Bellek boyutunu kontrol et
        total_vectors = len(self.memory_manager.searchInMemoryVector("Test"))
        self.assertLessEqual(total_vectors, 5)  # En fazla 5 sonuç döndürmeli

def run_tests():
    unittest.main()

if __name__ == '__main__':
    run_tests()