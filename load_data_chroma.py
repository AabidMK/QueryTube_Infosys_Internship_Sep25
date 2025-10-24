import pandas as pd
import chromadb
import numpy as np 
import os
import sys

# --- Configuration ---
# CRITICAL: Ensure this CSV file is located in the same folder as this script.
FILE_NAME = "BRINDA_videos_with_embeddings_cleaned.csv" 
CHROMA_PATH = "./chromadb_data" # ChromaDB persistence data will be saved here
COLLECTION_NAME = "video_embeddings"

# --- Utility Function ---
def parse_embedding(x):
    """
    Parses a string representation of an embedding list/array back into its original format.
    Uses eval() which requires 'numpy as np' to be imported if embeddings were stored
    as numpy array strings (e.g., 'np.array([...])').
    """
    if isinstance(x, str) and x.strip().startswith('['):
        try:
            # We use eval() to safely convert the string representation back to a list/array
            return eval(x)
        except Exception as e:
            # Log the error to stderr for better terminal visibility
            print(f"Error evaluating embedding string (Partial Data: {x[:50]}... Error: {e})", file=sys.stderr)
            return [] 
    
    # Handle cases where data might already be an array/list (useful if processing in chunks)
    elif isinstance(x, list) or isinstance(x, np.ndarray):
        return x
    
    return [] 

# --- Main Loading Script ---
def load_data_to_chromadb():
    """Loads data from the CSV file into a ChromaDB persistent collection."""
    
    # 1. Load Data
    try:
        print(f"Loading dataset from: {FILE_NAME}")
        df = pd.read_csv(FILE_NAME)
        print(f"Dataset loaded with {len(df)} rows.")

    except FileNotFoundError:
        # User feedback for local file path error
        print(f"Error: File '{FILE_NAME}' not found.", file=sys.stderr)
        print("Please ensure the CSV file is in the same folder as 'load_data.py'.", file=sys.stderr)
        return
    except Exception as e:
        print(f"An error occurred during file loading: {e}", file=sys.stderr)
        return

    # 2. Initialize ChromaDB client
    print(f"Initializing ChromaDB PersistentClient at {CHROMA_PATH}...")
    try:
        client = chromadb.PersistentClient(path=CHROMA_PATH)
    except Exception as e:
        print(f"Error initializing ChromaDB PersistentClient: {e}", file=sys.stderr)
        return
    

    # 3. Delete existing collection for a fresh start (cleaner for testing)
    try:
        if COLLECTION_NAME in [c.name for c in client.list_collections()]:
            client.delete_collection(name=COLLECTION_NAME)
            print(f"Successfully deleted existing collection '{COLLECTION_NAME}'.")
        else:
            print(f"Collection '{COLLECTION_NAME}' did not exist. Creating new collection.")
    except Exception as e:
        print(f"Warning: Error during collection deletion/check: {e}. Attempting to create new.", file=sys.stderr)

    # 4. Get or create the collection
    collection = client.get_or_create_collection(name=COLLECTION_NAME)
    print(f"ChromaDB collection '{COLLECTION_NAME}' ready.")

    # 5. Prepare and Filter Data for insertion
    ids = df['video_id'].astype(str).tolist()

    print("Parsing embeddings...")
    embeddings_raw = df['embedding'].apply(parse_embedding).tolist()

    # Filter out empty/invalid embeddings
    valid_data = [(i, e, m) 
                  for i, e, m in zip(ids, embeddings_raw, df.to_dict(orient='records')) 
                  if e and isinstance(e, (list, np.ndarray)) and len(e) > 0]

    if not valid_data:
        print("No valid embedding data found after parsing. Aborting insertion.")
        return

    ids, embeddings, metadatas_raw = zip(*valid_data)

    # Define columns for metadata
    metadata_cols = ['video_id', 'title', 'description', 'categoryId', 'duration',
                     'channel_id', 'channel_title', 'channel_description',
                     'channel_subscribercount', 'likecount', 'transcript']

    # Create final metadata dictionary list, filling NaN/None values with 'N/A'
    metadatas = []
    for record in metadatas_raw:
        metadata_item = {}
        for col in metadata_cols:
            value = record.get(col)
            # Use pandas.isna to handle various NaN types and check for None
            if pd.isna(value) or value is None:
                 metadata_item[col] = 'N/A'
            else:
                 # Ensure the value is string-based or a primitive type for ChromaDB
                 metadata_item[col] = str(value) if not isinstance(value, (str, int, float, bool)) else value
        metadatas.append(metadata_item)


    # 6. Add embeddings and metadata to the collection
    print(f"Attempting to add {len(ids)} valid documents to ChromaDB...")

    # ChromaDB insertion, ensuring embeddings are standard Python lists
    collection.add(
        ids=list(ids),
        embeddings=[list(e) for e in embeddings], 
        metadatas=metadatas
    )

    # 7. Verification
    count = collection.count()
    print("-" * 50)
    print(f"SUCCESS: Total documents stored in '{COLLECTION_NAME}': {count}")
    print(f"ChromaDB persistence data saved locally to the '{CHROMA_PATH}' folder.")
    print("-" * 50)

if __name__ == '__main__':
    load_data_to_chromadb()