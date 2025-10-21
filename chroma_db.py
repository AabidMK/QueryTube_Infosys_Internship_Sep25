import pandas as pd
import numpy as np
import chromadb

# ============================
# Load dataset from Parquet
# ============================
merged_df = pd.read_parquet(r"C:\Users\sai15\OneDrive\Desktop\AI Query Engine\Merged_Embeddings.parquet")

# Initialize persistent ChromaDB client
client = chromadb.PersistentClient(path="./chroma_db")

# Create or get collection
collection = client.get_or_create_collection(name="youtube_videos")

# Remove duplicate IDs
merged_df.drop_duplicates(subset=['id'], inplace=True)

# Convert embedding column safely (if stored as string)
def parse_embedding(x):
    if isinstance(x, str):
        return np.array(eval(x))
    return np.array(x)

merged_df["embedding"] = merged_df["embedding"].apply(parse_embedding)

# Stack embeddings into a single array
embeddings = np.vstack(merged_df["embedding"].values)

# Add data to ChromaDB, including video_id in metadata
collection.add(
    ids=merged_df["id"].astype(str).tolist(),
    embeddings=embeddings,
    metadatas=[
        {
            "title": row["title"],
            "transcript": row["transcript"],
            "video_id": row["id"]
        } for _, row in merged_df.iterrows()
    ],
    documents=merged_df["combined_text"].astype(str).tolist()
)

print(f"✅ Stored {len(merged_df)} videos in ChromaDB collection 'youtube_videos'.")
print("🎯 Data is ready for semantic search queries.")
