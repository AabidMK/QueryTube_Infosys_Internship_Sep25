import pandas as pd
import numpy as np
import chromadb
from sentence_transformers import SentenceTransformer
import sys
from typing import List, Dict, Optional, Any

# --- Configuration Constants ---
CHROMA_PATH = "./chromadb_data"
COLLECTION_NAME = "video_embeddings"
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"

# --- Search Engine Class ---

class VideoSearchEngine:
    """
    A reusable class to encapsulate the ChromaDB client, embedding model,
    and the core search logic for video embeddings.
    """
    def __init__(self):
        self.model: Optional[SentenceTransformer] = None
        self.client: Optional[chromadb.PersistentClient] = None
        self.collection: Optional[chromadb.Collection] = None

        print("--- Initializing VideoSearchEngine ---")
        self.load_model()
        self.connect_to_db()
        print("--- Initialization Complete ---")

    def load_model(self):
        """Loads the SBERT model for query embedding."""
        try:
            print(f"⚙️ Loading embedding model: {EMBEDDING_MODEL_NAME}...")
            # Set the model device to 'cpu' explicitly for stability in server environments
            self.model = SentenceTransformer(EMBEDDING_MODEL_NAME, device='cpu')
            print("Model loaded successfully.")
        except Exception as e:
            print(f"❌ Error loading SentenceTransformer model: {e}", file=sys.stderr)
            sys.exit(1)

    def connect_to_db(self):
        """Connects to the persistent ChromaDB collection."""
        try:
            print(f"🔎 Connecting to ChromaDB at {CHROMA_PATH}...")
            self.client = chromadb.PersistentClient(path=CHROMA_PATH)
            # Use get_collection as we expect it to exist after the loading script is run
            self.collection = self.client.get_collection(name=COLLECTION_NAME)
            print(f"ChromaDB collection '{COLLECTION_NAME}' connected.")
        except ValueError:
            print(f"❌ Error: Collection '{COLLECTION_NAME}' not found.", file=sys.stderr)
            print("Please run the data loading script ('load_data.py') first.", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"❌ Error connecting to ChromaDB: {e}", file=sys.stderr)
            sys.exit(1)

    def generate_query_embedding(self, query: str) -> np.ndarray:
        """Generates an embedding for the given query using the loaded model."""
        if self.model is None:
             raise RuntimeError("Embedding model is not loaded.")
        
        # Encode the query
        embedding = self.model.encode(query, convert_to_numpy=True)
        return embedding

    def search(self, query: str, top_k: int = 5, min_score: float = 0.2) -> List[Dict[str, Any]]:
        """
        Performs a semantic search against the ChromaDB collection.
        
        Args:
            query: The user's search string.
            top_k: The number of results to retrieve from the database.
            min_score: Minimum similarity score (0 to 1) required for a result.
            
        Returns:
            A list of formatted dictionaries containing the search results.
        """
        if self.collection is None:
            raise RuntimeError("ChromaDB collection is not available.")
            
        if not query or not query.strip():
            print("Warning: Received empty query.", file=sys.stderr)
            return []

        # 1. Generate Query Embedding
        query_embedding = self.generate_query_embedding(query)
        
        # 2. Search ChromaDB
        results = self.collection.query(
            query_embeddings=query_embedding.tolist(),
            n_results=top_k,
            include=["metadatas", "documents", "distances"]
        )
        
        # 3. Format and Filter Results
        return self._format_results(results, min_score)


    def _format_results(self, results: Dict[str, Any], min_score: float) -> List[Dict[str, Any]]:
        """Internal method to process and format raw ChromaDB results."""
        if not results or not results.get("ids") or not results["ids"][0]:
            return []

        formatted = []
        num_results = len(results["ids"][0])

        for i in range(num_results):
            distance = results["distances"][0][i]

            # Convert distance to similarity score
            score = 1 / (1 + distance)

            if score >= min_score:
                metadata = results["metadatas"][0][i]
                
                # Format the transcript preview
                transcript_text = str(metadata.get("transcript", ""))
                transcript_preview = transcript_text[:200] + "..." if len(transcript_text) > 200 else transcript_text

                data = {
                    "rank": i + 1,
                    "title": metadata.get("title", "N/A"),
                    "channel": metadata.get('channel_title', 'N/A'),
                    "video_id": metadata.get('video_id', 'N/A'),
                    "transcript_preview": transcript_preview,
                    "similarity_score": round(score, 4)
                }
                formatted.append(data)

        return formatted

# IMPORTANT: Initialize the search engine globally so the model and DB connection 
# are loaded only once when the application starts.
try:
    search_engine = VideoSearchEngine()
except SystemExit:
    # If initialization fails (e.g., DB not found), search_engine will remain uninitialized.
    search_engine = None 
