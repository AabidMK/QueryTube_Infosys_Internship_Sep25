import chromadb
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import Optional # FIX: Import Optional for type hinting

class VideoSearchEngine:
    def __init__(self):
        print("🚀 Initializing SentenceTransformer model and ChromaDB client...")
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.client = chromadb.PersistentClient(path="./chroma_db")
        self.collection = self.client.get_or_create_collection(name="youtube_videos")
        print("✅ VideoSearchEngine ready.")

    def search(self, query: str, top_k: int = 5, category_id: Optional[int] = None):
        """
        Perform semantic search in ChromaDB with optional category filter.
        """
        if not query or not query.strip():
            raise ValueError("Query cannot be empty.")

        # Generate embedding for the query
        query_embedding = self.model.encode(query, convert_to_numpy=True)

        # Build filter dictionary if categoryId is provided
        query_filter = None
        if category_id is not None:
            # Note: ChromaDB stores metadata values as strings/numbers/bools. 
            # If categoryId was stored as a string, filter must match the type.
            query_filter = {"categoryId": str(category_id)} 
            # Using $eq is robust for simple string matching, 
            # but for simplicity, we rely on exact match structure if it's not needed.

        # Perform search in ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=top_k, 
            include=["metadatas", "documents", "distances"],
            where=query_filter
        )

        final_results = []
        if results and results["ids"]:
            for i in range(len(results["ids"][0])):
                metadata = results["metadatas"][0][i]
                distance = results["distances"][0][i]
                similarity_score = round(1 - distance, 3)

                # Get duration safely and convert to string to match FastAPI Pydantic model
                duration_value = metadata.get("duration", "")
                if duration_value is not None:
                    duration_str = str(duration_value)
                else:
                    duration_str = ""
                
                # Extract all metadata fields
                final_results.append({
                    "rank": i + 1,
                    "title": metadata.get("title", "N/A"),
                    "channel": metadata.get("channel_title", "Unknown"),
                    "similarity_score": similarity_score,
                    "transcript": metadata.get("transcript", ""),
                    "video_id": metadata.get("video_id", ""),
                    "published_at": metadata.get("publishedAt", ""),
                    "thumbnail_high": metadata.get("thumbnail_high", ""),
                    "duration": duration_str, # FIX APPLIED HERE
                    "view_count": metadata.get("viewCount", 0),
                    "like_count": metadata.get("likeCount", 0),
                    "category_id": metadata.get("categoryId", 0)
                })

        return final_results
