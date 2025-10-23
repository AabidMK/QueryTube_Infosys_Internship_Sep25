import pandas as pd
from sentence_transformers import SentenceTransformer
import chromadb
import numpy as np

# ---------------------------
# Load Dataset
# ---------------------------
dataset_path = "data/final_dataset_with_flag_transcript.csv"
df = pd.read_csv(dataset_path)

# Drop rows with missing transcripts
df = df.dropna(subset=['transcript'])
print(f"Dataset loaded: {len(df)} rows")

# ---------------------------
# Load Embedding Model
# ---------------------------
model = SentenceTransformer('all-MiniLM-L6-v2')

# ---------------------------
# Connect to persistent ChromaDB
# ---------------------------
client = chromadb.PersistentClient(path="chroma_db_data")
collection_name = "videos_collection"

try:
    collection = client.get_collection(name=collection_name)
    print("Collection exists, clearing old data...")
    collection.delete(where={})  # Clear existing embeddings
except:
    collection = client.create_collection(name=collection_name)
    print("Collection created")

# ---------------------------
# Prepare data and embeddings
# ---------------------------
metadatas = []
ids = []
embeddings = []

for idx, row in df.iterrows():
    ids.append(str(row['id']))
    metadatas.append({
        "video_id": str(row['id']),         # ✅ Add video_id here
        "title": row['title'],
        "channel_title": row['channel_title'],
        "transcript": row['transcript']
    })
    # Combine title + transcript for richer embedding
    text_to_embed = f"{row['title']} - {row['transcript']}"
    emb = model.encode(text_to_embed)
    embeddings.append(emb)

embeddings = np.array(embeddings)

# ---------------------------
# Add to ChromaDB
# ---------------------------
collection.add(
    ids=ids,
    metadatas=metadatas,
    embeddings=embeddings.tolist()
)
print(f"Added {len(ids)} embeddings to ChromaDB collection '{collection_name}'")

# ---------------------------
# Save final dataset with embeddings as CSV & Parquet
# ---------------------------
df['embedding'] = [emb.tolist() for emb in embeddings]

final_csv_path = "data/final_embedded_dataset.csv"
final_parquet_path = "data/final_embedded_dataset.parquet"

df.to_csv(final_csv_path, index=False)
df.to_parquet(final_parquet_path, index=False)

print(f"Final dataset with embeddings saved to CSV: '{final_csv_path}'")
print(f"Final dataset with embeddings saved to Parquet: '{final_parquet_path}'")
