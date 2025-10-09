import chromadb
from sentence_transformers import SentenceTransformer
import numpy as np

# 1. Initialize the Sentence Transformer Model for Embedding Generation
# This line downloads and loads the pre-trained model.
# The model is chosen for its balance of speed and performance.
try:
    model = SentenceTransformer('all-MiniLM-L6-v2')
    print("✅ SentenceTransformer model loaded successfully.")
except Exception as e:
    print(f"Error loading model: {e}")
    exit()

# 2. Connect to the ChromaDB Database
try:
    client = chromadb.PersistentClient(path="./chroma_db")
    collection = client.get_collection(name="video_embeddings")
    print("✅ Connected to ChromaDB collection 'video_embeddings'.")
except Exception as e:
    print(f"Error connecting to ChromaDB: {e}")
    print("Please make sure you have created the ChromaDB database using the previous script.")
    exit()

def search_videos(query, top_k=5):
    """
    Performs a semantic search on the ChromaDB collection.

    Args:
        query (str): The user's natural language search query.
        top_k (int): The number of top results to retrieve.

    Returns:
        None: Prints the formatted search results.
    """
    # --- Step 1 & 2: Input Handling and Query Embedding Generation ---
    if not query.strip():
        print("Error: Search query cannot be empty.")
        return

    # Generate the embedding for the user's query
    query_embedding = model.encode(query, convert_to_tensor=False).tolist()

    # --- Step 3: Perform Semantic Search ---
    # Use the collection's query method to find the nearest neighbors
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["metadatas", "distances"]  # We want metadata and the similarity score
    )

    # --- Step 4 & 5: Format and Display Results ---
    if not results or not results['ids'][0]:
        print("No results found for your query.")
        return

    print(f"\n🔎 Top {len(results['ids'][0])} results for: '{query}'\n" + "-"*50)

    # The results are nested in lists, so we access the first element
    ids = results['ids'][0]
    distances = results['distances'][0]
    metadatas = results['metadatas'][0]

    for rank, (video_id, score, metadata) in enumerate(zip(ids, distances, metadatas), 1):
        # The 'distance' in ChromaDB is a measure of dissimilarity.
        # We can convert it to a similarity score (0 to 1) for easier interpretation.
        # A common way is (1 - distance), but this depends on the distance metric used (default is L2).
        # For simplicity, we'll just display the raw distance score. Lower is better.
        similarity_score = 1 - score # Example conversion

        print(f"#{rank}")
        print(f"  ▶️ Title: {metadata.get('title', 'N/A')}")
        print(f"  📺 Channel: {metadata.get('channel_title', 'N/A')}")
        print(f"  ⭐ Similarity Score: {similarity_score:.4f} (Distance: {score:.4f})")
        # Uncomment the line below if you want to see the video ID
        # print(f"  Video ID: {metadata.get('id', 'N/A')}")
        print("-" * 50)


# --- Main script execution ---
if __name__ == "__main__":
    while True:
        # Accept user input for the search query
        user_query = input("Enter your search query (or type 'exit' to quit): ")
        if user_query.lower() == 'exit':
            break
        search_videos(user_query)