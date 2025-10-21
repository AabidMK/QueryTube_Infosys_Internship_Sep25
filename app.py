from flask import Flask, request, jsonify, render_template
from video_search_engine import VideoSearchEngine

app = Flask(__name__)
search_engine = VideoSearchEngine()

# Root endpoint - serves the frontend
@app.route("/", methods=["GET"])
def home():
    return render_template("index1.html")

# Search endpoint - called via AJAX
@app.route("/search", methods=["POST"])
def search_videos():
    try:
        data = request.get_json()
        query = data.get("query", "").strip()
        top_k = int(data.get("top_k", 5))

        if not query:
            return jsonify({"error": "Query cannot be empty"}), 400

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
