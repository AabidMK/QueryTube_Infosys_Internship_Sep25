import pandas as pd
import numpy as np
import chromadb

# ============================
# Load dataset from Parquet
# ============================
merged_df = pd.read_parquet(r"D:\youtube_search_engine\Merged_Embeddings.parquet")
print(f"📦 Loaded {len(merged_df)} rows from Parquet file")

# Initialize persistent ChromaDB client
client = chromadb.PersistentClient(path="./chroma_db")

# Create or get collection
collection = client.get_or_create_collection(name="youtube_videos")

# Remove duplicate IDs
merged_df.drop_duplicates(subset=['id'], inplace=True)

# Convert embedding column safely
def parse_embedding(x):
    if isinstance(x, str):
        return np.array(eval(x))
    return np.array(x)

merged_df["embedding"] = merged_df["embedding"].apply(parse_embedding)

# Stack embeddings into a single array
embeddings = np.vstack(merged_df["embedding"].values)

# Rename columns if needed
merged_df = merged_df.rename(columns={
    "channel_title": "channel"
})

# Add YouTube link
merged_df["url"] = "https://www.youtube.com/watch?v=" + merged_df["id"].astype(str)

# ✅ Ensure these columns exist
for col in ["description", "thumbnail"]:
    if col not in merged_df.columns:
        merged_df[col] = ""

# ✅ Include description & thumbnail in metadatas
metadatas = merged_df[["title", "channel", "url", "description", "thumbnail"]].to_dict(orient="records")

# Add data to ChromaDB
collection.add(
    ids=merged_df["id"].astype(str).tolist(),
    embeddings=embeddings,
    metadatas=metadatas,
    documents=merged_df["combined_text"].astype(str).tolist()
)

print(f"✅ Stored {len(merged_df)} videos in ChromaDB collection 'youtube_videos'.")
print("🎯 Data is ready for semantic video search with thumbnails & descriptions.")
