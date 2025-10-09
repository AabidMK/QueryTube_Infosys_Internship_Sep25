import chromadb
import pandas as pd

# 1. Initialize the ChromaDB client
# It's crucial to point the PersistentClient to the *same path* where your database is saved.
client = chromadb.PersistentClient(path="./chroma_db")

# 2. Get the existing collection
# This accesses the collection you previously created and populated.
collection_name = "video_embeddings"
try:
    collection = client.get_collection(name=collection_name)
    print(f"Successfully connected to the '{collection_name}' collection.")
except Exception as e:
    print(f"Error: Could not get collection. Please ensure the database exists at the specified path.")
    print(e)
    exit()

# 3. View the data in the collection
# You can retrieve data using the get() method.

# --- Option A: Get a small sample of items ---
# Use the 'limit' parameter to specify how many items to retrieve.
print("\n--- Fetching a small sample (5 items) ---")
data_sample = collection.get(
    limit=5,
    include=["metadatas", "embeddings"] # Specify what you want to retrieve
)

# Let's display the retrieved data in a more readable format
if data_sample and data_sample['ids']:
    for i in range(len(data_sample['ids'])):
        print(f"\nItem ID: {data_sample['ids'][i]}")
        print(f"  Metadata: {data_sample['metadatas'][i]}")
        print(f"  Document (Transcript): {data_sample['embeddings'][i][:200]}...") # Print first 200 chars
else:
    print("No data found in the sample.")


# --- Option B: Get all items in the collection ---
# You can retrieve everything by calling get() without a limit on IDs.
# Be cautious with very large collections, as this can use a lot of memory.
print("\n--- Fetching all items ---")
all_data = collection.get(include=["metadatas"]) # Just getting metadatas for brevity
total_items = len(all_data['ids'])
print(f"Total items in collection: {total_items}")

# You can convert this data to a pandas DataFrame for easier analysis
if total_items > 0:
    df = pd.DataFrame(all_data['metadatas'])
    df['id'] = all_data['ids'] # Add the ChromaDB IDs to the dataframe
    print("\n--- All Metadatas as a Pandas DataFrame ---")
    print(df.head())


# --- Option C: Get a specific item by its ID ---
# If you know the ID of an item, you can retrieve it directly.
# Let's try to get the item with ID '0'.
print("\n--- Fetching a specific item by ID ('0') ---")
specific_item = collection.get(
    ids=['0'],
    include=["metadatas", "embeddings"]
)
print(specific_item)