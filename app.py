from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import chromadb

# --- Initialize ChromaDB Client ---
try:
    client = chromadb.PersistentClient(path="./chroma_db")
    collection = client.get_collection(name="video_embeddings")
    print("✅ Successfully connected to ChromaDB collection.")
except Exception as e:
    print(f"❌ Error connecting to ChromaDB: {e}")
    collection = None

# --- Pydantic Model for Request Body ---
class SearchRequest(BaseModel):
    query: str
    top_k: int = 5

# --- FastAPI App Initialization ---
app = FastAPI()

# --- Add CORS Middleware ---
origins = [
    "http://localhost",
    "http://127.0.0.1",
    "http://127.0.0.1:5500",
    "null" # Allow requests from local files
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/search")
def search(request: SearchRequest):
    if collection is None:
        return {"error": "ChromaDB collection is not available."}
    
    try:
        # --- MODIFICATION 1: Include "distances" in the query ---
        results = collection.query(
            query_texts=[request.query],
            n_results=request.top_k,
            include=["metadatas", "documents", "distances"] # Added "distances"
        )
        
        output = []
        
        if results and results['ids'] and len(results['ids'][0]) > 0:
            num_results = len(results['ids'][0])
            for i in range(num_results):
                metadata = results['metadatas'][0][i]
                document = results['documents'][0][i]
                distance = results['distances'][0][i] # Get the distance score
                
                # --- MODIFICATION 2: Add distance_score to the response ---
                output.append({
                    "id": metadata.get('id', 'N/A'),
                    "title": metadata.get('title', 'No Title'),
                    "channel_title": metadata.get('channel_title', 'No Channel'),
                    "transcript_snippet": document[:250] + "...",
                    "distance_score": distance # Add the score here
                })
        
        return {"results": output}

    except Exception as e:
        print(f"Error during search: {e}")
        return {"error": f"An error occurred during search: {e}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
