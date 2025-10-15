import os
import time
import json
from flask import Flask, request, jsonify
from chromadb import PersistentClient
import numpy as np

# --- Configuration (Must match the setup used for indexing) ---
# Path where the persistent ChromaDB collection was saved
CHROMA_BASE_PATH = r"C:\Users\dream\Desktop\Internships\Infosys Springboard\QueryTube\Task 5_ Merging Metadata & Transcripts\Storing_in_ChromaDB"
CHROMA_DB_PATH = os.path.join(CHROMA_BASE_PATH, "ChromaDB_Collection")
COLLECTION_NAME = "youtube_analysis_collection"

# --- 2. Perform Semantic Search (Encapsulated in a class) ---

class VideoSearchEngine:
    """
    Initializes the ChromaDB client and handles all semantic search logic.
    """
    def __init__(self):
        print(f"--- Initializing ChromaDB Client and Search Engine ---")
        if not os.path.exists(CHROMA_DB_PATH):
            raise FileNotFoundError(f"FATAL ERROR: ChromaDB collection not found at {CHROMA_DB_PATH}. Run the storage script first.")
        
        # Initialize client to load the existing database persistently
        self.client = PersistentClient(path=CHROMA_DB_PATH)
        self.collection = self.client.get_collection(name=COLLECTION_NAME)
        print(f"-> Collection '{COLLECTION_NAME}' loaded successfully with {self.collection.count()} documents.")

    def search(self, query: str, top_k: int):
        """
        Accepts query/top_k, performs semantic search, and formats results.
        """
        start_time = time.time()

        # ChromaDB handles the query embedding (Step 2) and performs the search (Step 3) internally.
        results = self.collection.query(
            query_texts=[query],
            n_results=top_k,
            include=['metadatas', 'distances'] # Include scores and metadata (Step 3)
        )
        
        end_time = time.time()
        
        # 4. Format and Filter Results (The logic is similar to the previous script)
        formatted_results = []
        
        if results and results.get('metadatas') and len(results['metadatas'][0]) > 0:
            metadatas = results['metadatas'][0]
            distances = results['distances'][0]
            
            for metadata, distance in zip(metadatas, distances):
                # Convert cosine distance to similarity (1.0 = perfect match)
                similarity = 1.0 - distance 
                
                # We can optionally set a threshold here, but for an API, it's often better
                # to return the raw top_k results and let the client filter.
                
                formatted_results.append({
                    'title': metadata.get('title', 'N/A'),
                    'channel': metadata.get('channel_title', 'N/A'),
                    'published_at': metadata.get('publishedAt', 'N/A'),
                    'views': int(metadata.get('viewCount', 0)),
                    'likes': int(metadata.get('likeCount', 0)),
                    'similarity_score': round(similarity, 4)
                })
                
        # Calculate search latency
        latency = round(end_time - start_time, 4)
        
        return {
            "query": query,
            "latency_seconds": latency,
            "total_results": len(formatted_results),
            "results": formatted_results
        }

# --- 1. API Setup ---

app = Flask(__name__)
# Initialize the search engine globally so it only loads once
try:
    search_engine = VideoSearchEngine()
except FileNotFoundError as e:
    print(e)
    # Exit gracefully if the database isn't found
    search_engine = None
    
# Check for a successful startup
if search_engine:
    print("--- Flask API Ready ---")

@app.route('/search', methods=['POST'])
def search_api():
    """
    API endpoint to handle semantic search queries.
    Accepts JSON body: {"query": "...", "top_k": N}
    """
    if not search_engine:
        return jsonify({"error": "Semantic search engine not initialized. Check server logs."}), 500
        
    data = request.get_json()
    query = data.get('query')
    top_k = int(data.get('top_k', 5)) # Default to top 5 results

    # 1. Input Validation
    if not query or len(query.strip()) < 3:
        return jsonify({"error": "Invalid query provided. Query must be at least 3 characters long."}), 400

    # 2. Perform Search
    results = search_engine.search(query, top_k)

    # 3. Return JSON Response
    return jsonify(results)

if __name__ == '__main__':
    # Flask runs in debug mode by default, suitable for testing
    app.run(host='0.0.0.0', port=5000)
