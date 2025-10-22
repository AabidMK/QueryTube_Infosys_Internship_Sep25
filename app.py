from flask import Flask, request, jsonify
from flask_cors import CORS
from video_search_engine import VideoSearchEngine

app = Flask(__name__)
CORS(app)

search_engine = VideoSearchEngine()

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "✅ Semantic Video Search API is running!",
        "usage": "POST to /search with {'query': 'your text', 'top_k': 5}"
    })

@app.route("/search", methods=["POST"])
def search_videos():
    try:
        data = request.get_json()
        query = data.get("query", "").strip()
        top_k = int(data.get("top_k", 5))

        if not query:
            return jsonify({"error": "Query cannot be empty"}), 400

        # Perform semantic search
        result_obj = search_engine.search(query, top_k)

        # ✅ Fix the response shape
        return jsonify(result_obj["results"])

    except Exception as e:
        print("❌ Error in /search:", str(e))
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
