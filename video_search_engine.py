# video_search_engine.py
from sentence_transformers import SentenceTransformer
import chromadb
import numpy as np
from typing import List, Dict, Any


class VideoSearchEngine:
    def __init__(self, chroma_path: str = "./chromadb_data", collection_name: str = "video_embeddings"):
        """
        Initializes model and ChromaDB collection.
        """
        print("⚙️ Initializing VideoSearchEngine...")
        # Load embedding model once
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        # Initialize chromadb persistent client and collection
        self.client = chromadb.PersistentClient(path=chroma_path)
        self.collection = self.client.get_or_create_collection(name=collection_name)
        print("✅ Model and ChromaDB collection loaded.")

    # -------------------------
    # Utilities (moved from functions)
    # -------------------------
    def _preprocess_query(self, query: str) -> str:
        q = query.strip()
        if not q:
            raise ValueError("Query cannot be empty.")
        # preserve only alnum and spaces (same as original)
        q = ''.join(c for c in q if c.isalnum() or c.isspace())
        return q

    def _generate_embedding(self, query: str) -> np.ndarray:
        q = self._preprocess_query(query)
        # convert_to_numpy True returns numpy array
        embedding = self.model.encode(q, convert_to_numpy=True)
        # Ensure vector is 1-D numpy array
        embedding = np.asarray(embedding).reshape(-1)
        return embedding

    def _format_results(self, results: Dict[str, Any], min_score: float = 0.2) -> List[Dict[str, Any]]:
        """
        Format chromadb results to the structure we used earlier.
        Assumes results comes with keys: 'ids', 'metadatas', 'documents', 'distances'.
        """
        formatted = []
        # defensive checks
        if not results or "ids" not in results or not results["ids"]:
            return formatted

        # results["distances"][0] is distances list for the single query
        distances_list = results.get("distances", [[]])[0]
        metadatas_list = results.get("metadatas", [[]])[0]

        for i in range(len(distances_list)):
            dist = distances_list[i]
            # Convert distance -> similarity (same as original script)
            score = 1 / (1 + dist) if dist is not None else 0.0
            if score >= min_score:
                meta = metadatas_list[i] if i < len(metadatas_list) else {}
                # transcript preview safe
                transcript = meta.get("transcript", "")
                if transcript is None:
                    transcript = ""
                preview = (transcript[:200] + "...") if len(transcript) > 200 else transcript

                data = {
                    "rank": i + 1,
                    "title": meta.get("title", "N/A"),
                    "channel": meta.get("channel_title", "N/A"),
                    "video_id": meta.get("id", None),
                    "similarity_score": round(float(score), 3),
                    "transcript": preview
                }
                formatted.append(data)
        return formatted

    # -------------------------
    # Public API
    # -------------------------
    def search(self, query: str, top_k: int = 5, min_score: float = 0.2) -> List[Dict[str, Any]]:
        """
        Perform semantic search and return formatted results list.
        This is the method your FastAPI app should call.
        """
        embedding = self._generate_embedding(query)
        # IMPORTANT: chromadb expects a list of query embeddings
        results = self.collection.query(
            query_embeddings=[embedding.tolist()],
            n_results=top_k,
            include=["metadatas", "documents", "distances"]
        )
        formatted = self._format_results(results, min_score=min_score)
        return formatted

    # -------------------------
    # CLI helper (preserve terminal behavior)
    # -------------------------
    def interactive_search(self):
        """
        Replicates your original script behavior for terminal usage.
        """
        try:
            query = input("🔍 Enter your search query: ").strip()
            if not query:
                raise ValueError("❌ Query cannot be empty. Please enter a valid search term.")
            print("⚙️ Generating embedding...")
            embedding = self._generate_embedding(query)
            print("🔎 Querying ChromaDB...")
            results = self.collection.query(
                query_embeddings=[embedding.tolist()],
                n_results=5,
                include=["metadatas", "documents", "distances"]
            )
            formatted = self._format_results(results, min_score=0.2)
            self.display_results(formatted)
        except Exception as e:
            print(f"⚠️ Error: {e}")

    def display_results(self, formatted_results: List[Dict[str, Any]]):
        """
        Print results to terminal like your original script.
        """
        if not formatted_results:
            print("❌ No relevant results found.")
            return
        print("\n🎯 Top Search Results:")
        for r in formatted_results:
            print(f"\nRank {r['rank']}")
            print(f"Video ID: {r.get('video_id', 'N/A')}")
            print(f"Channel: {r.get('channel', 'N/A')}")
            print(f"Title: {r.get('title', 'N/A')}")
            print(f"Similarity Score: {r.get('similarity_score', 0.0)}")
            print(f"Transcript (Preview): {r.get('transcript', '')}")


# When run directly, fall back to interactive CLI (like original script)
if __name__ == "__main__":
    engine = VideoSearchEngine()
    engine.interactive_search()
