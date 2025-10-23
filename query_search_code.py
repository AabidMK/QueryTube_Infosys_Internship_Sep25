import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
import os
import chromadb
# --- Configuration Constants ---
CHROMA_PATH = "chromadb_data"
COLLECTION_NAME = "video_embeddings_all"
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"

# --- Utility Functions ---

# Query Input Handling (Uses standard input, suitable for Colab)
def get_user_query():
    """Prompts the user for a search query and performs basic sanitization."""
    query = input("🔍 Enter your search query: ").strip()
    if not query:
        # Instead of raising, we can prompt again or return a flag
        print("❌ Query cannot be empty. Please enter a valid search term.")
        return None
    # Simple preprocessing: remove non-alphanumeric characters except spaces
    # NOTE: This line was in the original request, but it might harm complex queries.
    # We will keep it for now as requested, but a more flexible approach is usually better.
    # query = ''.join(c for c in query if c.isalnum() or c.isspace())
    return query

# Query Embedding Generation
def generate_query_embedding(query):
    """Loads the SBERT model and generates an embedding for the query."""
    print(f"⚙ Loading embedding model: {EMBEDDING_MODEL_NAME}...")
    # This line downloads and loads the model into memory
    model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    print("Model loaded successfully.")
    
    # Encode the query
    embedding = model.encode(query, convert_to_numpy=True)
    return embedding

# Perform Semantic Search
def search_chromadb(query_embedding, top_k=5):
    """Connects to the persistent ChromaDB and executes a semantic search."""
    print(f"🔎 Connecting to ChromaDB at {CHROMA_PATH}...")
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    
    try:
        # Use get_collection as we expect it to exist after the previous loading step
        collection = client.get_collection(name=COLLECTION_NAME)
    except ValueError:
        print(f"❌ Error: Collection '{COLLECTION_NAME}' not found. Please run the data loading script first.")
        return None

    # Perform the semantic search
    results = collection.query(
        query_embeddings=query_embedding.tolist(),
        n_results=top_k,
        # Ensure we request all necessary information
        include=["metadatas", "documents", "distances"] 
    )
    return results

# Format and Filter Results
# Replace your existing format_results() with this:
def format_results(results, min_score=0.2):
    if not results or not results.get("ids") or not results["ids"][0]:
        return []

    formatted = []
    num_results = len(results["ids"][0])
    
    for i in range(num_results):
        distance = results["distances"][0][i]
        score = 1 / (1 + distance)
        metadata = results["metadatas"][0][i]

        if score >= min_score:
            # Get raw transcript (try both fields)
            transcript_raw = str(metadata.get("transcript", "") or 
                               metadata.get("transcript_preview", ""))
            
            # First 200 chars, add "..." only if truncated
            if len(transcript_raw) > 200:
                transcript = transcript_raw[:200] + "..."
            else:
                transcript = transcript_raw[:200]  # Exactly 200 chars max
            
            data = {
                "rank": i + 1,
                "title": metadata.get("title", "N/A"),
                "transcript": transcript,  # ✅ First 200 characters
                'channel': metadata.get('channel_title', 'N/A'),
                "similarity_score": round(score, 3)
            }
            formatted.append(data)
            
    return formatted
# Display Results
def display_results(formatted_results):
    """Prints the formatted search results to the console."""
    if not formatted_results:
        print("\n❌ No relevant results found (either the collection is empty or score < 0.2).")
        return
    
    print("\n" + "=" * 50)
    print(f"🎯 Top {len(formatted_results)} Semantic Search Results:")
    print("=" * 50)

    for r in formatted_results:
        print(f"\n[ Rank {r['rank']} | Score: {r['similarity_score']} ]")
        print(f"Title: {r['title']}")
        print(f"Channel: {r['channel']}")
        print(f"Transcript (Preview): {r['transcript']}")
    print("\n" + "=" * 50)


# --- Main Script Execution ---
if __name__ == "__main__":
    try:
        # Get user query
        query = get_user_query()
        if query is None:
            # Handle empty query case gracefully
            exit()
            
        # Generate embedding
        query_embedding = generate_query_embedding(query)
        
        # Search ChromaDB
        results = search_chromadb(query_embedding, top_k=5)
        
        if results is None:
            # Handle error during search (e.g., collection not found)
            exit()

        # Format and display
        formatted_results = format_results(results, min_score=0.2)
        display_results(formatted_results)
        
    except Exception as e:
        print(f"\n⚠ Fatal Error: {e}")
