import chromadb

# --- Configuration ---
DB_PATH = "./chroma_db"
COLLECTION_NAME = "video_embeddings"
# Number of results to return
TOP_N_RESULTS = 5

def search_collection(query_text: str):
    """
    Performs a similarity search on the ChromaDB collection with a given text query.
    """
    if not query_text or not query_text.strip():
        print("❌ Please enter a valid search query.")
        return

    print(f"\n--- Searching for: '{query_text}' ---")

    # 1. Connect to the ChromaDB client and get the collection
    try:
        client = chromadb.PersistentClient(path=DB_PATH)
        collection = client.get_collection(name=COLLECTION_NAME)
    except Exception as e:
        print(f"❌ Error connecting to ChromaDB or finding collection: {e}")
        return

    # 2. Perform the query
    results = collection.query(
        query_texts=[query_text],
        n_results=TOP_N_RESULTS,
        include=["metadatas", "distances"]
    )

    if not results['ids'][0]:
        print("No results found for your query.")
        return

    # 3. Process and display the results
    distances = results['distances'][0]
    metadatas = results['metadatas'][0]

    for i, (metadata, dist) in enumerate(zip(metadatas, distances)):
        video_title = metadata.get('title', 'N/A')
        channel_title = metadata.get('channel_title', 'N/A')
        video_id = metadata.get('id', '')
        yt_link = f"https://www.youtube.com/watch?v={video_id}" if video_id else "N/A"

        print(f"\n--- Result {i+1} ---")
        print(f"Video Title: {video_title}")
        print(f"Channel Title: {channel_title}")
        print(f"YT link: {yt_link}")
        print(f"Distance Score: {dist:.4f}")

if __name__ == "__main__":
    print("--- ChromaDB Interactive Video Search ---")
    print("Enter your search query below. Type 'exit' to quit.")
    
    # 4. Start an infinite loop to keep asking for input
    while True:
        # Prompt the user for input at runtime
        user_query = input("\n🔎 Enter search query: ")
        
        # 5. Check if the user wants to exit
        if user_query.lower() == 'exit':
            print("Exiting the program. Goodbye!")
            break # Exit the loop
        
        # Call the search function with the user's input
        search_collection(user_query)
        print("\n" + "="*50)