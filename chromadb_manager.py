import chromadb

class ChromaDBManager:
    def __init__(self, chroma_path="chroma_db_data", collection_name="videos_collection"):
        # Connect to persistent ChromaDB
        self.client = chromadb.PersistentClient(path=chroma_path)
        try:
            self.collection = self.client.get_collection(name=collection_name)
        except:
            self.collection = self.client.create_collection(name=collection_name)

    # Query embeddings in ChromaDB
    def query_embeddings(self, query_embedding, top_k=5):
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=['metadatas', 'distances']
        )
        return results
