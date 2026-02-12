import pandas as pd
import os
import time
from chromadb import PersistentClient
from tqdm import tqdm

# --- Configuration ---
INPUT_PATH = r"C:\Users\dream\Desktop\Internships\Infosys Springboard\QueryTube\Task 5_ Merging Metadata & Transcripts\Embedding\Embedded_Merged_Dataset.parquet"
OUTPUT_DIR = r"C:\Users\dream\Desktop\Internships\Infosys Springboard\QueryTube\Task 5_ Merging Metadata & Transcripts\Storing_in_ChromaDB"
CHROMA_DB_PATH = os.path.join(OUTPUT_DIR, "ChromaDB_Collection_Updated")
COLLECTION_NAME = "youtube_analysis_collection"

def load_embedded_data():
    print("--- 1. LOADING EMBEDDED DATA ---")
    try:
        df = pd.read_parquet(INPUT_PATH)
        print(f"Loaded embedded data from: {INPUT_PATH}")
        
        # Display available columns for verification
        print("\nAvailable columns in the dataset:")
        print(df.columns.tolist())
        
        return df
    except Exception as e:
        print(f"FATAL ERROR: Could not load data. {e}")
        return None

def store_in_chroma(df):
    print("\n--- 2. STORING IN CHROMADB ---")
    
    # Create a copy of the dataframe to avoid modifying the original
    df = df.copy()
    
    # Handle duplicate IDs by adding a suffix
    if len(df['id']) != len(df['id'].unique()):
        print(f"Found {len(df) - len(df['id'].unique())} duplicate IDs. Adding suffixes to make them unique...")
        # Create a new column to store the original ID
        df['original_id'] = df['id']
        # Add a suffix to duplicate IDs to make them unique
        df['id'] = df.groupby('id').cumcount().astype(str) + '_' + df['id']
        print("-> Duplicate IDs have been made unique.")
    else:
        df['original_id'] = df['id']  # Still keep original ID for reference
    start_time = time.time()
    
    # 1. Initialize Persistent ChromaDB Client
    os.makedirs(CHROMA_DB_PATH, exist_ok=True)
    client = PersistentClient(path=CHROMA_DB_PATH)
    print(f"-> ChromaDB client initialized. Database will be saved in: {CHROMA_DB_PATH}")

    # 2. Get/Create Collection (Overwrite if already exists)
    try:
        client.delete_collection(name=COLLECTION_NAME)
    except Exception:
        pass
        
    collection = client.create_collection(name=COLLECTION_NAME)
    
    # 3. Prepare data for ChromaDB format
    documents = df['text_for_embedding'].tolist()
    ids = df['id'].astype(str).tolist()
    embeddings = df['embedding_vector'].tolist()
    
    # Include all available columns except the ones we don't want in metadata
    exclude_columns = ['text_for_embedding', 'embedding_vector']
    available_columns = [col for col in df.columns if col not in exclude_columns]
    
    print(f"\nIncluding these columns as metadata: {available_columns}")
    
    # Convert to list of metadata dictionaries
    metadata_list = df[available_columns].astype(str).to_dict('records')
    
    # Ensure all metadata values are strings (ChromaDB requirement)
    for meta in metadata_list:
        for key, value in meta.items():
            if pd.isna(value) or value == 'nan':
                meta[key] = ''  # Replace NaN with empty string
    
    # 4. Add data to the collection with chunking
    print(f"\n-> Adding {len(ids)} documents and embeddings to ChromaDB...")
    chunk_size = 500
    
    for i in tqdm(range(0, len(ids), chunk_size), desc="ChromaDB Insertion"):
        end_idx = min(i + chunk_size, len(ids))
        collection.add(
            embeddings=embeddings[i:end_idx],
            documents=documents[i:end_idx],
            metadatas=metadata_list[i:end_idx],
            ids=ids[i:end_idx]
        )
    
    end_time = time.time()
    print(f"\n-> Successfully stored {collection.count()} documents in collection '{COLLECTION_NAME}'.")
    print(f"-> Storage complete in {end_time - start_time:.2f} seconds.")
    
    # 5. Verify the data was stored correctly
    print("\n--- 3. VERIFICATION ---")
    if collection.count() > 0:
        sample = collection.get(limit=1)
        print("\nSample stored metadata:")
        print(sample['metadatas'][0])
    
    return collection

def main():
    # Load the data
    df = load_embedded_data()
    if df is None:
        return
    
    # Store in ChromaDB
    collection = store_in_chroma(df)
    
    if collection and collection.count() > 0:
        print("\n--- CHROMADB STORAGE COMPLETE ---")
        print(f"Collection '{COLLECTION_NAME}' is ready at: {CHROMA_DB_PATH}")

if __name__ == "__main__":
    main()
