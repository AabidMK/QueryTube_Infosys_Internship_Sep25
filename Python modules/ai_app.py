from flask import Flask, request, jsonify, render_template
from Search_Query_main import search_youtube_videos  # ✅ Import your function
from flask_cors import CORS
import os
# app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_DIR = os.path.join(BASE_DIR, 'frontend')
app = Flask(__name__, template_folder=TEMPLATE_DIR)
CORS(app, origins="*", supports_credentials=True)# Root endpoint - serves the frontend
@app.route("/", methods=["GET"])
def home():
    return render_template("index1.html")  # ✅ Your frontend UI

# Search endpoint - API for searching YouTube videos
@app.route("/search", methods=["POST"])
def search_videos():
    try:
        data = request.get_json()
        query = data.get("query", "").strip()
        top_k = int(data.get("top_k", 5))

        if not query:
            return jsonify({"error": "Query cannot be empty"}), 400

        # ✅ Use your ChromaDB search function
        results = search_youtube_videos(query, top_k)

        return jsonify({
            "query": query,
            "top_k": top_k,
            "results": results
        })

    except Exception as e:
        print("Error:", e)  # ✅ Log server side error
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
