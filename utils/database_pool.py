import sqlite3
import asyncio

class DatabasePool:
    def __init__(self, db_path: str = "database.db"):
        self.db_path = db_path
        self._pool = []
        self._pool_lock = asyncio.Lock()
        
    async def _create_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        await self._initialize_tables(conn)
        return conn
    
    async def _initialize_tables(self, conn: sqlite3.Connection):
        cursor = conn.cursor()
        
        # Memory table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_memory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT NOT NULL,
            value TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")
        
        # Memory table indexes
        cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_memory_key 
        ON user_memory(key)
        """)
        
        cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_memory_created 
        ON user_memory(created_at)
        """)
        
        conn.commit()
    
    async def get_connection(self) -> sqlite3.Connection:
        async with self._pool_lock:
            if self._pool:
                return self._pool.pop()
            return await self._create_connection()
    
    async def release_connection(self, conn: sqlite3.Connection):
        async with self._pool_lock:
            self._pool.append(conn)
    
    async def close_all(self):
        async with self._pool_lock:
            for conn in self._pool:
                conn.close()
            self._pool.clear()

export = {
    'DatabasePool': DatabasePool
}