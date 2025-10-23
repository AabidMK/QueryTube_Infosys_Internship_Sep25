from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from search_engine import SearchEngine
import re

# ---------------------------
# Request & Response Models
# ---------------------------
class SearchRequest(BaseModel):
    query: str
    top_k: Optional[int] = 5
    min_similarity: Optional[float] = 0.5

class SearchResultItem(BaseModel):
    rank: int
    title: str
    channel: str
    similarity: float
    video_url: str
    thumbnail_url: str

class SearchResponse(BaseModel):
    query: str
    results: List[SearchResultItem]
    average_similarity: float
    relevance: str

# ---------------------------
# Initialize FastAPI & Search Engine
# ---------------------------
app = FastAPI(title="Semantic Video Search API")
engine = SearchEngine()

# Allow requests from frontend
origins = ["http://localhost:3000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------
# Utility: preprocess query
# ---------------------------
def preprocess_query(query: str) -> str:
    query = query.strip().lower()
    query = re.sub(r"[^\w\s]", "", query)
    if len(query.split()) <= 1:
        query += " tutorial or introduction"
    return query

# ---------------------------
# /search endpoint
# ---------------------------
@app.post("/search", response_model=SearchResponse)
def search_videos(request: SearchRequest):
    if not request.query:
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    query = preprocess_query(request.query)

    # Generate embedding & query database
    embedding = engine.generate_embedding(query)
    results = engine.db_manager.query_embeddings(embedding, top_k=50)

    hits = results['metadatas'][0]
    distances = results['distances'][0]

    scored_results = []
    for meta, dist in zip(hits, distances):
        similarity = 1 - (dist / 2)
        similarity = max(0.0, min(similarity, 1.0))
        if similarity >= request.min_similarity:
            scored_results.append((similarity, meta))

    # Sort by similarity descending and take top_k
    scored_results.sort(key=lambda x: x[0], reverse=True)
    scored_results = scored_results[:request.top_k]

    # Calculate average similarity
    avg_similarity = sum([sim for sim, _ in scored_results]) / len(scored_results) if scored_results else 0
    if avg_similarity >= 0.75:
        relevance = "Excellent"
    elif avg_similarity >= 0.5:
        relevance = "Good"
    else:
        relevance = "Weak"

    # Prepare response with video_id
    response_results = []
    for idx, (sim, meta) in enumerate(scored_results, start=1):
        video_id = meta.get("video_id") or meta.get("id") or "N/A"
        video_url = f"https://www.youtube.com/watch?v={video_id}" if video_id != "N/A" else "N/A"
        thumbnail_url = f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg" if video_id != "N/A" else "N/A"

        response_results.append({
            "rank": idx,
            "title": meta.get('title', 'N/A'),
            "channel": meta.get('channel_title', 'N/A'),
            "similarity": round(sim, 3),
            "video_url": video_url,
            "thumbnail_url": thumbnail_url
        })

    return SearchResponse(
        query=request.query,
        results=response_results,
        average_similarity=round(avg_similarity, 3),
        relevance=relevance
    )
