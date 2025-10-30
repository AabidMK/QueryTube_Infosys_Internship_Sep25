"""
ChromaDB Storage Script
Purpose: Load embeddings from CSV/Parquet and store in ChromaDB for semantic search
"""

import pandas as pd
import chromadb
import ast
from pathlib import Path
import sys

def load_embeddings_from_file(file_path, embedding_column='embedding'):
    """
    Load dataset with embeddings from CSV or Parquet file
    
    Args:
        file_path: Path to the CSV or Parquet file
        embedding_column: Name of the column containing embeddings
    
    Returns:
        DataFrame with embeddings and metadata
    """
    print(f"Loading data from {file_path}...")
    
    file_extension = Path(file_path).suffix.lower()
    
    if file_extension == '.csv':
        df = pd.read_csv(file_path)
    elif file_extension == '.parquet':
        df = pd.read_parquet(file_path)
    else:
        raise ValueError(f"Unsupported file format: {file_extension}. Use .csv or .parquet")
    
    print(f"Loaded {len(df)} records")
    
    # Convert string representations of lists to actual lists if needed
    if df[embedding_column].dtype == 'object':
        print("Converting embeddings from string to list format...")
        df[embedding_column] = df[embedding_column].apply(ast.literal_eval)
    
    return df

def initialize_chromadb(persist_directory='./chromadb_data', collection_name='video_embeddings'):
    """
    Initialize ChromaDB client and create/get collection
    
    Args:
        persist_directory: Directory path for persistent storage
        collection_name: Name of the collection
    
    Returns:
        ChromaDB collection object
    """
    print(f"Initializing ChromaDB at {persist_directory}...")
    
    # Create persistent client
    client = chromadb.PersistentClient(path=persist_directory)
    
    # Create or get collection with cosine similarity
    collection = client.get_or_create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"}  # Use cosine similarity for semantic search
    )
    
    print(f"Collection '{collection_name}' initialized (Total existing items: {collection.count()})")
    
    return collection

def add_embeddings_to_chromadb(df, collection, batch_size=100):
    """
    Add embeddings and metadata to ChromaDB collection in batches
    
    Args:
        df: DataFrame containing embeddings and metadata
        collection: ChromaDB collection object
        batch_size: Number of records to process in each batch
    """
    print(f"Adding {len(df)} embeddings to ChromaDB...")
    
    # Required columns
    required_columns = ['video_id', 'title', 'transcript', 'embedding']
    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")
    
    # Process in batches for efficiency
    total_batches = (len(df) + batch_size - 1) // batch_size
    
    for i in range(0, len(df), batch_size):
        batch_df = df.iloc[i:i+batch_size]
        batch_num = i // batch_size + 1
        
        # Prepare batch data
        embeddings = batch_df['embedding'].tolist()
        ids = batch_df['video_id'].astype(str).tolist()
        metadatas = batch_df[['video_id', 'title', 'transcript']].to_dict('records')
        
        # Add to collection
        collection.add(
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )
        
        print(f"Processed batch {batch_num}/{total_batches} ({len(batch_df)} records)")
    
    print(f"✓ Successfully added all embeddings. Total items in collection: {collection.count()}")

def verify_storage(collection, num_samples=3):
    """
    Verify that data was stored correctly by retrieving sample records
    
    Args:
        collection: ChromaDB collection object
        num_samples: Number of sample records to retrieve
    """
    print(f"\nVerifying storage with {num_samples} sample records...")
    
    try:
        results = collection.peek(limit=num_samples)
        print(f"✓ Successfully retrieved {len(results['ids'])} sample records")
        
        for i, (id_, metadata) in enumerate(zip(results['ids'], results['metadatas'])):
            print(f"\nSample {i+1}:")
            print(f"  ID: {id_}")
            print(f"  Title: {metadata.get('title', 'N/A')[:60]}...")
            print(f"  Video ID: {metadata.get('video_id', 'N/A')}")
        
    except Exception as e:
        print(f"✗ Verification failed: {str(e)}")

def main():
    """
    Main execution function
    """
    # Configuration
    INPUT_FILE = r'C:\Users\balak\OneDrive\Desktop\Youtube_Query\videos_with_embeddings.csv'  # Change to your file path
    PERSIST_DIR = r'C:\Users\balak\OneDrive\Desktop\Youtube_Query\chromadb_data'
    COLLECTION_NAME = 'video_embeddings'
    BATCH_SIZE = 100
    
    try:
        # Step 1: Load dataset with embeddings
        df = load_embeddings_from_file(INPUT_FILE)
        
        # Step 2: Initialize ChromaDB collection
        collection = initialize_chromadb(PERSIST_DIR, COLLECTION_NAME)
        
        # Step 3: Add embeddings and metadata to collection
        add_embeddings_to_chromadb(df, collection, batch_size=BATCH_SIZE)
        
        # Step 4: Verify storage (collection is auto-saved with PersistentClient)
        verify_storage(collection)
        
        print(f"\n{'='*60}")
        print("✓ ChromaDB storage completed successfully!")
        print(f"Location: {PERSIST_DIR}")
        print(f"Collection: {COLLECTION_NAME}")
        print(f"Total records: {collection.count()}")
        print(f"{'='*60}")
        
    except FileNotFoundError:
        print(f"✗ Error: File '{INPUT_FILE}' not found.")
        print("Please update INPUT_FILE variable with correct path.")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Error occurred: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
