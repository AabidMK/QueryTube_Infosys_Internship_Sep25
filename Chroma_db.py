import pandas as pd
import numpy as np
import chromadb
import ast

# ============================
# Load dataset from Parquet
# ============================
# Ensure you have 'dataset-with-embeddings_parquetFile.parquet' accessible
merged_df = pd.read_parquet("dataset-with-embeddings_parquetFile.parquet")

# Initialize persistent ChromaDB client
client = chromadb.PersistentClient(path="./chroma_db")


try:
    # Use client.get_collection().delete() for better error handling if needed, 
    # but for simplicity, we keep the try/except block.
    client.delete_collection(name="youtube_videos")
    print("✅ Successfully deleted old 'youtube_videos' collection to reset the metric.")
except ValueError:
    print("⚠️ 'youtube_videos' collection not found, proceeding with creation.")
except Exception as e:
    # Catching the specific error from your output
    if "does not exists" in str(e):
        print("⚠️ 'youtube_videos' collection not found, proceeding with creation.")
    else:
        print(f"Error during collection deletion: {e}")

collection = client.get_or_create_collection(
    name="youtube_videos",
    metadata={"hnsw:space": "cosine"} 
)
print("✅ Collection 'youtube_videos' is set up with 'cosine' distance metric.")

# Remove duplicate IDs
merged_df.drop_duplicates(subset=['id'], inplace=True)

# Convert embedding column safely
def parse_embedding(x):
    """Safely converts string representation of list/array to numpy array."""
    if isinstance(x, str):
        try:
            return np.array(ast.literal_eval(x))
        except (ValueError, SyntaxError):
            return None
    return np.array(x)

# --- Data Preparation for ChromaDB ---

# Convert publishedAt to a clean string format (ISO 8601) if it's a datetime object
if 'publishedAt' in merged_df.columns:
    try:
        merged_df['publishedAt'] = pd.to_datetime(merged_df['publishedAt'], utc=True).dt.isoformat()
    except Exception:
        pass # If conversion fails or it's already a string, proceed

merged_df["embedding"] = merged_df["embedding"].apply(parse_embedding)
merged_df.dropna(subset=['embedding', 'id'], inplace=True)

embeddings = np.vstack(merged_df["embedding"].values)

# Define the columns to store as metadata in ChromaDB
metadata_cols = [
    "id", "title", "transcript", "channel_title", 
    "publishedAt", "thumbnail_high", "duration", "viewCount", 
    "likeCount", "categoryId"
]

# CRITICAL FIX: Ensure all metadata fields are non-null and correctly typed for ChromaDB.
# 1. Select the metadata columns.
metadata_df = merged_df[metadata_cols].copy()

# 2. Fill NaN values:
# Text/String fields (including ID and CategoryID for safety, although they should be present)
string_cols = ["id", "title", "transcript", "channel_title", "publishedAt", "thumbnail_high", "duration"]
metadata_df[string_cols] = metadata_df[string_cols].fillna("")

# Numeric fields (viewCount, likeCount, categoryId) - fill NaN with 0
numeric_cols = ["viewCount", "likeCount", "categoryId"]
metadata_df[numeric_cols] = metadata_df[numeric_cols].fillna(0).astype(int) 


# 3. Rename 'id' to 'video_id' and convert to list of dictionaries
metadatas = metadata_df.rename(columns={"id": "video_id"}).to_dict(orient="records")

collection.add(
    # Note: ChromaDB IDs must be strings
    ids=merged_df["id"].astype(str).tolist(),
    embeddings=embeddings.tolist(), # Convert to list of lists for ChromaDB
    metadatas=metadatas,
    documents=merged_df["combined_text"].astype(str).tolist()
)

print(f"\n✅ Stored {len(merged_df)} videos in ChromaDB collection 'youtube_videos'.")
print("🎯 Data is ready for semantic search queries.")
