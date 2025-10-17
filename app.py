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

# --- FastAPI App Initialization ---
app = FastAPI()

# --- Add CORS Middleware ---
# This is the crucial part that was missing.
# It allows your frontend (running on a different "origin") to talk to your backend.
origins = [
    "http://localhost",
    "http://127.0.0.1",
    "http://127.0.0.1:5500",
    "http://0.0.0.0:8000", # Common for VS Code Live Server
    "null" # Allow requests from local files (opening index.html directly)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Allows all methods (POST, GET, etc.)
    allow_headers=["*"], # Allows all headers
)


# --- API Endpoint ---
@app.post("/search")
def search_videos(request: SearchRequest):
    if collection is None:
        return {"error": "ChromaDB collection is not available."}
    
    try:
        # Query the collection
        results = collection.query(
            query_texts=[request.query],
            n_results=5 # Get top 5 results
        )
        
        # Structure the results for the frontend
        # The original code was returning a complex object. Let's simplify it.
        output = []
        
        # Check if there are any results to process
        if results and results['ids'] and len(results['ids'][0]) > 0:
            num_results = len(results['ids'][0])
            for i in range(num_results):
                metadata = results['metadatas'][0][i]
                document = results['documents'][0][i]
                
                output.append({
                    "id": metadata.get('id', 'N/A'),
                    "title": metadata.get('title', 'No Title'),
                    "channel_title": metadata.get('channel_title', 'No Channel'),
                    "transcript_snippet": document[:250] + "..." # Send a snippet
                })
        
        return {"results": output}

    except Exception as e:
        print(f"Error during search: {e}")
        return {"error": f"An error occurred during search: {e}"}

# This part is for running the script directly with `python app.py`
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)