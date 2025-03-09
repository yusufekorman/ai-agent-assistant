import os
import sqlite3
from typing import List
from utils.logger import get_logger

# Get logger instance
logger = get_logger()

class MemoryManager:
    def __init__(self, max_items: int = 1000):
        """
        Initialize Memory Manager
        
        Args:
            max_items: Maximum number of memory items
        """
        self.max_items = max_items
        self.texts: List[str] = []
        
        try:
            logger.info("Initializing memory manager...")
            self._init_db()
            if not self.loadFromSQLite():
                logger.warning("No existing items loaded from database")
        except Exception as e:
            logger.error(f"Initialization error: {e}")
            self.texts = []

    def _init_db(self):
        """Create database tables"""
        with sqlite3.connect('memory.db') as conn:
            c = conn.cursor()
            c.execute('''CREATE TABLE IF NOT EXISTS memory_items
                         (id INTEGER PRIMARY KEY AUTOINCREMENT,
                          text TEXT NOT NULL,
                          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
            conn.commit()

    def addItem(self, text: str) -> None:
        """
        Add new text to memory
        
        Args:
            text: Text to store
        """
        if not isinstance(text, str) or not text.strip():
            raise ValueError("Text must be a non-empty string")

        # Check maximum item count
        if len(self.texts) >= self.max_items:
            # Delete oldest item
            self.deleteItem(0)

        self.texts.append(text)

    def deleteItem(self, index: int) -> None:
        """Delete memory item"""
        if 0 <= index < len(self.texts):
            del self.texts[index]

    def getItems(self) -> List[str]:
        """
        Return memory items in the given order
        
        Args:
            sorted_indices: List of indices in desired order
            
        Returns:
            Memory items in the specified order
        """
        if not self.texts:
            return []

        try:
            return self.texts
        except Exception as e:
            logger.error(f"Error retrieving items: {str(e)}")
            return []

    def clear(self) -> None:
        """Clear all memory items"""
        self.texts.clear()

    def saveToSQLite(self) -> bool:
        """
        Save memory data to database
        
        Returns:
            bool: Operation success status
        """
        try:
            if not self.texts:
                logger.info("No items to save")
                return True

            with sqlite3.connect('memory.db') as conn:
                c = conn.cursor()
                
                # Clean and recreate table
                c.execute("DROP TABLE IF EXISTS memory_items")
                c.execute('''CREATE TABLE memory_items
                           (id INTEGER PRIMARY KEY AUTOINCREMENT,
                            text TEXT NOT NULL,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
                
                # Save all items at once
                data = [(text,) for text in self.texts]
                c.executemany("INSERT INTO memory_items (text) VALUES (?)", data)
                
                conn.commit()
                logger.info(f"Successfully saved {len(data)} text items to database")
                return True

        except Exception as e:
            logger.error(f"Error in saveToSQLite: {e}")
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
                
                # Get latest max_items entries
                c.execute("""
                    SELECT text
                    FROM memory_items
                    ORDER BY created_at DESC
                    LIMIT ?
                """, (self.max_items,))

                # Clear existing items
                self.texts.clear()

                # Load texts
                loaded_count = 0
                for (text,) in c.fetchall():
                    self.texts.append(text)
                    loaded_count += 1

                logger.info(f"Loaded {loaded_count} text items")
                return loaded_count > 0

        except Exception as e:
            logger.error(f"Error loading from database: {e}")
            return False

    def __del__(self):
        """Save items and cleanup when object is deleted"""
        try:
            self.saveToSQLite()
            self.clear()
        except:
            pass