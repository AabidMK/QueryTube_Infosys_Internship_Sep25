import pandas as pd
import os
import time
from chromadb import PersistentClient
from tqdm import tqdm
import ast # Required to safely convert the embedding_vector string back to a list
import numpy as np # Import NumPy to handle array strings

# --- Configuration ---
# 1. Input File Path (The dataset with the 'embedding_vector' column)
# Corrected to where the embedding script saved the file (Task 5_ Merging Metadata & Transcripts\Embedding)
INPUT_PATH = r"C:\Users\dream\Desktop\Internships\Infosys Springboard\QueryTube\Task 5_ Merging Metadata & Transcripts\Embedding\Embedded_Merged_Dataset.parquet"

# 2. Output Path for the ChromaDB persistence (The database itself)
# Corrected to the user's specified location for the ChromaDB folder
OUTPUT_DIR = r"C:\Users\dream\Desktop\Internships\Infosys Springboard\QueryTube\Task 5_ Merging Metadata & Transcripts\Storing_in_ChromaDB"
CHROMA_DB_PATH = os.path.join(OUTPUT_DIR, "ChromaDB_Collection")
COLLECTION_NAME = "youtube_analysis_collection"

def load_embedded_data():
    """
    Loads the Parquet file and prepares the data structures for ChromaDB insertion.
    """
    print("--- 1. LOADING EMBEDDED DATA ---")
    try:
        # Load the Parquet file
        df = pd.read_parquet(INPUT_PATH)
        print(f"Loaded embedded data from: {INPUT_PATH}")
    except FileNotFoundError:
        print(f"FATAL ERROR: Embedded file not found at {INPUT_PATH}. Please run the embedding step first.")
        return None
    except Exception as e:
        print(f"FATAL ERROR: Could not load data. Ensure 'pyarrow' is installed if using Parquet. {e}")
        return None
    
    # --- FIX 1: Deduplication ---
    initial_count = len(df)
    df.drop_duplicates(subset=['id'], keep='first', inplace=True)
    dedup_count = len(df)
    
    if initial_count != dedup_count:
        print(f"-> Detected and removed {initial_count - dedup_count} duplicate 'id' records.")
        print(f"-> Remaining unique records: {dedup_count}")

    # --- FIX 2: Handle NaN in Metadata (The fix for the TypeError) ---
    # Fill NaN values in numerical columns with 0, and convert them to integers
    count_columns = ['viewCount', 'likeCount', 'commentCount']
    df[count_columns] = df[count_columns].fillna(0).astype(int)
    
    # Fill NaN values in string/datetime columns with an empty string
    string_columns = ['title', 'channel_title', 'publishedAt']
    df[string_columns] = df[string_columns].fillna('')

    print("-> Metadata NaN values successfully handled.")

    # Crucial step: Convert the embedding vector (which is a NumPy array object) 
    # back into a standard Python list of floats for ChromaDB.
    print("-> Converting NumPy arrays to Python lists...")
    
    # We use .apply(lambda x: x.tolist()) to safely convert each NumPy array object 
    # in the series to a standard Python list.
    df['embedding_vector'] = df['embedding_vector'].apply(lambda x: x.tolist())
    
    # Remove the temporary 'text_for_embedding' column as we can reconstruct it, 
    # but let's keep it simple for now, as it's the core document.
    
    print(f"-> Data Ready. Total {len(df)} records to be indexed.")
    return df

def store_in_chroma(df):
    """
    Initializes ChromaDB, stores the embeddings and metadata, and performs a test query.
    """
    print(f"\n--- 2. STORING IN CHROMADB ---")
    start_time = time.time()
    
    # 1. Initialize Persistent ChromaDB Client
    # This creates the necessary folders if they don't exist
    os.makedirs(CHROMA_DB_PATH, exist_ok=True)
    client = PersistentClient(path=CHROMA_DB_PATH)
    print(f"-> ChromaDB client initialized. Database will be saved in: {CHROMA_DB_PATH}")

    # 2. Get/Create Collection (Overwrite if already exists to ensure a clean insert)
    # The 'get_or_create' method is robust, but removing the collection ensures a fresh start.
    try:
        client.delete_collection(name=COLLECTION_NAME)
    except Exception:
        # Ignore error if collection does not exist
        pass
        
    collection = client.create_collection(name=COLLECTION_NAME)
    
    # 3. Prepare data for ChromaDB format
    documents = df['text_for_embedding'].tolist()
    ids = df['id'].astype(str).tolist()
    embeddings = df['embedding_vector'].tolist() # This is already a list of lists

    # Metadata dictionaries for each document
    # Note: The fillna logic in load_embedded_data ensures no NaNs reach here.
    metadata_list = df[['title', 'channel_title', 'publishedAt', 'viewCount', 'likeCount', 'commentCount']].to_dict('records')
    
    # 4. Add data to the collection
    print(f"-> Adding {len(ids)} documents and embeddings to ChromaDB...")
    
    # Chunking the insertion is recommended for large datasets
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
    print(f"-> Successfully stored {collection.count()} documents in collection '{COLLECTION_NAME}'.")
    print(f"-> Storage complete in {end_time - start_time:.2f} seconds.")
    
    # --- 3. Verification Query ---
    print("\n--- ChromaDB Verification Query (Top 1 result) ---")
    # This tests the database is working by performing a semantic search
    results = collection.query(
        query_texts=["best tips for a new software developer career"],
        n_results=1,
        include=['documents', 'metadatas', 'distances']
    )
    
    if results and results.get('documents') and len(results['documents'][0]) > 0:
        # Extracting the first element from the lists in the results dictionary
        first_result_metadata = results['metadatas'][0][0]
        
        print(f"Query Text: 'best tips for a new software developer career'")
        print(f"Result Title: {first_result_metadata.get('title', 'N/A')}")
        print(f"Result Channel: {first_result_metadata.get('channel_title', 'N/A')}")
        print(f"Result Distance (Lower is better): {results['distances'][0][0]:.4f}")
    else:
        print("Verification query failed. Check data integrity.")

def main():
    """
    Runs the ChromaDB storage pipeline.
    """
    
    # 1. Load Data
    data_df = load_embedded_data()
    if data_df is None:
        return

    # 2. Store Data
    store_in_chroma(data_df)
    
    print("\n\nPIPELINE COMPLETE: Your data is fully indexed in ChromaDB and ready for semantic search!")

if __name__ == "__main__":
    main()
