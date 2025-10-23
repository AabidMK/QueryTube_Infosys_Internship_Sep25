#!/usr/bin/env python3
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.utils import embedding_functions
from fastapi.middleware.cors import CORSMiddleware
import os

# --- Configuration ---
PERSIST_DIR = "/Users/hariniemmadi/Desktop/QueryTube/chromadb_store"
COLLECTION_NAME = "videos"

# --- Initialize FastAPI ---
app = FastAPI(title="Video Semantic Search API", version="1.0")

# --- Enable CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow requests from any frontend
    allow_credentials=True,
    allow_methods=["*"],  # allow GET, POST, OPTIONS, etc.
    allow_headers=["*"],  # allow all headers
)

# --- Load embedding model ---
print("🧠 Loading SentenceTransformer model...")
model = SentenceTransformer("all-MiniLM-L6-v2")

# --- Initialize Chroma client ---
client = chromadb.PersistentClient(path=PERSIST_DIR)
collection = client.get_or_create_collection(name=COLLECTION_NAME)
print(f"✅ Connected to ChromaDB collection: {COLLECTION_NAME}")

# --- Request body model ---
class SearchRequest(BaseModel):
    query: str
    top_k: int = 5

# --- Search endpoint ---
@app.post("/search")
def search_videos(request: SearchRequest):
    query = request.query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    print(f"🔍 Received query: {query}")

    # Generate query embedding
    query_embedding = model.encode(query).tolist()

    # Perform search in ChromaDB
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=request.top_k
    )

    # Format results
    formatted_results = []
    for i, (id_, metadata, score) in enumerate(
        zip(results["ids"][0], results["metadatas"][0], results["distances"][0])
    ):
        formatted_results.append({
            "rank": i + 1,
            "video_id": id_,
            "title": metadata.get("title", "N/A"),
            "similarity_score": round(score, 4),
            "transcript": metadata.get("transcript", "")[:200] + "..."
        })

    return {"query": query, "results": formatted_results}
