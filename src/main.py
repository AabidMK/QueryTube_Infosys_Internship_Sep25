# from fastapi import FastAPI, Query
# from pydantic import BaseModel
# import chromadb
# from sentence_transformers import SentenceTransformer
# import numpy as np

# app = FastAPI(
#     title="YouTube Semantic Search API",
#     description="Find top similar YouTube videos based on text meaning using ChromaDB.",
#     version="3.0",
# )

# # ✅ Initialize once
# print("🔹 Connecting to ChromaDB...")
# client = chromadb.PersistentClient(path="./data/chroma_db")
# collection = client.get_or_create_collection("youtube_videos")

# print("🔹 Loading SentenceTransformer model...")
# model = SentenceTransformer("all-MiniLM-L6-v2")

# @app.get("/")
# def root():
#     return {"message": "✅ YouTube Semantic Search API is running!"}


# @app.get("/query")
# def search_videos(
#     query: str = Query(..., description="Enter your search term"),
#     top_k: int = Query(5, description="Number of top results to return")
# ):
#     # ✅ Embed the query using real model
#     query_embedding = model.encode(query).tolist()

#     # ✅ Query the ChromaDB collection
#     results = collection.query(
#         query_embeddings=[query_embedding],
#         n_results=top_k,
#         include=["metadatas", "distances"]
#     )

#     if not results["metadatas"][0]:
#         return {"query": query, "results": [], "message": "No results found"}

#     # ✅ Convert distances to similarity (1 - distance)
#     formatted_results = []
#     for rank, (metadata, dist) in enumerate(zip(results["metadatas"][0], results["distances"][0]), start=1):
#         similarity = round(1 - float(dist), 3)
#         formatted_results.append({
#             "rank": rank,
#             "title": metadata.get("title", "Unknown Title"),
#             "channel_title": metadata.get("channel_title", "Unknown Channel"),
#             "description": metadata.get("description", "No description"),
#             "url": metadata.get("url", "N/A"),
#             "thumbnail": metadata.get("thumbnail", ""),
#             "similarity_score": similarity,
#         })

#     return {"query": query, "results": formatted_results}



# from fastapi import FastAPI, Query
# from fastapi.middleware.cors import CORSMiddleware
# import chromadb
# from sentence_transformers import SentenceTransformer
# import numpy as np

# app = FastAPI(
#     title="YouTube Semantic Search API",
#     description="Find top similar YouTube videos based on text meaning using ChromaDB.",
#     version="3.0",
# )

# # ✅ Allow frontend to access backend
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # you can restrict to ["http://127.0.0.1:5500"] later
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # ✅ Initialize ChromaDB and model
# print("🔹 Connecting to ChromaDB...")
# client = chromadb.PersistentClient(path="./data/chroma_db")
# collection = client.get_or_create_collection("youtube_videos")

# print("🔹 Loading SentenceTransformer model...")
# model = SentenceTransformer("all-MiniLM-L6-v2")

# @app.get("/")
# def root():
#     return {"message": "✅ YouTube Semantic Search API is running!"}


# @app.get("/query")
# def search_videos(
#     query: str = Query(..., description="Enter your search term"),
#     top_k: int = Query(5, description="Number of top results to return")
# ):
#     # ✅ Embed the query
#     query_embedding = model.encode(query).tolist()

#     # ✅ Search in ChromaDB
#     results = collection.query(
#         query_embeddings=[query_embedding],
#         n_results=top_k,
#         include=["metadatas", "distances"]
#     )

#     if not results["metadatas"][0]:
#         return {"query": query, "results": [], "message": "No results found"}

#     # ✅ Format results
#     formatted_results = []
#     for rank, (metadata, dist) in enumerate(zip(results["metadatas"][0], results["distances"][0]), start=1):
#         similarity = round(1 - float(dist), 3)
#         formatted_results.append({
#             "rank": rank,
#             "title": metadata.get("title", "Unknown Title"),
#             "channel_title": metadata.get("channel_title", "Unknown Channel"),
#             "description": metadata.get("description", "No description"),
#             "url": metadata.get("url", "N/A"),
#             "thumbnail": metadata.get("thumbnail", ""),
#             "similarity_score": similarity,
#         })

#     return {"query": query, "results": formatted_results}


from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import chromadb
from sentence_transformers import SentenceTransformer

# Initialize FastAPI app
app = FastAPI(
    title="YouTube Semantic Search API",
    description="Search YouTube videos semantically using ChromaDB and embeddings.",
    version="1.0.0"
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or ["http://127.0.0.1:5500", "http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize ChromaDB and model
print("🔹 Connecting to ChromaDB...")
client = chromadb.PersistentClient(path="data/chroma_db")
collection = client.get_collection(name="youtube_videos")

print("🔹 Loading SentenceTransformer model...")
model = SentenceTransformer("all-MiniLM-L6-v2")

@app.get("/")
def home():
    return {"message": "YouTube Semantic Search API is running 🚀"}

@app.get("/query")
def semantic_search(query: str = Query(..., description="Enter your search query"), top_k: int = 5):
    """Perform semantic search using ChromaDB"""
    if not query.strip():
        return {"error": "Query cannot be empty."}

    print(f"🔍 Searching for: {query}")

    # Compute embedding for query
    query_embedding = model.encode(query).tolist()

    # Query ChromaDB
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )

    if not results or not results["metadatas"]:
        return {"message": "No results found."}

    output = []
    for i, meta in enumerate(results["metadatas"][0]):
        output.append({
            "rank": i + 1,
            "title": meta.get("title", "No title"),
            "channel_title": meta.get("channel_title", "Unknown Channel"),
            "description": meta.get("description", "No description"),
            "url": meta.get("url", ""),
            "thumbnail": meta.get("thumbnail", ""),
            "similarity_score": round(results["distances"][0][i], 3)
        })

    return {"query": query, "results": output}
