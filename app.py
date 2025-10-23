from flask import Flask, request, jsonify
from flask_cors import CORS
from VideoSearchEngine import VideoSearchEngine

app = Flask(__name__)
CORS(app)  # Enable CORS

search_engine = VideoSearchEngine(
    collection_name="video_embeddings",
    db_path="chroma_db",
    model_name="all-MiniLM-L6-v2"
)

@app.route("/search", methods=["POST"])
def search():
    data = request.get_json()
    if not data or "query" not in data:
        return jsonify({"error": "Missing 'query' in request body"}), 400

    query = data["query"]
    top_k = int(data.get("top_k", 5))

    results = search_engine.search(query, top_k=top_k)
    return jsonify({"results": results})

if __name__ == "__main__":
    app.run(debug=True)
