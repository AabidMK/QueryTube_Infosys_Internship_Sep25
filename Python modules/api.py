from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
from fastapi.middleware.cors import CORSMiddleware
from Search_Query_main import search_youtube_videos

app = FastAPI(title="QueryTube: YouTube Semantic Search API")

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


@app.post("/search")
async def search_videos(req: SearchRequest) -> Dict[str, Any]:
    if not req.query or not req.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")
    if req.top_k <= 0:
        raise HTTPException(status_code=400, detail="top_k must be > 0")

    try:
        results = search_youtube_videos(req.query, top_n=req.top_k)
        return {"query": req.query, "top_k": req.top_k, "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "QueryTube API running. Use POST /search with {query, top_k}"}    

# run with: uvicorn api:app --reload
# can check it at http://127.0.0.1:8000/docs