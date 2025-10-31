from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from threading import Thread
from sentence_transformers import SentenceTransformer, util
import torch
import json
import os

# ========================================
# 🚀 VideoSearchEngine (Semantic Search)
# ========================================

class VideoSearchEngine:
    def __init__(self, data_path="videos.json"):
        if not os.path.exists(data_path):
            # Create a small dataset
            sample_data = [
                {"title": "Flask Tutorial", "description": "Learn Flask web development from scratch", "url": "https://youtu.be/Z1RJmh_OqeA"},
                {"title": "FastAPI Crash Course", "description": "Build modern APIs using FastAPI", "url": "https://youtu.be/0RS0B59A_GI"},
                {"title": "Python for Data Science", "description": "Data Science and analysis using Python", "url": "https://youtu.be/LHBE6Q9XlzI"},
                {"title": "Machine Learning Basics", "description": "Learn ML algorithms and AI concepts", "url": "https://youtu.be/GwIo3gDZCVQ"},
                {"title": "Data Visualization in Python", "description": "Learn Matplotlib, Seaborn, and visualization", "url": "https://youtu.be/0P7QnIQDBJY"},
                {"title": "Deep Learning Tutorial", "description": "Neural networks and deep learning with Python", "url": "https://youtu.be/tPYj3fFJGjk"}
            ]
            with open(data_path, "w") as f:
                json.dump(sample_data, f, indent=4)

        with open(data_path, "r") as f:
            self.videos = json.load(f)

        # Load pretrained semantic model
        print("🔄 Loading semantic model... please wait (only once)...")
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

        # Encode video corpus
        corpus_texts = [v["title"] + " " + v["description"] for v in self.videos]
        self.corpus_embeddings = self.model.encode(corpus_texts, convert_to_tensor=True)
        print("✅ Model loaded successfully!")

    def search(self, query, top_k=5):
        query_embedding = self.model.encode(query, convert_to_tensor=True)
        scores = util.pytorch_cos_sim(query_embedding, self.corpus_embeddings)[0]
        top_results = torch.topk(scores, k=min(top_k, len(self.videos)))

        results = []
        for score, idx in zip(top_results.values, top_results.indices):
            s = round(float(score), 3)
            if s > 0.35:  # ignore weak matches
                video = self.videos[idx]
                results.append({
                    "title": video["title"],
                    "description": video["description"],
                    "url": video["url"],
                    "score": s
                })
        if not results:
            results = [{"title": "No relevant videos found", "description": "", "url": "#", "score": 0}]
        return results


# ========================================
# ⚙️ Flask App Setup
# ========================================

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)
search_engine = VideoSearchEngine(data_path="videos.json")


@app.route('/search', methods=['POST', 'OPTIONS'])
@cross_origin(origin='*', headers=['Content-Type', 'Authorization'])
def search_videos():
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
        response.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
        return response

    try:
        data = request.get_json(force=True)
        query = data.get("query", "").strip()
        top_k = int(data.get("top_k", 5))

        if not query:
            return jsonify({"error": "Query is required"}), 400

        results = search_engine.search(query=query, top_k=top_k)
        return jsonify({"query": query, "results": results})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ========================================
# ▶️ Run Flask in Background (for notebook use)
# ========================================

def run_app():
    app.run(host='127.0.0.1', port=5000, debug=True, use_reloader=False)

Thread(target=run_app).start()
