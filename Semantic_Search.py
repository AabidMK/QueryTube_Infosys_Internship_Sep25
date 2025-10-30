"""
CHROMADB + SEMANTIC SEARCH PIPELINE
-----------------------------------
• Builds ChromaDB from CSV if not already present
• Performs semantic search on transcripts
• Displays normalized similarity (0–1)
"""

import os
import pandas as pd
import re
from sentence_transformers import SentenceTransformer
import chromadb

# ===============================
# 1. CONFIGURATION
# ===============================
DATA_PATH = r"C:\Users\balak\OneDrive\Desktop\Youtube_Query\videos_with_embeddings.csv"
CHROMA_PATH = r"C:\Users\balak\OneDrive\Desktop\Youtube_Query\chroma_db"
COLLECTION_NAME = "video_embeddings"
MODEL_NAME = "all-MiniLM-L6-v2"
TOP_K = 5

# ===============================
# 2. INITIALIZE MODEL & CLIENT
# ===============================
print("🧠 Loading embedding model...")
model = SentenceTransformer(MODEL_NAME)

print("💾 Initializing persistent Chroma client...")
client = chromadb.PersistentClient(path=CHROMA_PATH)

# ===============================
# 3. CREATE / POPULATE COLLECTION
# ===============================
collections = [c.name for c in client.list_collections()]
if COLLECTION_NAME not in collections:
    print("📂 Building new collection from CSV...")

    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"❌ File not found at: {DATA_PATH}")

    df = pd.read_csv(DATA_PATH)

    required_cols = ["title", "channel_title", "transcript"]
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"❌ Missing required column: {col}")

    texts = df["transcript"].astype(str).tolist()

    print(f"🔢 Generating embeddings for {len(texts)} transcripts...")
    embeddings = model.encode(texts, convert_to_numpy=True, show_progress_bar=True)

    # ✅ Create metadata with URL and thumbnail
    metadatas = []
    for _, row in df.iterrows():
        meta = {
            "title": row.get("title", ""),
            "channel_title": row.get("channel_title", ""),
            "url": f"https://www.youtube.com/watch?v={row.get('video_id', '')}",
            "thumbnail": row.get("thumbnail_high", row.get("thumbnail_default", "")),
        }
        metadatas.append(meta)

    collection = client.get_or_create_collection(name=COLLECTION_NAME)
    collection.add(
        ids=[str(i) for i in range(len(df))],
        embeddings=embeddings,
        metadatas=metadatas,
        documents=texts
    )

    print(f"✅ Collection '{COLLECTION_NAME}' successfully created and stored at {CHROMA_PATH}")

else:
    print(f"✅ Collection '{COLLECTION_NAME}' already exists.")
    collection = client.get_collection(name=COLLECTION_NAME)

# ===============================
# 4. GET USER QUERY
# ===============================
def get_user_query():
    query = input("\n🔎 Enter your search query: ").strip()
    if not query:
        raise ValueError("❌ Query cannot be empty.")
    query = re.sub(r"[^a-zA-Z0-9\s]", "", query)
    return query

# ===============================
# 5. SEMANTIC SEARCH
# ===============================
def semantic_search(query_text, top_k=TOP_K):
    print("\n⚙️ Generating embedding for query...")
    query_embedding = model.encode(query_text, convert_to_numpy=True)

    print("🔍 Running semantic search...")
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["metadatas", "distances", "documents"]
    )
    return results

# ===============================
# 6. DISPLAY RESULTS
# ===============================
def display_results(results):
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]
    documents = results.get("documents", [[]])[0]

    print("\n🎯 Top Search Results:")
    print("=" * 90)
    for idx, (meta, distance, doc) in enumerate(zip(metadatas, distances, documents)):
        similarity = 1 / (1 + distance)  # Normalize cosine distance → similarity in [0,1]
        print(f"Rank: {idx + 1}")
        print(f"🎬 Title: {meta.get('title', 'Unknown')}")
        print(f"📺 Channel: {meta.get('channel_title', 'Unknown')}")
        print(f"🔗 URL: {meta.get('url', 'N/A')}")
        print(f"🖼️ Thumbnail: {meta.get('thumbnail', 'N/A')}")
        print(f"📏 Distance: {round(distance, 3)} | 🔢 Similarity: {round(similarity, 3)}")
        print(f"📝 Snippet: {doc[:250]}...\n")
        print("-" * 90)

# ===============================
# 7. MAIN EXECUTION LOOP
# ===============================
if __name__ == "__main__":
    try:
        while True:
            query = get_user_query()
            results = semantic_search(query, top_k=TOP_K)
            display_results(results)

            cont = input("\n🔁 Search again? (y/n): ").lower()
            if cont != "y":
                print("👋 Exiting Semantic Search.")
                break

    except Exception as e:
        print(f"❌ Error: {e}")
