from typing import Dict, List, Optional, Any
from utils.database_pool import DatabasePool
from sentence_transformers import SentenceTransformer
from scipy.spatial.distance import cosine

class SimpleVectorMemory:
    def __init__(self):
        self.db_pool = DatabasePool()
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
    
    async def save_memory(self, memory_data: str):
        """Save memory data in key:value format to database"""
        if not memory_data:
            return
            
        conn = await self.db_pool.get_connection()
        try:
            cursor = conn.cursor()
            pairs = memory_data.split(';')
            
            for pair in pairs:
                if ':' not in pair:
                    continue
                    
                key, value = pair.split(':', 1)
                cursor.execute("""
                INSERT INTO user_memory (key, value)
                VALUES (?, ?)
                """, (key.strip(), value.strip()))
            
            conn.commit()
        finally:
            await self.db_pool.release_connection(conn)
    
    async def get_memory(self, key: str) -> Optional[str]:
        """Get the latest value for a specific memory key"""
        conn = await self.db_pool.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT value
            FROM user_memory
            WHERE key = ?
            ORDER BY created_at DESC
            LIMIT 1
            """, (key,))
            
            result = cursor.fetchone()
            return result[0] if result else None
        finally:
            await self.db_pool.release_connection(conn)
    
    async def get_all_memory(self) -> str:
        """Get all latest memory values in key:value format"""
        conn = await self.db_pool.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
            WITH LatestMemory AS (
                SELECT key, value,
                       ROW_NUMBER() OVER (PARTITION BY key ORDER BY created_at DESC) as rn
                FROM user_memory
            )
            SELECT key, value
            FROM LatestMemory
            WHERE rn = 1
            """)
            
            results = cursor.fetchall()
            if not results:
                return ""
                
            return ";".join([f"{key}:{value}" for key, value in results])
        finally:
            await self.db_pool.release_connection(conn)
    
    async def clear_memory(self):
        """Clear all memory data"""
        conn = await self.db_pool.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM user_memory")
            conn.commit()
        finally:
            await self.db_pool.release_connection(conn)
            
    async def search(self, query: str) -> List[Dict[str, Any]]:
        """Search memory entries using semantic similarity"""
        memory = await self.get_all_memory()
        if not memory:
            return []
            
        entries = memory.split(';')
        if not entries:
            return []
            
        # Get embeddings
        query_embedding = self.model.encode([query])[0]
        entry_embeddings = self.model.encode(entries)
        
        # Calculate similarities
        results = []
        for entry, embedding in zip(entries, entry_embeddings):
            similarity = 1 - cosine(query_embedding, embedding)
            results.append({"text": entry, "similarity": float(similarity)})
            
        # Sort by similarity
        results.sort(key=lambda x: x["similarity"], reverse=True)
        return results