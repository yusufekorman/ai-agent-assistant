import os
import sqlite3
from typing import List, Optional, Dict, Any
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache

import spacy
import numpy as np
from utils.logger import get_logger

# Get logger instance
logger = get_logger()

class MemoryManager:
    def __init__(self, batch_size: int = 100, max_vectors: int = 1000, auto_save: bool = True):
        """
        Initialize Memory Manager
        
        Args:
            batch_size: Batch size for database operations (1-1000)
            max_vectors: Maximum number of memory vectors (1-10000)
            auto_save: Auto-save feature
            
        Raises:
            ValueError: For invalid parameter values
        """
        # Parameter validation
        if not isinstance(batch_size, int) or batch_size <= 0:
            raise ValueError("batch_size must be a positive integer")
        if not isinstance(max_vectors, int) or max_vectors <= 0:
            raise ValueError("max_vectors must be a positive integer")
            
        # Safe limits
        self.batch_size = min(max(1, batch_size), 1000)
        self.max_vectors = min(max(1, max_vectors), 10000)
        self.auto_save = bool(auto_save)
        
        # Main data structures
        self.memoryVectors: List[str] = []
        self.vector_embeddings: List[np.ndarray] = []
        
        # Define nlp as property for lazy loading
        self._nlp = None
        
        try:
            # Initialize database connection
            logger.info("Initializing memory manager...")
            self._init_db()
            if not self.loadFromSQLite():
                logger.warning("No existing vectors loaded from database")
        except Exception as e:
            logger.error(f"Initialization error: {e}")
            # Initialize basic structures as empty
            self.memoryVectors = []
            self.vector_embeddings = []

    @property
    def nlp(self):
        """Load spacy model with lazy loading"""
        if self._nlp is None:
            self._nlp = spacy.load("en_core_web_md", disable=['ner', 'parser'])
        return self._nlp

    def _init_db(self):
        """Create database tables"""
        with sqlite3.connect('memory.db') as conn:
            c = conn.cursor()
            c.execute('''CREATE TABLE IF NOT EXISTS memory_vectors
                        (id INTEGER PRIMARY KEY AUTOINCREMENT,
                         text TEXT NOT NULL,
                         vector BLOB NOT NULL,
                         created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
            conn.commit()

    @lru_cache(maxsize=1000)
    def _calculate_vector(self, text: str) -> np.ndarray:
        """Convert text to vector and cache"""
        if not isinstance(text, str):
            raise TypeError("Input must be a string")
        if not text.strip():
            raise ValueError("Input cannot be empty")
            
        # Create spacy doc and convert to vector
        doc = self.nlp(text)
        if not doc.has_vector:
            raise ValueError("Could not generate vector for text")
            
        # Convert vector to numpy array
        vector = np.array(doc.vector)
        
        if not vector.size:
            raise ValueError("Empty vector generated")
            
        # Check vector size (spaCy's default size)
        expected_size = 300
        if vector.size != expected_size:
            raise ValueError(f"Unexpected vector size: {vector.size}, expected: {expected_size}")
            
        # Convert to float32 type
        return vector.astype(dtype=np.dtype('float32'))

    def addMemoryVector(self, memoryVector: str) -> None:
        """Add new memory vector"""
        if not isinstance(memoryVector, str):
            raise TypeError("Memory vector must be a string")
        if not memoryVector.strip():
            raise ValueError("Memory vector cannot be empty")

        # Check maximum vector count
        if len(self.memoryVectors) >= self.max_vectors:
            # Delete oldest vector
            self.deleteMemoryVector(0)

        # Calculate and add vector
        vector = self._calculate_vector(memoryVector)
        self.memoryVectors.append(memoryVector)
        self.vector_embeddings.append(vector)

    def deleteMemoryVector(self, index: int) -> None:
        """Delete memory vector"""
        if 0 <= index < len(self.memoryVectors):
            del self.memoryVectors[index]
            del self.vector_embeddings[index]

    def searchInMemoryVector(self, query: str, top_k: int = 5) -> List[str]:
        """
        Find most similar memory vectors
        
        Args:
            query: Search text
            top_k: Number of results to return
            
        Returns:
            Top k most similar memory vectors
            
        Raises:
            TypeError: Invalid input type
            ValueError: Empty input or vector generation error
        """
        # Input validation
        if not isinstance(query, str):
            raise TypeError("Query must be a string")
        if not query.strip():
            raise ValueError("Query cannot be empty")
        if not self.memoryVectors:
            return []

        try:
            # Calculate query vector
            query_vector = self._calculate_vector(query)

            # Convert all vectors to numpy array
            if not self.vector_embeddings:
                return []
                
            embeddings = np.stack(self.vector_embeddings).astype(np.float32)
            
            # Check vector dimensions
            if embeddings.shape[1] != query_vector.shape[0]:
                raise ValueError(
                    f"Vector dimension mismatch: embeddings {embeddings.shape}, query {query_vector.shape}"
                )

            # Calculate similarity (vectorized)
            norm_query = np.linalg.norm(query_vector)
            norm_embeddings = np.linalg.norm(embeddings, axis=1)
            
            # Check division by zero
            if norm_query == 0 or np.any(norm_embeddings == 0):
                raise ValueError("Zero magnitude vectors detected")
                
            similarities = np.dot(embeddings, query_vector) / (norm_embeddings * norm_query)

            # Check for NaN values
            if np.any(np.isnan(similarities)):
                raise ValueError("NaN values in similarity calculation")

            # Find highest similarities
            top_k = min(top_k, len(similarities))
            top_k_indices = np.argpartition(similarities, -top_k)[-top_k:]
            top_k_indices = top_k_indices[np.argsort(similarities[top_k_indices])][::-1]

            return [self.memoryVectors[i] for i in top_k_indices]

        except Exception as e:
            logger.error(f"Error in vector search: {str(e)}")
            return []

    def clearMemoryVector(self) -> None:
        """Clear all memory"""
        self.memoryVectors.clear()
        self.vector_embeddings.clear()

    def saveToSQLite(self) -> bool:
        """
        Save memory data to database
        
        Returns:
            bool: Operation success status
        """
        try:
            if not self.memoryVectors:
                logger.info("No vectors to save")
                return True

            with sqlite3.connect('memory.db') as conn:
                c = conn.cursor()
                
                # Clean and recreate table
                c.execute("DROP TABLE IF EXISTS memory_vectors")
                c.execute('''CREATE TABLE memory_vectors
                           (id INTEGER PRIMARY KEY AUTOINCREMENT,
                            text TEXT NOT NULL,
                            vector BLOB NOT NULL,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
                
                # Prepare data
                data = []
                for text, vector in zip(self.memoryVectors, self.vector_embeddings):
                    if not isinstance(vector, np.ndarray):
                        logger.warning(f"Invalid vector type for text: {text[:50]}...")
                        continue
                    try:
                        data.append((text, vector.tobytes()))
                    except Exception as e:
                        logger.error(f"Error converting vector to bytes: {e}")
                        continue

                # Batch insert
                for i in range(0, len(data), self.batch_size):
                    batch = data[i:i + self.batch_size]
                    try:
                        c.executemany(
                            "INSERT INTO memory_vectors (text, vector) VALUES (?, ?)",
                            batch
                        )
                    except sqlite3.Error as e:
                        logger.error(f"SQLite batch insert error: {e}")
                        return False

                conn.commit()
                logger.info(f"Successfully saved {len(data)} vectors to database")
                return True

        except sqlite3.Error as e:
            logger.error(f"SQLite database error: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error in saveToSQLite: {e}")
            return False

    def loadFromSQLite(self) -> bool:
        """
        Load memory data from database
        
        Returns:
            bool: Operation success status
        """
        if not os.path.exists('memory.db'):
            logger.info("No memory database found")
            return False

        try:
            with sqlite3.connect('memory.db') as conn:
                c = conn.cursor()
                
                try:
                    # Get latest max_vectors entries
                    c.execute("""
                        SELECT text, vector
                        FROM memory_vectors
                        ORDER BY created_at DESC
                        LIMIT ?
                    """, (self.max_vectors,))
                except sqlite3.Error as e:
                    logger.error(f"SQLite query error: {e}")
                    return False

                # Clear existing vectors
                self.memoryVectors.clear()
                self.vector_embeddings.clear()

                loaded_count = 0
                error_count = 0

                # Use ThreadPoolExecutor for batch processing
                with ThreadPoolExecutor() as executor:
                    for text, vector_bytes in c.fetchall():
                        try:
                            vector = np.frombuffer(vector_bytes, dtype=np.float32)
                            
                            # Check vector size
                            if vector.size != 300:  # spaCy's default size
                                logger.warning(f"Skipping vector with invalid size: {vector.size}")
                                error_count += 1
                                continue

                            self.memoryVectors.append(text)
                            self.vector_embeddings.append(vector)
                            loaded_count += 1

                        except Exception as e:
                            logger.error(f"Error loading vector: {e}")
                            error_count += 1

                logger.info(f"Loaded {loaded_count} vectors, {error_count} errors")
                return loaded_count > 0

        except sqlite3.Error as e:
            logger.error(f"SQLite database error: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error in loadFromSQLite: {e}")
            return False

    def __del__(self):
        """
        Auto-save when object is deleted
        """
        if not hasattr(self, 'auto_save') or not self.auto_save:
            return

        try:
            if not hasattr(self, 'memoryVectors') or not self.memoryVectors:
                logger.debug("No vectors to save during cleanup")
                return

            logger.info("Auto-saving memory vectors during cleanup...")
            if self.saveToSQLite():
                logger.info(f"Successfully saved {len(self.memoryVectors)} vectors")
            else:
                logger.error("Failed to save vectors during cleanup")
                
        except Exception as e:
            logger.error(f"Error during auto-save cleanup: {e}")
        finally:
            # Clear memory
            try:
                self.clearMemoryVector()
            except:
                pass