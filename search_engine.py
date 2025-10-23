import re
import numpy as np
from sentence_transformers import SentenceTransformer
from chromadb_manager import ChromaDBManager


class SearchEngine:
    def __init__(self):
        self.db_manager = ChromaDBManager()
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

    def apply_prompt_template(self, query):
        self.template = (
            f"""
            You are performing a semantic search over YouTube video transcripts and metadata.
            Focus on understanding the real meaning of the user's query.

            User query: {query}

            Return only results that directly relate to the query topic.
            """
        )
        return self.template

    # Generate embedding for user query
    def generate_embedding(self, query):
        return np.array(self.model.encode(query))

    # Format, filter, and display top 5 results with video link & thumbnail
    def format_and_display(self, results, min_similarity=0.5):
        hits = results['metadatas'][0]
        distances = results['distances'][0]

        scored_results = []
        for meta, dist in zip(hits, distances):
            similarity = 1 - (dist / 2)
            similarity = max(0.0, min(similarity, 1.0))  # clamp

            # ✅ Fetch YouTube video ID from metadata
            video_id = meta.get("id") or meta.get("video_id") or "N/A"

            # ✅ Build full YouTube link & thumbnail
            video_url = f"https://www.youtube.com/watch?v={video_id}" if video_id != "N/A" else "N/A"
            thumbnail_url = f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg" if video_id != "N/A" else "N/A"

            scored_results.append({
                "rank": None,  # will be filled later
                "title": meta.get("title", "N/A"),
                "channel_title": meta.get("channel_title", "N/A"),
                "similarity": round(similarity, 3),
                "video_id": video_id,
                "video_url": video_url,
                "thumbnail_url": thumbnail_url
            })

        # Sort by similarity descending
        scored_results.sort(key=lambda x: x["similarity"], reverse=True)

        # Filter by minimum similarity
        filtered = [r for r in scored_results if r["similarity"] >= min_similarity]

        # If no strong matches, show top 5 closest
        if not filtered:
            print("⚠️ No results above similarity threshold. Showing top 5 closest results instead.\n")
            filtered = scored_results[:5]
        else:
            filtered = filtered[:5]

        # Add rank numbers
        for idx, item in enumerate(filtered, start=1):
            item["rank"] = idx

        # Print results
        print("\nTop Results:\n" + "=" * 60)
        for item in filtered:
            print(f"Rank: {item['rank']}")
            print(f"Title: {item['title']}")
            print(f"Channel: {item['channel_title']}")
            print(f"Similarity: {item['similarity']:.3f}")
            print(f"Video URL: {item['video_url']}")
            print(f"Thumbnail: {item['thumbnail_url']}")
            print("-" * 60)

        return filtered


# ---------------------------
# Main execution
# ---------------------------
if __name__ == "__main__":
    engine = SearchEngine()

    query = input("Enter your search query: ").strip()
    while not query:
        print("❌ Query cannot be empty")
        query = input("Enter your search query: ").strip()

    # Clean query text
    query = re.sub(r"[^\w\s]", "", query)

    min_similarity = 0.5

    # Generate embedding & query database
    embedding = engine.generate_embedding(query)
    results = engine.db_manager.query_embeddings(embedding, top_k=50)

    # Display formatted results
    engine.format_and_display(results, min_similarity=min_similarity)
