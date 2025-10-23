import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
import chromadb
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os

# Suppress TensorFlow warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

# --- Configuration ---
FILE_NAME = "videos_with_embeddings_cleaned_unique.csv"
CHROMA_PATH = "chromadb_data"
COLLECTION_NAME = "video_embeddings_all"
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"

# --- Pydantic Model for Request ---
class SearchRequest(BaseModel):
    query: str
    top_k: int = 5

# --- VideoSearchEngine Class ---
class VideoSearchEngine:
    def __init__(self):
        self.model = SentenceTransformer(EMBEDDING_MODEL_NAME)
        self.client = chromadb.PersistentClient(path=CHROMA_PATH)
        
        try:
            self.collection = self.client.get_collection(COLLECTION_NAME)
            print(f"✅ Connected to existing collection: {COLLECTION_NAME} ({self.collection.count()} videos)")
        except Exception as e:
            print(f"⚠️ Collection '{COLLECTION_NAME}' not found or schema error: {e}")
            print("🗑️ Resetting database and creating new collection...")
            try:
                for coll in self.client.list_collections():
                    self.client.delete_collection(coll.name)
                self.collection = self.client.create_collection(
                    name=COLLECTION_NAME,
                    metadata={"hnsw:space": "cosine"}
                )
                print(f"✅ Created new collection: {COLLECTION_NAME}")
                self.load_videos()
            except Exception as create_err:
                raise Exception(f"Failed to create collection: {create_err}")
    
    def load_videos(self):
        print("📊 Loading videos from CSV...")
        try:
            df = pd.read_csv(FILE_NAME)
            print(f"Found {len(df)} videos")
            
            ids, embeddings, metadatas = [], [], []
            seen_ids = set()
            
            for idx, row in df.iterrows():
                video_id = str(row.get('video_id', f"video_{idx}"))
                
                if video_id in seen_ids or video_id in ['nan', 'you know']:
                    video_id = f"video_{idx}_{len(seen_ids)}"
                
                title = str(row.get('title', ''))
                desc = str(row.get('description', ''))[:500]
                transcript = str(row.get('transcript', ''))[:4000]
                channel = str(row.get('channel_title', 'Unknown'))
                
                full_text = f"{title} {desc} {transcript}".strip()
                if len(full_text) > 10:
                    try:
                        embedding = self.model.encode(full_text, show_progress_bar=False)
                        if len(embedding) == 384:
                            ids.append(video_id)
                            seen_ids.add(video_id)
                            embeddings.append(embedding.tolist())
                            metadatas.append({
                                'video_id': video_id,
                                'title': title,
                                'channel_title': channel,
                                'description': desc,
                                'transcript_preview': (transcript[:200] + "...") if len(transcript) > 200 else transcript
                            })
                    except:
                        continue
            
            if ids:
                self.collection.add(ids=ids, embeddings=embeddings, metadatas=metadatas)
                print(f"✅ Loaded {len(ids)} videos into {COLLECTION_NAME}")
            else:
                print("❌ No valid videos loaded")
                
        except Exception as e:
            print(f"❌ Load error: {e}")
            raise
    
    def generate_query_embedding(self, query):
        return self.model.encode(query, convert_to_numpy=True)
    
    def search(self, query_embedding, top_k=5):
        results = self.collection.query(
            query_embeddings=query_embedding.tolist(),
            n_results=top_k,
            include=["metadatas", "distances"]
        )
        return results
    
    def format_results(self, results, min_score=0.1):
        if not results or not results.get("ids") or not results["ids"][0]:
            return []
        
        formatted = []
        for i in range(len(results["ids"][0])):
            distance = results["distances"][0][i]
            score = 1 / (1 + distance)
            metadata = results["metadatas"][0][i]
            
            if score >= min_score:
                transcript_raw = str(metadata.get("transcript", "") or 
                                   metadata.get("transcript_preview", ""))
                transcript = transcript_raw[:200] if len(transcript_raw) <= 200 else transcript_raw[:200] + "..."
                
                formatted.append({
                    "rank": i + 1,
                    "title": metadata.get("title", "N/A"),
                    "channel": metadata.get("channel_title", "N/A"),
                    "transcript": transcript,
                    "similarity_score": round(score, 3),
                    "video_id": metadata.get("video_id", "N/A")
                })
        
        return formatted

# --- FastAPI Setup ---
app = FastAPI(title="Video Semantic Search API", version="1.0")

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to Video Semantic Search API!",
        "docs": "http://localhost:8000/docs",
        "endpoint": "POST /search with {query: str, top_k: int}"
    }

# Initialize search engine
try:
    search_engine = VideoSearchEngine()
except Exception as e:
    print(f"⚠️ Failed to initialize: {e}")
    raise

# --- Endpoints ---
@app.post("/search")
async def search_videos(request: SearchRequest):
    query = request.query.strip()
    top_k = max(1, min(request.top_k, 10))
    
    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    try:
        query_embedding = search_engine.generate_query_embedding(query)
        results = search_engine.search(query_embedding, top_k)
        formatted_results = search_engine.format_results(results, min_score=0.1)
        
        return {
            "query": query,
            "results": formatted_results,
            "count": len(formatted_results)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    print("🌐 Starting FastAPI server...")
    print(f"API at: http://localhost:8000")
    print("Docs at: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)
