import chromadb
from sentence_transformers import SentenceTransformer

# Initialize your ChromaDB client and collection path
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_collection("youtube_videos")

# Load the same embedding model as used during ingestion
model = SentenceTransformer('all-MiniLM-L6-v2')  # Change to match your setup

def search_youtube_videos(query_text, top_n=5):
    # Encode the search query to an embedding vector
    query_embedding = model.encode([query_text])[0]

    # Perform semantic search in ChromaDB
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_n
    )

    # Parse and return the metadata for display or further processing
    hits = []
    for i in range(len(results['ids'][0])):
        metadata = results['metadatas'][0][i]
        video_result = {
            "id": results['ids'][0][i],
            "title": metadata.get('title', ''),
            "channel": metadata.get('channel', ''),
            "url": metadata.get('url', ''),
            "description": metadata.get('description', ''),
            "thumbnail": metadata.get('thumbnail', ''),
            "score": results['distances'][0][i]  # Lower = better match
        }
        hits.append(video_result)
    return hits

# Example usage
query = "How to use pandas for data analysis"
results = search_youtube_videos(query, top_n=5)
for video in results:
    print(f"{video['title']} ({video['channel']}) - {video['url']}")
    print(f"Description: {video['description']}\nThumbnail: {video['thumbnail']}\nScore: {video['score']}\n")
