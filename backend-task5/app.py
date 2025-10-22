from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
# Assuming video_search_engine.py is in the same directory
from video_search_engine import VideoSearchEngine 


# API Setup
app = FastAPI(
    title="Video Semantic Search API",
    description="FastAPI backend for ChromaDB-powered semantic video search with detailed metadata.",
    version="2.1.0"
)

# Allow frontend (React/Vite) access
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Search Engine
try:
    search_engine = VideoSearchEngine()
except Exception as e:
    print(f"❌ FATAL ERROR: Could not initialize VideoSearchEngine: {e}")
    # In a real environment, you might stop here or use a dummy engine
    # For this example, we re-raise to indicate a critical setup failure
    raise

# Define Request & Response Models
class SearchRequest(BaseModel):
    """Incoming payload from frontend"""
    query: str = Field(..., description="The semantic search query text.")
    top_k: int = Field(5, description="Number of top results to return.", ge=1, le=20)
    category_id: Optional[int] = Field(None, description="Optional category ID filter.")


class SearchResult(BaseModel):
    """One video search result with full metadata"""
    rank: int
    title: str
    channel: str
    similarity_score: float
    video_id: str
    published_at: str
    thumbnail_high: str
    duration: str
    view_count: int
    like_count: int
    transcript: str # Now including full transcript
    category_id: int


class SearchResponse(BaseModel):
    """Response returned to frontend"""
    status: str
    results: List[SearchResult]
    total_results: int


# API Endpoint — Semantic Search
@app.post("/search", response_model=SearchResponse)
def search_videos(request: SearchRequest):
    """
    Perform a semantic video search with optional category ID filtering.
    """
    try:
        print(f"🧠 Query: {request.query}, Category ID: {request.category_id}, TopK: {request.top_k}")
        
        # The search method now expects a single category_id integer or None
        results = search_engine.search(
            query=request.query,
            top_k=request.top_k,
            category_id=request.category_id 
        )

        # The results coming from search_engine now match the SearchResult model structure
        return {
            "status": "success",
            "results": results,
            "total_results": len(results)
        }

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        print(f"❌ Internal server error: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")


# Health Check Endpoint
@app.get("/")
def health_check():
    return {"status": "ok", "message": "Video Search API is running."}


# To run: uvicorn app:app --reload --port 8000
