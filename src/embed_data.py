# import pandas as pd
# import chromadb
# from chromadb.config import Settings
# from sentence_transformers import SentenceTransformer

# print("🔹 Loading dataset...")
# df = pd.read_csv("data/Merged_Video_Transcript.csv")

# print("🔹 Cleaning dataset...")
# df = df.drop_duplicates(subset=["id", "title"]).dropna(subset=["title", "transcript"])
# df["channel_title"] = df["channel_title"].fillna("Unknown Channel")
# df["description"] = df["description"].fillna("No description")
# df["thumbnail_high"] = df["thumbnail_high"].fillna("https://i.ytimg.com/vi/default.jpg")


# print(f"✅ Remaining rows after cleaning: {len(df)}")

# print("🔹 Loading embedding model...")
# model = SentenceTransformer("all-MiniLM-L6-v2")

# print("🔹 Setting up ChromaDB with cosine similarity...")
# client = chromadb.PersistentClient(path="data/chroma_db")

# # Create collection with cosine metric
# collection = client.get_or_create_collection(
#     name="youtube_videos",
#     metadata={"hnsw:space": "cosine"}  # 👈 ensures cosine similarity is used
# )

# print("🔹 Generating embeddings and storing data...")
# for i, row in df.iterrows():
#     text = f"{row['title']} {row['description']} {row['transcript']}"
#     embedding = model.encode(text)

#     metadata = {
#         "title": row["title"],
#         "channel_title": row["channel_title"],
#         "description": row["description"],
#         "url": f"https://www.youtube.com/watch?v={row['id']}",
#         "thumbnail": row["thumbnail_high"]
#     }

#     collection.add(
#         ids=[str(i)],
#         embeddings=[embedding],
#         metadatas=[metadata],
#         documents=[text]
#     )

# print("✅ Embedding process completed successfully using cosine similarity!")


import pandas as pd
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

print("🔹 Loading dataset...")
df = pd.read_csv("data/Merged_Video_Transcript.csv")

print("🔹 Cleaning dataset...")
df = df.drop_duplicates(subset=["id", "title"]).dropna(subset=["title", "transcript"])
df["channel_title"] = df["channel_title"].fillna("Unknown Channel")
df["description"] = df["description"].fillna("No description")

# Default YouTube logo fallback
YOUTUBE_LOGO = "https://upload.wikimedia.org/wikipedia/commons/b/b8/YouTube_Logo_2017.svg"

# Fix thumbnail column — if missing or broken, replace with logo
def clean_thumbnail(url):
    if pd.isna(url) or not isinstance(url, str) or not url.startswith("http"):
        return YOUTUBE_LOGO
    # Some invalid YouTube thumbnails may still use wrong patterns
    if "default.jpg" in url or "no_thumbnail" in url:
        return YOUTUBE_LOGO
    return url.strip()

df["thumbnail_high"] = df["thumbnail_high"].apply(clean_thumbnail)

print(f"✅ Remaining rows after cleaning: {len(df)}")

print("🔹 Loading embedding model...")
model = SentenceTransformer("all-MiniLM-L6-v2")

print("🔹 Setting up ChromaDB with cosine similarity...")
client = chromadb.PersistentClient(path="data/chroma_db")

# Create collection with cosine metric
collection = client.get_or_create_collection(
    name="youtube_videos",
    metadata={"hnsw:space": "cosine"}  # 👈 ensures cosine similarity is used
)

print("🔹 Generating embeddings and storing data...")
for i, row in df.iterrows():
    text = f"{row['title']} {row['description']} {row['transcript']}"
    embedding = model.encode(text)

    metadata = {
        "title": row["title"],
        "channel_title": row["channel_title"],
        "description": row["description"],
        "url": f"https://www.youtube.com/watch?v={row['id']}",
        "thumbnail": f"https://img.youtube.com/vi/{row['id']}/mqdefault.jpg" #row["thumbnail_high"]
    }

    collection.add(
        ids=[str(i)],
        embeddings=[embedding],
        metadatas=[metadata],
        documents=[text]
    )

print("✅ Embedding process completed successfully using cosine similarity with YouTube logo fallback!")
