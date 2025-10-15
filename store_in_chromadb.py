#!/usr/bin/env python3
import argparse
import pandas as pd
import chromadb
from chromadb.config import Settings
from tqdm.auto import tqdm
import ast
import os

def main():
    parser = argparse.ArgumentParser(description="Store embeddings and metadata in ChromaDB")
    parser.add_argument("--input_parquet", required=True, help="Path to Parquet file with embeddings")
    parser.add_argument("--persist_dir", default="chromadb_store", help="Directory to persist ChromaDB data")
    parser.add_argument("--collection_name", default="videos", help="ChromaDB collection name")
    args = parser.parse_args()

    print(f"📂 Loading dataset: {args.input_parquet}")
    df = pd.read_parquet(args.input_parquet)
    print(f"✅ Loaded {len(df)} rows")

    # Parse embedding column if stored as string
    if isinstance(df.loc[0, "embedding"], str):
        print("🔄 Parsing embeddings column...")
        df["embedding"] = df["embedding"].apply(ast.literal_eval)

    # Initialize ChromaDB client
    print(f"🧠 Initializing ChromaDB at '{args.persist_dir}' ...")
    os.makedirs(args.persist_dir, exist_ok=True)
    client = chromadb.Client(Settings(
        persist_directory=args.persist_dir
    ))

    # Create or get collection
    collection = client.get_or_create_collection(args.collection_name)
    print(f"📦 Using collection: {args.collection_name}")

    # Add embeddings in batches
    print("🚀 Inserting embeddings into ChromaDB...")
    batch_size = 50
    for i in tqdm(range(0, len(df), batch_size)):
        batch = df.iloc[i:i+batch_size]
        meta_cols = [c for c in ["video_id", "title", "transcript"] if c in batch.columns]
        metadatas = batch[meta_cols].to_dict(orient="records")

        collection.add(
            ids=batch["video_id"].astype(str).tolist(),
            embeddings=batch["embedding"].tolist(),
            metadatas=metadatas
        )

    print(f"✅ Successfully stored {len(df)} embeddings in ChromaDB.")
    print(f"📍 Persistent directory: {args.persist_dir}")


if __name__ == "__main__":
    main()
