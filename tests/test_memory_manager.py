import unittest
import os
import numpy as np
from unittest.mock import patch, MagicMock
from utils.memory_manager import MemoryManager

class TestMemoryManager(unittest.TestCase):
    def setUp(self):
        """Setup to run before each test"""
        self.memory_manager = MemoryManager(batch_size=10, max_vectors=100)
        self.test_input = "Test memory input"
        
        # Delete test database file
        if os.path.exists('memory.db'):
            os.remove('memory.db')

    def tearDown(self):
        """Cleanup after each test"""
        self.memory_manager.clearMemoryVector()
        if os.path.exists('memory.db'):
            os.remove('memory.db')

    def test_initialization(self):
        """Initialization parameters test"""
        # Invalid batch_size
        with self.assertRaises(ValueError):
            MemoryManager(batch_size=0)
        
        # Invalid max_vectors
        with self.assertRaises(ValueError):
            MemoryManager(max_vectors=0)
            
        # Boundary values
        mm = MemoryManager(batch_size=2000, max_vectors=20000)
        self.assertEqual(mm.batch_size, 1000)  # Maximum limit
        self.assertEqual(mm.max_vectors, 10000)  # Maximum limit

    @patch('spacy.load')
    def test_nlp_lazy_loading(self, mock_spacy_load):
        """NLP model lazy loading test"""
        mock_nlp = MagicMock()
        mock_spacy_load.return_value = mock_nlp
        
        # Should load on first access
        _ = self.memory_manager.nlp
        mock_spacy_load.assert_called_once_with("en_core_web_md", disable=['ner', 'parser'])
        
        # Should not load on second access
        _ = self.memory_manager.nlp
        mock_spacy_load.assert_called_once()

    def test_vector_calculation(self):
        """Vector calculation tests"""
        # Invalid inputs
        with self.assertRaises(TypeError):
            self.memory_manager._calculate_vector(None)
        
        with self.assertRaises(ValueError):
            self.memory_manager._calculate_vector("")
            
        # Real vector calculation
        vector = self.memory_manager._calculate_vector(self.test_input)
        self.assertIsInstance(vector, np.ndarray)
        self.assertEqual(vector.shape[0], 300)  # spaCy default size
        self.assertEqual(vector.dtype, np.dtype('float32'))

    def test_add_memory_vector(self):
        """Memory vector addition tests"""
        # Successful addition
        self.memory_manager.addMemoryVector(self.test_input)
        self.assertEqual(len(self.memory_manager.memoryVectors), 1)
        self.assertEqual(len(self.memory_manager.vector_embeddings), 1)
        
        # Maximum vector limit test
        for i in range(150):  # max_vectors = 100
            self.memory_manager.addMemoryVector(f"Test {i}")
        self.assertLessEqual(len(self.memory_manager.memoryVectors), 100)

    def test_delete_memory_vector(self):
        """Vector deletion tests"""
        # Add test data
        self.memory_manager.addMemoryVector(self.test_input)
        initial_count = len(self.memory_manager.memoryVectors)
        
        # Delete with valid index
        self.memory_manager.deleteMemoryVector(0)
        self.assertEqual(len(self.memory_manager.memoryVectors), initial_count - 1)
        
        # Delete with invalid index
        self.memory_manager.deleteMemoryVector(99)  # No effect
        self.assertEqual(len(self.memory_manager.memoryVectors), initial_count - 1)

    def test_search_in_memory_vector(self):
        """Memory search tests"""
        test_inputs = [
            "The quick brown fox jumps over the lazy dog",
            "A quick brown dog jumps over the lazy fox",
            "The lazy fox sleeps while the quick brown dog watches",
            "Completely different text about artificial intelligence"
        ]
        
        for input_text in test_inputs:
            self.memory_manager.addMemoryVector(input_text)
        
        # Similar content search
        results = self.memory_manager.searchInMemoryVector("quick brown fox")
        self.assertGreater(len(results), 0)
        self.assertLessEqual(len(results), 5)
        
        # Unrelated content search
        results = self.memory_manager.searchInMemoryVector("artificial intelligence")
        self.assertEqual(len([r for r in results if "artificial" in r.lower()]), 1)

    def test_clear_memory_vector(self):
        """Memory clearing test"""
        self.memory_manager.addMemoryVector(self.test_input)
        self.memory_manager.clearMemoryVector()
        self.assertEqual(len(self.memory_manager.memoryVectors), 0)
        self.assertEqual(len(self.memory_manager.vector_embeddings), 0)

    def test_save_load_sqlite(self):
        """SQLite save and load tests"""
        # Add test data
        test_inputs = ["First test", "Second test", "Third test"]
        for input_text in test_inputs:
            self.memory_manager.addMemoryVector(input_text)
        
        # Save
        save_success = self.memory_manager.saveToSQLite()
        self.assertTrue(save_success)
        self.assertTrue(os.path.exists('memory.db'))
        
        # Clear
        self.memory_manager.clearMemoryVector()
        self.assertEqual(len(self.memory_manager.memoryVectors), 0)
        
        # Load
        load_success = self.memory_manager.loadFromSQLite()
        self.assertTrue(load_success)
        self.assertEqual(len(self.memory_manager.memoryVectors), len(test_inputs))

    def test_auto_save(self):
        """Auto-save feature test"""
        # Memory manager with auto-save enabled
        mm_auto = MemoryManager(auto_save=True)
        mm_auto.addMemoryVector(self.test_input)
        
        # Delete object (should trigger auto-save)
        del mm_auto
        
        # Load with new memory manager
        mm_new = MemoryManager()
        self.assertTrue(mm_new.loadFromSQLite())
        self.assertGreater(len(mm_new.memoryVectors), 0)

    def test_batch_operations(self):
        """Batch operations test"""
        # Add more data than batch size
        batch_size = 10
        mm = MemoryManager(batch_size=batch_size)
        
        test_inputs = [f"Test input {i}" for i in range(batch_size * 2)]
        for input_text in test_inputs:
            mm.addMemoryVector(input_text)
            
        # Save and verify
        save_success = mm.saveToSQLite()
        self.assertTrue(save_success)
        
        # Load with new instance
        mm_new = MemoryManager(batch_size=batch_size)
        load_success = mm_new.loadFromSQLite()
        self.assertTrue(load_success)
        self.assertEqual(len(mm_new.memoryVectors), len(test_inputs))

def run_tests():
    unittest.main()

if __name__ == '__main__':
    run_tests()