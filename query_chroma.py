from sentence_transformers import SentenceTransformer
import chromadb
import numpy as np
import re
import time

# ===============================
# 1️⃣ Query Input Handling
# ===============================
def preprocess_query(query: str) -> str:
    """Preprocess and validate the user query."""
    query = query.strip()
    if not query:
        raise ValueError("❌ Empty query. Please enter a valid text query.")
    
    query = re.sub(r"[^a-zA-Z0-9\s.,!?]", "", query)
    return query

# ===============================
# 2️⃣ Query Embedding Generation
# ===============================
def generate_query_embedding(query_text: str) -> np.ndarray:
    """Generate an embedding for the given query using SentenceTransformer."""
    print("\n⚙️ Generating embedding for the query...")
    # NOTE: This model must be the same as the one used to create the embeddings!
    model = SentenceTransformer("all-MiniLM-L6-v2") 
    query_embedding = model.encode(query_text, convert_to_numpy=True)
    print("✅ Embedding generated successfully!")
    return query_embedding

# ===============================
# 3️⃣ Perform Semantic Search
# ===============================
def search_top_videos(query_text: str, top_k: int = 5):
    """Search the ChromaDB collection for semantically similar entries."""
    print("\n🔍 Searching in ChromaDB...")
    start_time = time.time()

    # Generate query embedding
    embedding = generate_query_embedding(query_text)

    client = chromadb.PersistentClient(path="./chroma_db")
    collection = client.get_or_create_collection(
        name="youtube_videos",
        metadata={"hnsw:space": "cosine"} 
    )

    # Perform semantic search
    results = collection.query(
        query_embeddings=[embedding.tolist()],
        n_results=top_k,
        include=["metadatas", "documents", "distances"]
    )

    elapsed = round(time.time() - start_time, 2)
    print(f"✅ Search completed in {elapsed} seconds!")

    # ===============================
    # 4️⃣ Format and Filter Results
    # ===============================
    formatted_results = []
    if results and results["ids"]:
        for i in range(len(results["ids"][0])):
            distance = results["distances"][0][i]
            similarity_score = round(1 - distance, 3) 

            metadata = results["metadatas"][0][i]
            
            # Extracting all new and old fields
            formatted_results.append({
                "rank": i + 1,
                "title": metadata.get("title", "N/A"),
                "channel": metadata.get("channel_title", "Unknown"), 
                "similarity_score": similarity_score,
                "video_id": metadata.get("video_id", "N/A"),
                "published_at": metadata.get("publishedAt", "N/A")[:10], # Show only date
                "duration": metadata.get("duration", "N/A"),
                "view_count": metadata.get("viewCount", "N/A"),
                "like_count": metadata.get("likeCount", "N/A"),
                "transcript_preview": metadata.get("transcript", "")[:200] + "...",
                "category_id": metadata.get("categoryId", "N/A")
            })
    else:
        print("⚠️ No matching entries found in the database.")
    
    return formatted_results

# ===============================
# 5️⃣ Display Results
# ===============================
def display_results(results):
    """Display formatted results to the user."""
    if not results:
        print("❌ No relevant videos found.")
        return

    print("\n🎯 Top Search Results:")
    for r in results:
        print(f"\nRank {r['rank']} | ID: {r['video_id']}")
        print(f"📺 Title: {r['title']}")
        print(f"📣 Channel: {r['channel']}")
        print(f"💡 Similarity Score: {r['similarity_score']}")
        print(f"🗓️ Published: {r['published_at']} | Duration: {r['duration']}")
        print(f"👀 Views: {r['view_count']} | 👍 Likes: {r['like_count']}")
        print(f"🏷️ Category ID: {r['category_id']}")
        print(f"📝 Transcript Preview: {r['transcript_preview']}")
        print("-" * 80)

# ===============================
# 🚀 Run the Search
# ===============================
if __name__ == "__main__":
    try:
        user_query = input("🔍 Enter your search query: ")
        cleaned_query = preprocess_query(user_query)
        top_results = search_top_videos(cleaned_query, top_k=5)
        display_results(top_results)

    except ValueError as ve:
        print(ve)
    except Exception as e:
        print(f"❌ Error occurred: {e}")
