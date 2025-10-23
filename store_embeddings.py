import pandas as pd
import chromadb
import numpy as np

# ============================
# Load dataset
# ============================
print("📂 Loading dataset...")
df = pd.read_csv(r'D:\webtech lab\querytube\dataset_with_embeddings.csv')
print(f"✅ Loaded {len(df)} rows from dataset")

# ============================
# Initialize ChromaDB
# ============================
print("🔧 Initializing ChromaDB...")
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection(name="video_embeddings")
print("✅ ChromaDB initialized")

# ============================
# Remove duplicates
# ============================
print("🧹 Removing duplicates...")
df.drop_duplicates(subset=['id'], inplace=True)
print(f"✅ After removing duplicates: {len(df)} rows")

# ============================
# Parse embeddings
# ============================
print("🔢 Parsing embeddings...")
def parse_embedding(x):
    if isinstance(x, str):
        return np.array(eval(x))
    return np.array(x)

df['embedding'] = df['embedding'].apply(parse_embedding)
embeddings = np.vstack(df['embedding'].values)
print(f"✅ Parsed {len(embeddings)} embeddings")

# ============================
# Prepare metadata (including channel_title & description)
# ============================
print("📋 Preparing metadata...")
metadatas = [
    {
        "id": row["id"],
        "title": row.get("title") or "N/A",
        "channel_title": row.get("channel_title") or "N/A",
        "description": row.get("description") or "No description available",
        "transcript": row.get("transcript") or ""
    }
    for _, row in df.iterrows()
]
print(f"✅ Prepared metadata for {len(metadatas)} items")

# ============================
# Add to ChromaDB
# ============================
print("💾 Adding data to ChromaDB...")
collection.add(
    ids=df["id"].astype(str).tolist(),
    embeddings=embeddings,
    metadatas=metadatas,
    documents=df["transcript"].astype(str).tolist()  # or combined text for embeddings
)

print(f"✅ Stored {len(df)} videos in ChromaDB collection 'video_embeddings'.")
print("🎯 Data is ready for semantic search queries.")
