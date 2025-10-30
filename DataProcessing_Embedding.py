import pandas as pd
import os
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.utils import embedding_functions

# -------------------------
# 1. FILE PATHS
# -------------------------
metadata_path = r"C:\Users\balak\OneDrive\Desktop\Combined_dataset\master_task1_datset.csv"
transcript_path = r"C:\Users\balak\OneDrive\Desktop\Combined_dataset\master_task2_datset.csv"
merged_output = "merged_videos.csv"
embedded_output = "videos_with_embeddings.csv"
chroma_db_path = "./chroma_db"

# -------------------------
# 2. LOAD AND MERGE DATA
# -------------------------
print("📘 Loading data...")
meta_df = pd.read_csv(metadata_path)
trans_df = pd.read_csv(transcript_path)

# Normalize column names
meta_df.columns = meta_df.columns.str.strip().str.lower()
trans_df.columns = trans_df.columns.str.strip().str.lower()

# Ensure 'video_id' exists
if "video_id" not in meta_df.columns or "video_id" not in trans_df.columns:
    raise ValueError("❌ Both CSVs must have a 'video_id' column.")

print("🔄 Merging metadata and transcripts...")
merged_df = pd.merge(meta_df, trans_df, on="video_id", how="inner")

# Clean missing or empty transcripts
merged_df = merged_df[merged_df["transcript"].notna() & (merged_df["transcript"].str.strip() != "")]
print(f"✅ Merged dataset size before cleaning duplicates: {merged_df.shape}")

# Remove malformed IDs (e.g., #NAME?) and ensure IDs are strings
merged_df = merged_df[~merged_df["video_id"].astype(str).str.contains("#NAME\?")]

# Drop duplicate video_ids, keeping the first occurrence
merged_df = merged_df.drop_duplicates(subset="video_id", keep="first").reset_index(drop=True)
print(f"✅ Merged dataset size after cleaning duplicates: {merged_df.shape}")

# Save merged dataset
merged_df.to_csv(merged_output, index=False)
print(f"💾 Merged data saved as: {merged_output}")

# -------------------------
# 3. GENERATE EMBEDDINGS
# -------------------------
print("🧠 Loading SentenceTransformer model (all-MiniLM-L6-v2)...")
model = SentenceTransformer("all-MiniLM-L6-v2")

# Combine title + transcript
merged_df["combined_text"] = merged_df["title"].fillna("") + ". " + merged_df["transcript"].fillna("")

print("🔍 Generating embeddings...")
embeddings = model.encode(
    merged_df["combined_text"].tolist(),
    show_progress_bar=True,
    convert_to_numpy=True
)

# Add embeddings to dataframe
merged_df["embedding"] = embeddings.tolist()

# Save dataset with embeddings
merged_df.to_csv(embedded_output, index=False)
print(f"💾 Data with embeddings saved as: {embedded_output}")

# -------------------------
# 4. STORE IN CHROMADB
# -------------------------
print("🗂️ Initializing ChromaDB collection...")

chroma_client = chromadb.PersistentClient(path=chroma_db_path)
embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")

collection = chroma_client.get_or_create_collection(
    name="video_embeddings",
    embedding_function=embedding_func
)

print("📥 Adding data to ChromaDB...")
collection.add(
    ids=merged_df["video_id"].astype(str).tolist(),
    embeddings=embeddings.tolist(),
    metadatas=merged_df[["title", "transcript"]].to_dict(orient="records"),
    documents=merged_df["combined_text"].tolist(),
)
print(f"✅ Stored {len(merged_df)} videos in ChromaDB at: {chroma_db_path}")
print("🎯 Pipeline completed successfully!")

# -------------------------
# 5. SEMANTIC SEARCH INTERFACE
# -------------------------
def semantic_search():
    print("\n🔎 SEMANTIC SEARCH READY!")
    print("Type a query to find relevant videos (or type 'exit' to quit).")

    while True:
        query = input("\nEnter your search query: ").strip()
        if query.lower() in ["exit", "quit"]:
            print("👋 Exiting search. Goodbye!")
            break

        results = collection.query(
            query_texts=[query],
            n_results=3
        )

        print("\n🧩 Top Results:")
        for i, (vid, meta) in enumerate(zip(results["ids"][0], results["metadatas"][0]), start=1):
            print(f"\n{i}. 🎬 Video ID: {vid}")
            print(f"   🏷️ Title: {meta.get('title', '')[:100]}")
            snippet = meta.get("transcript", "")[:200].replace("\n", " ")
            print(f"   💬 Transcript Snippet: {snippet}...")

# -------------------------
# RUN SEARCH
# -------------------------
if __name__ == "__main__":
    semantic_search()
