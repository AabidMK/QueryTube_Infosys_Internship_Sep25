# app.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
from video_search_engine import VideoSearchEngine
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="QueryTube: YouTube Semantic Search API")

# LangGraph wrapper stays at API boundary while preserving the same search logic.
search_engine = None
search_graph = None

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SearchRequest(BaseModel):
    query: str
    top_k: int = 5
    #min_score: float = 0.2

# Initialize engine once at startup
try:
    search_engine = VideoSearchEngine()
    search_graph = search_engine.build_graph()
except Exception as e:
    # If engine fails to load, raise when app starts
    raise RuntimeError(f"Failed to initialize VideoSearchEngine: {e}")

@app.post("/search")
async def search_videos(req: SearchRequest) -> Dict[str, Any]:
    if not req.query or not req.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")
    if req.top_k <= 0:
        raise HTTPException(status_code=400, detail="top_k must be > 0")

    try:
        state = search_graph.invoke({
            "query": req.query,
            "top_k": req.top_k,
            "min_score": 0.2,
            "results": [],
        })
        return {"query": req.query, "top_k": req.top_k, "results": state.get("results", [])}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "QueryTube API running. Use POST /search with {query, top_k}"} # min_score
