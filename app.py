# app.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
import pandas as pd
import numpy as np
import ast

# -----------------------------
# 1. Load Data & Model
# -----------------------------
CSV_PATH = "phase2_transcript_embeddings.csv"  # Update path if needed

try:
    df = pd.read_csv(CSV_PATH)
    df['clean_transcript_embedding'] = df['clean_transcript_embedding'].apply(ast.literal_eval)
except FileNotFoundError:
    raise Exception(f"CSV file not found at {CSV_PATH}. Please add your dataset to this path.")

# Load the Sentence Transformer model
model = SentenceTransformer('all-MiniLM-L6-v2')


# -----------------------------
# 2. VideoSearchEngine Class
# -----------------------------
class VideoSearchEngine:
    def __init__(self, df, embedding_col='clean_transcript_embedding'):
        self.df = df
        self.embeddings = np.array(df[embedding_col].to_list())

    def search(self, query: str, top_k: int = 5):
        # Encode query
        q_emb = model.encode(query, convert_to_numpy=True, normalize_embeddings=True)

        # Compute cosine similarity
        sims = np.dot(self.embeddings, q_emb) / (
            np.linalg.norm(self.embeddings, axis=1) * np.linalg.norm(q_emb)
        )

        # Get top-k results
        top_indices = sims.argsort()[::-1][:top_k]
        results = self.df.iloc[top_indices].copy()
        results['similarity'] = sims[top_indices]

        # Format output
        output = []
        for rank, row in enumerate(results.itertuples(), start=1):
            output.append({
                "rank": rank,
                "video_title": row.title,
                "youtube_link": f"https://www.youtube.com/watch?v={row.video_id}",
                "channel_name": getattr(row, 'channel_title', ''),
                "similarity": row.similarity
            })
        return output


# Initialize the search engine
search_engine = VideoSearchEngine(df)


# -----------------------------
# 3. FastAPI Setup
# -----------------------------
app = FastAPI(title="Video Semantic Search API", version="1.0")

class SearchRequest(BaseModel):
    query: str
    top_k: int = 5


@app.post("/search")
def search_videos(request: SearchRequest):
    try:
        results = search_engine.search(request.query, request.top_k)
        return {"query": request.query, "top_k": request.top_k, "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
def root():
    return {"message": "Video Semantic Search API is running. Use POST /search to query."}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
