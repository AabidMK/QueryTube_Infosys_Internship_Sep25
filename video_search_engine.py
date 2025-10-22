from sentence_transformers import SentenceTransformer
import chromadb
import numpy as np
import json
import time


class VideoSearchEngine:
    def __init__(self, db_path: str = "./chroma_db", model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the semantic video search engine.
        """
        start_time = time.time()
        print("🚀 Initializing Video Search Engine...")

        # Persistent ChromaDB client
        self.client = chromadb.PersistentClient(path=db_path)
        self.collection = self.client.get_or_create_collection(name="youtube_videos")

        # Load embedding model
        self.model = SentenceTransformer(model_name)

        print(f"✅ Model and database loaded successfully in {time.time() - start_time:.2f}s")

    def search(self, query: str, top_k: int = 5):
        """
        Perform semantic search for YouTube videos using embeddings.
        Returns a list of results with title, channel, link, similarity score, etc.
        """
        if not query or not query.strip():
            raise ValueError("❌ Query cannot be empty")

        print(f"\n🔍 Searching for: '{query}' (top_k={top_k})")

        # Encode query
        query_embedding = self.model.encode(query.strip().lower())

        # Query ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=top_k
        )

        # Handle case where no results are found
        if not results.get("metadatas") or not results["metadatas"][0]:
            print("⚠️ No matching results found in the database.")
            return {"results": []}

        formatted_results = []
        for idx, metadata in enumerate(results["metadatas"][0]):
            # Extract distance (lower = more similar)
            distance = float(results["distances"][0][idx])

            # Convert distance to similarity (bounded 0–1)
            similarity = round(1 / (1 + distance), 4)

            # Extract fields
            video_title = metadata.get("title", "Untitled Video")
            channel_title = metadata.get("channel", "Unknown Channel")
            description = metadata.get("description", "No description available.")
            yt_link = metadata.get("url", "")

            # ✅ Thumbnail selection logic
            thumbnail_high = metadata.get("thumbnail_high")
            thumbnail_default = metadata.get("thumbnail_default")

            if thumbnail_high:
                thumbnail = thumbnail_high
            elif thumbnail_default:
                thumbnail = thumbnail_default
            elif "v=" in yt_link:  # fallback: generate from YouTube ID
                yt_id = yt_link.split("v=")[-1]
                thumbnail = f"https://img.youtube.com/vi/{yt_id}/hqdefault.jpg"
            else:
                thumbnail = "https://via.placeholder.com/320x180?text=No+Thumbnail"

            formatted_results.append({
                "video_title": video_title,
                "channel_title": channel_title,
                "description": description,
                "thumbnail": thumbnail,
                "yt_link": yt_link,
                "similarity_score": similarity
            })

        print(f"✅ Found {len(formatted_results)} results.")
        return {"results": formatted_results}


# ✅ Optional direct test
if __name__ == "__main__":
    engine = VideoSearchEngine()
    query = "Artificial intelligence"
    results = engine.search(query, top_k=3)
    print(json.dumps(results, indent=4))
