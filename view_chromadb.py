import chromadb
import textwrap

# --- Configuration ---
DB_PATH = "./chroma_db"
COLLECTION_NAME = "video_embeddings"
# Set how many items you want to view from the collection
VIEW_LIMIT = 5

def view_collection():
    """
    Connects to the ChromaDB collection and prints a specified number of items.
    """
    print(f"--- Attempting to view collection: '{COLLECTION_NAME}' ---")

    # 1. Connect to the ChromaDB client and get the collection
    try:
        client = chromadb.PersistentClient(path=DB_PATH)
        collection = client.get_collection(name=COLLECTION_NAME)
        print(f"✅ Successfully connected to '{COLLECTION_NAME}'.")
        print(f"Total items in collection: {collection.count()}\n")
    except Exception as e:
        print(f"❌ Error connecting to ChromaDB or finding collection: {e}")
        print("Please ensure the database exists and the collection name is correct.")
        return

    # 2. Get a number of items from the collection
    # We include 'metadatas' and 'documents' to see the information.
    # We don't need 'embeddings' for viewing purposes as they are just long lists of numbers.
    results = collection.get(
        limit=VIEW_LIMIT,
        include=["metadatas", "documents"]
    )

    if not results['ids']:
        print("The collection is empty. Nothing to display.")
        return

    # 3. Loop through the results and print them in a formatted way
    print(f"Displaying the first {len(results['ids'])} items:\n")

    for i, item_id in enumerate(results['ids']):
        metadata = results['metadatas'][i]
        document = results['documents'][i]

        # Safely get metadata fields, providing a default if a key is missing
        video_id = metadata.get('id', 'N/A')
        title = metadata.get('title', 'No Title Provided')
        channel_title = metadata.get('channel_title', 'N/A') # The new field!

        print(f"----------------------------------------")
        print(f"Entry {i+1} | ChromaDB ID: {item_id}")
        print(f"----------------------------------------")
        print(f"  ▶️  Video Title: {title}")
        print(f"  👤 Channel Title: {channel_title}")
        print(f"  🆔 YouTube ID: {video_id}")
        
        # Format the transcript for better readability
        print(f"  📄 Transcript Snippet:")
        # textwrap.indent adds a prefix to each line
        wrapped_text = textwrap.fill(document, width=80)
        indented_text = textwrap.indent(wrapped_text, '      ')
        print(indented_text[:400] + "...") # Print first 400 chars of the indented text
        print("\n")

if __name__ == "__main__":
    view_collection()