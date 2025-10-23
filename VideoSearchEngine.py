# videosearchengine.py
from sentence_transformers import SentenceTransformer
import chromadb
import numpy as np

class VideoSearchEngine:
    def __init__(self, collection_name="video_embeddings", db_path="chroma_db", model_name="all-MiniLM-L6-v2"):
        """Initialize ChromaDB client, collection, and sentence transformer model"""
        self.client = chromadb.PersistentClient(path=db_path)
        self.collection = self.client.get_collection(collection_name)
        self.model = SentenceTransformer(model_name)

    def generate_embedding(self, query):
        """Generate embedding for a query string"""
        embedding = self.model.encode([query])
        return np.array(embedding)

    def search(self, query, top_k=5):
        """Perform semantic search and return formatted results"""
        # Generate embedding for the query
        embedding = self.generate_embedding(query)

        # Perform ChromaDB query
        results = self.collection.query(
            query_embeddings=embedding.tolist(),
            n_results=top_k,
            include=['metadatas', 'distances']
        )

        # Safely check metadata (avoid NoneType error)
        space_type = "l2"
        if getattr(self.collection, "metadata", None):
            space_type = self.collection.metadata.get("hnsw:space", "l2")

        formatted_results = []

        # Format search results
        for meta, dist in zip(results['metadatas'][0], results['distances'][0]):
            video_id = meta.get("id", "N/A")
            title = meta.get("title", "N/A")
            channel_title = meta.get("channel_title", "N/A")
            description = meta.get("description", "No description available")

            # ✅ Always return positive similarity score
            if space_type == "cosine":
                # cosine_distance = 1 - cosine_similarity
                similarity = max(0.0, round(1 - dist, 3))
            else:  # Euclidean (l2)
                similarity = round(1 / (1 + dist), 3)

            formatted_results.append({
                "id": video_id,
                "title": title,
                "channel_title": channel_title,
                "description": description,
                "similarity": similarity,
                "distance": dist,
                "yt_link": f"https://www.youtube.com/watch?v={video_id}"
            })

        return formatted_results
