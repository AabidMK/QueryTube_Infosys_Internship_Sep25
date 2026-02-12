import os
import sys
import time
from chromadb import PersistentClient
from sentence_transformers import SentenceTransformer

# --- Configuration (Must match the setup used for indexing) ---
# Path where the persistent ChromaDB collection was saved
CHROMA_BASE_PATH = r"C:\Users\dream\Desktop\Internships\Infosys Springboard\QueryTube\Task 5_ Merging Metadata & Transcripts\Storing_in_ChromaDB"
CHROMA_DB_PATH = os.path.join(CHROMA_BASE_PATH, "ChromaDB_Collection")
COLLECTION_NAME = "youtube_analysis_collection"

# --- 1. Query Input Handling ---

def query_input_handler():
    """Accepts natural language input from the user."""
    if sys.stdin.isatty():
        query = input("\n[SEARCH] Enter your natural language query (or type 'exit'): ")
    else:
        # Default query if running non-interactively
        query = "best tips for a new software developer career"
    
    # Simple validation/preprocessing
    return query.strip()

# --- 2. 3. & 4. Search and Formatting Logic ---

def perform_semantic_search(client, query, top_k=5):
    """
    Generates query embedding, performs semantic search, and formats results.
    """
    print(f"\n--- PERFORMING SEMANTIC SEARCH ---")
    
    try:
        # Retrieve the existing collection
        collection = client.get_collection(name=COLLECTION_NAME)
    except Exception as e:
        print(f"Error accessing collection '{COLLECTION_NAME}': {e}")
        return None

    # ChromaDB handles the query embedding (Step 2) and performs the search (Step 3) internally.
    start_time = time.time()
    results = collection.query(
        query_texts=[query],
        n_results=top_k,
        include=['metadatas', 'distances'] # Include scores and metadata (Step 3)
    )
    end_time = time.time()
    print(f"-> Search complete in {end_time - start_time:.4f} seconds.")
    
    # 4. Format Results
    formatted_results = []
    
    if results and results.get('metadatas') and len(results['metadatas'][0]) > 0:
        metadatas = results['metadatas'][0]
        distances = results['distances'][0]
        
        for i, (metadata, distance) in enumerate(zip(metadatas, distances)):
            # Convert cosine distance (0=same, 1=different) to similarity (1=same, 0=different)
            similarity = 1.0 - distance 
            
            formatted_results.append({
                'rank': i + 1,
                'title': metadata.get('title', 'N/A'),
                'channel': metadata.get('channel_title', 'N/A'),
                'views': metadata.get('viewCount', 0),
                'likes': metadata.get('likeCount', 0),
                'similarity_score': similarity
            })
            
    return formatted_results

# --- 5. Display Results ---

def display_results(results, query):
    """Shows the search results to the user in a readable format."""
    print(f"Search Query: '{query}'\n")
    
    if not results:
        print("No relevant results found.")
        return

    # Use pandas for clean tabular printing
    display_df = pd.DataFrame(results)
    
    # Format similarity score to a percentage-like string
    display_df['Similarity'] = display_df['similarity_score'].apply(lambda x: f"{x:.4f}")
    
    # Select and order columns for display
    display_columns = ['rank', 'Similarity', 'title', 'channel', 'views', 'likes']
    
    print(display_df[display_columns].to_markdown(
        index=False, 
        numalign="left", 
        stralign="left"
    ))


def main():
    """Initializes the client and runs the interactive search loop."""
    print("--- CHROMA DB SEMANTIC SEARCH INITIATED ---")
    print(f"Database Path: {CHROMA_DB_PATH}")

    # Initialize client to load the existing database
    if not os.path.exists(CHROMA_DB_PATH):
        print(f"FATAL ERROR: ChromaDB collection not found at {CHROMA_DB_PATH}.")
        print("Please ensure you run the data indexing/storage script first.")
        return
        
    chroma_client = PersistentClient(path=CHROMA_DB_PATH)
    
    # Interactive Search Loop
    while True:
        query = query_input_handler()
        
        if query.lower() in ['exit', 'quit']:
            print("Exiting search mode. Goodbye!")
            break
        
        if not query:
            continue
            
        results = perform_semantic_search(chroma_client, query, top_k=5)
        display_results(results, query)

if __name__ == "__main__":
    # Ensure pandas is available for display
    try:
        import pandas as pd
    except ImportError:
        print("FATAL ERROR: pandas is required for display. Please install with 'pip install pandas'.")
        sys.exit(1)
        
    main()
