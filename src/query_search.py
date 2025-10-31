import chromadb
from sentence_transformers import SentenceTransformer
import numpy as np
from colorama import Fore, Style, init

# Initialize colorama for Windows PowerShell
init(autoreset=True)

def cosine_similarity(a, b):
    """Compute cosine similarity between two vectors."""
    a, b = np.array(a), np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def color_for_similarity(score):
    """Return color based on similarity range."""
    if score >= 0.85:
        return Fore.GREEN
    elif score >= 0.6:
        return Fore.YELLOW
    else:
        return Fore.RED

def main():
    print("\n🔎 Enter your search query: ", end="")
    query = input().strip()

    print("\n🔍 Connecting to ChromaDB...")
    client = chromadb.PersistentClient(path="./data/chroma_db")
    collection = client.get_or_create_collection("youtube_videos")

    print("🔹 Loading embedding model...")
    model = SentenceTransformer("all-MiniLM-L6-v2")

    print("🔹 Generating embedding for query...")
    query_embedding = model.encode(query)

    print("🔹 Searching top 10 relevant results...\n")
    results = collection.query(
        query_embeddings=[query_embedding.tolist()],
        n_results=10,
        include=["embeddings", "metadatas"]
    )

    if not results["metadatas"][0]:
        print("⚠️ No results found. Try a different query.")
        return

    # Compute cosine similarity manually for accuracy
    similarities = []
    for idx, emb in enumerate(results["embeddings"][0]):
        sim = cosine_similarity(query_embedding, emb)
        similarities.append(sim)

    # Sort by descending similarity
    sorted_indices = np.argsort(similarities)[::-1]

    for rank, idx in enumerate(sorted_indices[:5], start=1):
        metadata = results["metadatas"][0][idx]
        similarity = round(float(similarities[idx]), 3)
        color = color_for_similarity(similarity)

        title = metadata.get("title", "Unknown Title")
        channel_title = metadata.get("channel_title", "Unknown Channel")
        description = metadata.get("description", "No description")[:250].replace("\n", " ")
        url = metadata.get("url", "N/A")

        print(f"{color}🎬 Rank {rank} — (Similarity: {similarity}){Style.RESET_ALL}")
        print(f"   ▶ Title: {title}")
        print(f"   📺 Channel: {channel_title}")
        print(f"   📝 Description: {description}...")
        print(f"   🔗 URL: {url}\n")

if __name__ == "__main__":
    main()
