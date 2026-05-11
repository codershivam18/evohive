import chromadb
from chromadb.utils import embedding_functions
from config import config

class MemoryStore:
    def __init__(self):
        self.client = chromadb.PersistentClient(path="./evohive_memory")
        
        # Use default embedding function
        self.collection = self.client.get_or_create_collection(
            name="evohive_memory"
        )

    def add_memory(self, text: str, metadata: dict = None):
        if metadata is None:
            metadata = {}
        self.collection.add(
            documents=[text],
            metadatas=[metadata],
            ids=[f"mem_{len(self.collection.get()['ids'] or [])}"]
        )

    def search(self, query: str, n_results: int = 3):
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        return results.get('documents', [[]])[0]