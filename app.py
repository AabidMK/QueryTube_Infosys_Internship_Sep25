from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any

# Import the core search logic (assuming it's in search_engine.py)
from search_engine import search_engine

# --- API Setup ---
app = FastAPI(
    title="Video Vector Search API",
    description="API for performing semantic search on video embeddings using ChromaDB and Sentence-Transformers.",
    version="1.0.0"
)

# --- CORS Middleware FIX ---
# This allows the local index.html file to communicate with the API server.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins (for local development/testing)
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

# --- Request Body Schema ---
# Define the expected format for the POST request body
class SearchRequest(BaseModel):
    query: str
    top_k: int = 5
    min_score: float = 0.2

# --- API Endpoint ---

@app.post("/search", response_model=List[Dict[str, Any]], tags=["Search"])
def perform_semantic_search(request: SearchRequest):
    """
    Accepts a search query and returns the top K most semantically relevant videos.
    """
    # 1. Check if the search engine initialized correctly
    if search_engine is None:
        raise HTTPException(
            status_code=503,
            detail="Service Unavailable: VideoSearchEngine failed to initialize. Check if the embedding model and ChromaDB collection exist."
        )

    # 2. Validate the query input
    if not request.query or not request.query.strip():
        raise HTTPException(
            status_code=400,
            detail="Query cannot be empty."
        )

    # 3. Perform the search using the reusable engine
    try:
        results = search_engine.search(
            query=request.query,
            top_k=request.top_k,
            min_score=request.min_score
        )

        if not results:
             return [{"message": "No relevant videos found matching the criteria."}]

        return results

    except RuntimeError as e:
        # Handle errors related to the engine state (e.g., model or DB went missing)
        raise HTTPException(
            status_code=500,
            detail=f"Internal Search Engine Error: {e}"
        )
    except Exception as e:
        # Catch any unexpected errors during processing
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred during search: {e}"
        )

# --- Root/Health Check Endpoint ---
@app.get("/", tags=["Status"])
def read_root():
    return {"status": "ok", "service": "Video Vector Search API is running"}