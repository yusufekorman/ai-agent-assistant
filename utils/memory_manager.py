import spacy
import os

class MemoryManager:
    def __init__(self):
        self.memoryVectors = []
        self.loadMemoryVector()

    def addMemoryVector(self, memoryVector):
        self.memoryVectors.append(memoryVector)

    def deleteMemoryVector(self, index):
        del self.memoryVectors[index]

    def searchInMemoryVector(self, query):
        # implement search logic with similarity score use spacy
        nlp = spacy.load("en_core_web_md")
        doc = nlp(query)
        similarity_scores = [doc.similarity(nlp(memoryVector)) for memoryVector in self.memoryVectors]
        
        # sonrasında ilk 5 en yüksek olanları getir
        top5_indices = sorted(range(len(similarity_scores)), key=similarity_scores.__getitem__, reverse=True)[:5]
        top5_memoryVectors = [self.memoryVectors[i] for i in top5_indices]
        return top5_memoryVectors

    def clearMemoryVector(self):
        self.memoryVectors = []

    def saveMemoryVector(self):
        with open("memory_vectors.csv", "w", encoding="utf-8") as f:
            for memoryVector in self.memoryVectors:
                f.write(memoryVector + "\n")
    
    def loadMemoryVector(self):
        self.memoryVectors = []
        if os.path.exists("memory_vectors.csv"):
            with open("memory_vectors.csv", "r", encoding="utf-8") as f:
                for line in f:
                    self.memoryVectors.append(line.strip())