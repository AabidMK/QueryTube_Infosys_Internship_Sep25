from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import chromadb
from sentence_transformers import SentenceTransformer
import os

# === CONFIG ===
app = Flask(__name__, template_folder="templates")
CORS(app)

CHROMA_PATH = r"C:\Users\balak\OneDrive\Desktop\Youtube_Query\chroma_db"
COLLECTION_NAME = "video_embeddings"
MODEL_NAME = "all-MiniLM-L6-v2"

# === LOAD MODEL AND CHROMADB ===
print("🧠 Loading model and ChromaDB...")
model = SentenceTransformer(MODEL_NAME)
chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = chroma_client.get_collection(name=COLLECTION_NAME)
print("✅ Ready.")

# === ROUTES ===
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/search", methods=["POST"])
def search_videos():
    """Perform semantic search and return top results as JSON"""
    data = request.get_json()
    query = data.get("query", "").strip()

    if not query:
        return jsonify({"error": "Empty query"}), 400

    try:
        # Encode query to vector
        query_embedding = model.encode(query, convert_to_numpy=True)

        # Query Chroma
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=5,
            include=["metadatas", "documents", "distances"]
        )

        # Prepare response
        output = []
        metadatas = results.get("metadatas", [[]])[0]
        docs = results.get("documents", [[]])[0]
        distances = results.get("distances", [[]])[0]

        for meta, doc, dist in zip(metadatas, docs, distances):
            similarity = round(1 / (1 + dist), 3)
            similarity_percent = round(similarity * 100, 2)
            snippet = " ".join(doc.split()[:100]) + "..."
            output.append({
                "title": meta.get("title", "Untitled"),
                "channel": meta.get("channel_title", "Unknown Channel"),
                "thumbnail": meta.get("thumbnail", ""),  # if you stored it
                "url": meta.get("url", "#"),              # if you stored it
                "similarity": similarity,
                "similarity_percent": f"{similarity_percent}%",
                "transcript": snippet
            })

        return jsonify({"results": output})

    except Exception as e:
        print("❌ Error:", e)
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
