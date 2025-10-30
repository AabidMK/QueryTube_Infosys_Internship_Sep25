# VideoSearchEngine.py
import chromadb

class VideoSearchEngine:
    def __init__(self, chroma_client: chromadb.Client, collection_name: str):
        """Initialize with a Chroma client and collection name."""
        self.client = chroma_client
        self.collection = self.client.get_or_create_collection(name=collection_name)

    def search(self, query: str, top_k: int = 5):
        """Perform semantic search using Chroma."""
        results = self.collection.query(
            query_texts=[query],
            n_results=top_k
        )
        return results
