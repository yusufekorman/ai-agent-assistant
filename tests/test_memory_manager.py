import unittest
import os
import numpy as np
from unittest.mock import patch, MagicMock
from utils.memory_manager import MemoryManager

class TestMemoryManager(unittest.TestCase):
    def setUp(self):
        """Her test öncesi çalışacak kurulum"""
        self.memory_manager = MemoryManager(batch_size=10, max_vectors=100)
        self.test_input = "Test memory input"
        
        # Test veritabanı dosyasını sil
        if os.path.exists('memory.db'):
            os.remove('memory.db')

    def tearDown(self):
        """Her test sonrası temizlik"""
        self.memory_manager.clearMemoryVector()
        if os.path.exists('memory.db'):
            os.remove('memory.db')

    def test_initialization(self):
        """Başlatma parametreleri testi"""
        # Geçersiz batch_size
        with self.assertRaises(ValueError):
            MemoryManager(batch_size=0)
        
        # Geçersiz max_vectors
        with self.assertRaises(ValueError):
            MemoryManager(max_vectors=0)
            
        # Sınır değerler
        mm = MemoryManager(batch_size=2000, max_vectors=20000)
        self.assertEqual(mm.batch_size, 1000)  # Maximum limit
        self.assertEqual(mm.max_vectors, 10000)  # Maximum limit

    @patch('spacy.load')
    def test_nlp_lazy_loading(self, mock_spacy_load):
        """NLP modelinin lazy loading testi"""
        mock_nlp = MagicMock()
        mock_spacy_load.return_value = mock_nlp
        
        # İlk erişimde yüklenmeli
        _ = self.memory_manager.nlp
        mock_spacy_load.assert_called_once_with("en_core_web_md", disable=['ner', 'parser'])
        
        # İkinci erişimde yüklememeli
        _ = self.memory_manager.nlp
        mock_spacy_load.assert_called_once()

    def test_vector_calculation(self):
        """Vektör hesaplama testleri"""
        # Geçersiz girdiler
        with self.assertRaises(TypeError):
            self.memory_manager._calculate_vector(None)
        
        with self.assertRaises(ValueError):
            self.memory_manager._calculate_vector("")
            
        # Gerçek vektör hesaplama
        vector = self.memory_manager._calculate_vector(self.test_input)
        self.assertIsInstance(vector, np.ndarray)
        self.assertEqual(vector.shape[0], 300)  # spaCy default boyutu
        self.assertEqual(vector.dtype, np.dtype('float32'))

    def test_add_memory_vector(self):
        """Belleğe vektör ekleme testleri"""
        # Başarılı ekleme
        self.memory_manager.addMemoryVector(self.test_input)
        self.assertEqual(len(self.memory_manager.memoryVectors), 1)
        self.assertEqual(len(self.memory_manager.vector_embeddings), 1)
        
        # Maximum vektör limiti testi
        for i in range(150):  # max_vectors = 100
            self.memory_manager.addMemoryVector(f"Test {i}")
        self.assertLessEqual(len(self.memory_manager.memoryVectors), 100)

    def test_delete_memory_vector(self):
        """Vektör silme testleri"""
        # Test verisi ekle
        self.memory_manager.addMemoryVector(self.test_input)
        initial_count = len(self.memory_manager.memoryVectors)
        
        # Geçerli indeks ile silme
        self.memory_manager.deleteMemoryVector(0)
        self.assertEqual(len(self.memory_manager.memoryVectors), initial_count - 1)
        
        # Geçersiz indeks ile silme
        self.memory_manager.deleteMemoryVector(99)  # No effect
        self.assertEqual(len(self.memory_manager.memoryVectors), initial_count - 1)

    def test_search_in_memory_vector(self):
        """Bellek arama testleri"""
        test_inputs = [
            "The quick brown fox jumps over the lazy dog",
            "A quick brown dog jumps over the lazy fox",
            "The lazy fox sleeps while the quick brown dog watches",
            "Completely different text about artificial intelligence"
        ]
        
        for input_text in test_inputs:
            self.memory_manager.addMemoryVector(input_text)
        
        # Benzer içerik araması
        results = self.memory_manager.searchInMemoryVector("quick brown fox")
        self.assertGreater(len(results), 0)
        self.assertLessEqual(len(results), 5)
        
        # Alakasız içerik araması
        results = self.memory_manager.searchInMemoryVector("artificial intelligence")
        self.assertEqual(len([r for r in results if "artificial" in r.lower()]), 1)

    def test_clear_memory_vector(self):
        """Bellek temizleme testi"""
        self.memory_manager.addMemoryVector(self.test_input)
        self.memory_manager.clearMemoryVector()
        self.assertEqual(len(self.memory_manager.memoryVectors), 0)
        self.assertEqual(len(self.memory_manager.vector_embeddings), 0)

    def test_save_load_sqlite(self):
        """SQLite kaydetme ve yükleme testleri"""
        # Test verilerini ekle
        test_inputs = ["First test", "Second test", "Third test"]
        for input_text in test_inputs:
            self.memory_manager.addMemoryVector(input_text)
        
        # Kaydet
        save_success = self.memory_manager.saveToSQLite()
        self.assertTrue(save_success)
        self.assertTrue(os.path.exists('memory.db'))
        
        # Temizle
        self.memory_manager.clearMemoryVector()
        self.assertEqual(len(self.memory_manager.memoryVectors), 0)
        
        # Yükle
        load_success = self.memory_manager.loadFromSQLite()
        self.assertTrue(load_success)
        self.assertEqual(len(self.memory_manager.memoryVectors), len(test_inputs))

    def test_auto_save(self):
        """Auto-save özelliği testi"""
        # Auto-save açık memory manager
        mm_auto = MemoryManager(auto_save=True)
        mm_auto.addMemoryVector(self.test_input)
        
        # Nesneyi sil (auto-save tetiklenmeli)
        del mm_auto
        
        # Yeni memory manager ile yükle
        mm_new = MemoryManager()
        self.assertTrue(mm_new.loadFromSQLite())
        self.assertGreater(len(mm_new.memoryVectors), 0)

    def test_batch_operations(self):
        """Batch işlemleri testi"""
        # Batch size'dan fazla veri ekle
        batch_size = 10
        mm = MemoryManager(batch_size=batch_size)
        
        test_inputs = [f"Test input {i}" for i in range(batch_size * 2)]
        for input_text in test_inputs:
            mm.addMemoryVector(input_text)
            
        # Kaydet ve kontrol et
        save_success = mm.saveToSQLite()
        self.assertTrue(save_success)
        
        # Yeni instance ile yükle
        mm_new = MemoryManager(batch_size=batch_size)
        load_success = mm_new.loadFromSQLite()
        self.assertTrue(load_success)
        self.assertEqual(len(mm_new.memoryVectors), len(test_inputs))

def run_tests():
    unittest.main()

if __name__ == '__main__':
    run_tests()