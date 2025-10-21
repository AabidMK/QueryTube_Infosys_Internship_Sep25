from flask import Flask, request, jsonify
from video_search_engine import VideoSearchEngine

app = Flask(__name__)
search_engine = VideoSearchEngine()

# Root endpoint
@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "✅ Semantic Video Search API is running!",
        "usage": {
            "POST /search": {
                "query": "your text query",
                "top_k": "optional number of results (default = 5)"
            }
        }
    })

# Search endpoint
@app.route("/search", methods=["POST"])
def search_videos():
    try:
        data = request.get_json()
        query = data.get("query", "").strip()
        top_k = int(data.get("top_k", 5))

        if not query:
            return jsonify({"error": "Query cannot be empty"}), 400

        # Perform semantic search
        results = search_engine.search(query, top_k)

        return jsonify({
            "query": query,
            "top_k": top_k,
            "results": results
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
