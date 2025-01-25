import spacy
import numpy as np
import sqlite3
import os

class MemoryManager:
    def __init__(self):
        self.memoryVectors = []
        self.vector_embeddings = []
        self.nlp = spacy.load("en_core_web_md")
        self.loadFromSQLite()

    def addMemoryVector(self, memoryVector):
        self.memoryVectors.append(memoryVector)
        # Vector embedding process
        doc = self.nlp(memoryVector)
        self.vector_embeddings.append(doc.vector)

    def deleteMemoryVector(self, index):
        del self.memoryVectors[index]
        del self.vector_embeddings[index]

    def searchInMemoryVector(self, query):
        if not self.memoryVectors:
            return []
            
        # Calculate query vector and convert to numpy array
        query_vector = np.array(self.nlp(query).vector, dtype=np.float32)
        
        # Convert all vectors to numpy array
        embeddings = np.array(self.vector_embeddings, dtype=np.float32)
        
        # Calculate similarities
        similarities = np.zeros(len(embeddings))
        for i, embedding in enumerate(embeddings):
            similarities[i] = np.dot(embedding, query_vector) / (np.linalg.norm(embedding) * np.linalg.norm(query_vector))
        
        # Find top 5 similarities
        top5_indices = np.argsort(similarities)[-5:][::-1]
        top5_memoryVectors = [self.memoryVectors[i] for i in top5_indices]
        return top5_memoryVectors

    def clearMemoryVector(self):
        self.memoryVectors = []
        self.vector_embeddings = []

    def saveToSQLite(self):
        try:
            conn = sqlite3.connect('memory.db')
            c = conn.cursor()
            
            # Create table
            c.execute('''CREATE TABLE IF NOT EXISTS memory_vectors
                        (id INTEGER PRIMARY KEY AUTOINCREMENT,
                         text TEXT NOT NULL,
                         vector BLOB NOT NULL)''')
            
            # Save data
            for text, vector in zip(self.memoryVectors, self.vector_embeddings):
                c.execute("INSERT INTO memory_vectors (text, vector) VALUES (?, ?)",
                         (text, vector.tobytes()))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"SQLite save error: {e}")
            return False

    def loadFromSQLite(self):
        if os.path.exists('memory.db'):
            try:
                conn = sqlite3.connect('memory.db')
                c = conn.cursor()
                c.execute("SELECT text, vector FROM memory_vectors")
                rows = c.fetchall()
                
                self.memoryVectors = []
                self.vector_embeddings = []
                
                for text, vector_bytes in rows:
                    self.memoryVectors.append(text)
                    # Convert vector to numpy array of float32
                    vector = np.frombuffer(vector_bytes, dtype=np.float32)
                    self.vector_embeddings.append(vector)
                
                conn.close()
                return True
            except Exception as e:
                print(f"SQLite load error: {e}")
                return False
        return False

    def __del__(self):
        response = input("Would you like to save memory data to SQLite? (y/n): ")
        if response.lower() == 'y':
            if self.saveToSQLite():
                print("Data saved successfully.")
            else:
                print("Error saving data.")