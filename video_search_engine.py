from sentence_transformers import SentenceTransformer
import chromadb
import numpy as np


class VideoSearchEngine:
    def __init__(self, db_path: str = "./chroma_db", model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the semantic video search engine.
        """
        print("🚀 Initializing Video Search Engine...")

        # Connect to persistent ChromaDB client
        self.client = chromadb.PersistentClient(path=db_path)
        self.collection = self.client.get_or_create_collection(name="youtube_videos")

        # Load the SentenceTransformer model
        self.model = SentenceTransformer(model_name)
        print("✅ Model and database loaded successfully!")

    def search(self, query: str, top_k: int = 5):
        """
        Perform semantic search on the video transcripts and return formatted results.
        """
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")

        # Encode query into embedding
        query_embedding = self.model.encode(query.strip().lower())

        # ✅ FIX: Removed `ids` from include list
        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=top_k,
            include=["metadatas", "documents", "distances"]
        )

        # ✅ Extract results safely
        metadatas = results.get("metadatas", [[]])[0] if results.get("metadatas") else []
        distances = results.get("distances", [[]])[0] if results.get("distances") else []
        ids = results.get("ids", [[]])[0] if results.get("ids") else []

        if not metadatas:
            return []

        formatted_results = []
        for idx, metadata in enumerate(metadatas):
            video_id = (
                metadata.get("video_id") or
                (ids[idx] if idx < len(ids) else None) or
                "unknown"
            )
            distance = distances[idx] if idx < len(distances) else 1.0
            similarity = round(1 / (1 + distance), 3)

            formatted_results.append({
                "rank": idx + 1,
                "title": metadata.get("title", "Untitled Video"),
                "video_id": video_id,
                "similarity_score": similarity,
                "transcript_preview": metadata.get("transcript", "")[:250].replace("\n", " "),
                "youtube_link": f"https://www.youtube.com/watch?v={video_id}",
                "thumbnail": f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"
            })

        return formatted_results


# ✅ Optional Test Run
if __name__ == "__main__":
    engine = VideoSearchEngine()
    query = "python tutorial for beginners"
    results = engine.search(query, top_k=3)

    if not results:
        print("⚠️ No results found. Try another query.")
    else:
        for r in results:
            print(f"{r['rank']}. {r['title']} ({r['similarity_score']})")
            print(f"🔗 {r['youtube_link']}")
            print(f"🖼️ {r['thumbnail']}")
            print(f"📜 {r['transcript_preview']}\n")
