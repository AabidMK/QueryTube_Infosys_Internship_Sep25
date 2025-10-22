import os
import time
import json
from flask import Flask, request, jsonify
from chromadb import PersistentClient
import numpy as np
from flask_cors import CORS

def safe_int_convert(value, default=0):
    """Safely convert a value to int, handling empty strings and invalid values."""
    if value is None or value == '':
        return default
    try:
        return int(float(value))
    except (ValueError, TypeError):
        return default

def safe_float_convert(value, default=0.0):
    """Safely convert a value to float, handling empty strings and invalid values."""
    if value is None or value == '':
        return default
    try:
        return float(value)
    except (ValueError, TypeError):
        return default
CHROMA_BASE_PATH = r"C:\Users\dream\Desktop\Internships\Infosys Springboard\QueryTube\Task 5_ Merging Metadata & Transcripts\Storing_in_ChromaDB"
CHROMA_DB_PATH = os.path.join(CHROMA_BASE_PATH, "ChromaDB_Collection_Updated")
COLLECTION_NAME = "youtube_analysis_collection"

class VideoSearchEngine:
    """
    Initializes the ChromaDB client and handles all semantic search logic.
    """
    def __init__(self):
        if not os.path.exists(CHROMA_DB_PATH):
            raise FileNotFoundError(f"ChromaDB collection not found at {CHROMA_DB_PATH}")
        
        # Initialize client to load the existing database persistently
        self.client = PersistentClient(path=CHROMA_DB_PATH)
        self.collection = self.client.get_collection(name=COLLECTION_NAME)

    def search(self, query: str, offset: int = 0, limit: int = 10):
        """
        Performs semantic search with pagination support.
        Args:
            query: Search query string
            offset: Number of results to skip
            limit: Maximum number of results to return
        """
        start_time = time.time()
        
        # Calculate how many results to fetch
        fetch_count = min(offset + limit, self.collection.count())
        
        # For empty query, get all documents; otherwise do semantic search
        if not query or query.strip() == "":
            # Get all documents with pagination
            results = self.collection.get(
                limit=fetch_count,
                offset=0,
                include=['metadatas', 'documents']
            )
            # Convert to query format for consistency
            if results and results.get('metadatas'):
                results = {
                    'metadatas': [results['metadatas']],
                    'distances': [[0.0] * len(results['metadatas'])],  # No distance for get()
                    'documents': [results.get('documents', [])]
                }
        else:
            # ChromaDB handles the query embedding and performs the search
            results = self.collection.query(
                query_texts=[query],
                n_results=fetch_count,
                include=['metadatas', 'distances', 'documents']
            )
        
        end_time = time.time()
        
        formatted_results = []
        
        if results and results.get('metadatas') and len(results['metadatas'][0]) > 0:
            metadatas = results['metadatas'][0][offset:offset+limit]
            distances = results['distances'][0][offset:offset+limit]
            documents = results.get('documents', [[]])[0][offset:offset+limit]  # Get the transcript text
            
            for idx, (metadata, distance) in enumerate(zip(metadatas, distances)):
                # ChromaDB with cosine distance returns values where:
                # - 0 means identical vectors (perfect match)
                # - 2 means opposite vectors (completely different)
                # Convert to similarity score (0-1 where 1 is best match)
                # Formula: similarity = (2 - distance) / 2
                # This maps: distance 0 -> similarity 1.0, distance 2 -> similarity 0.0
                similarity_score = max(0, min(1, (2 - distance) / 2))
                
                # Get the transcript if available, otherwise use empty string
                transcript = documents[idx] if idx < len(documents) else ''
                
                # Extract video ID from metadata
                video_id = (
                    str(metadata.get('original_id', '')) or
                    str(metadata.get('id', '')).split('_')[-1] or
                    next((v for v in metadata.values() 
                         if isinstance(v, str) and len(v) == 11 and v.isalnum()), '')
                ).strip()
                
                result = {
                    'video_id': video_id,
                    'title': str(metadata.get('title', 'No Title')).strip(),
                    'channel': str(metadata.get('channel_title', 'Unknown Channel')).strip(),
                    'views': int(float(metadata.get('viewCount', metadata.get('views', 0)))),
                    'likes': int(float(metadata.get('likeCount', metadata.get('likes', 0)))),
                    'published_at': str(metadata.get('publishedAt', metadata.get('published_at', ''))).strip(),
                    'description': str(metadata.get('description', '')).strip(),
                    'transcript': str(transcript or '').strip(),
                    'similarity_score': round(similarity_score, 3),
                    'comment_count': int(float(metadata.get('commentCount', metadata.get('comment_count', 0)))),
                    'duration': int(float(metadata.get('duration', metadata.get('duration_seconds', 0)))),
                    'is_short': str(metadata.get('is_short', 'False')).lower() in ['true', '1', 'yes'],
                    'thumbnail_url': f'https://img.youtube.com/vi/{video_id}/maxresdefault.jpg',
                    'video_url': f'https://www.youtube.com/watch?v={video_id}'
                }
                
                # Only add URLs if we have a valid video_id
                if video_id:
                    result.update({
                        'thumbnail_url': f'https://img.youtube.com/vi/{video_id}/maxresdefault.jpg',
                        'video_url': f'https://www.youtube.com/watch?v={video_id}'
                    })
                else:
                    # Fallback to empty URLs if no video_id is found
                    result.update({
                        'thumbnail_url': '',
                        'video_url': ''
                    })
                
                formatted_results.append(result)
                
        # Calculate search latency
        latency = round(end_time - start_time, 4)
        
        return {
            "query": query,
            "latency_seconds": latency,
            "total_results": len(formatted_results),
            "results": formatted_results,
            "has_more": len(formatted_results) == limit
        }

# --- 1. API Setup ---

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize the search engine globally so it only loads once
try:
    search_engine = VideoSearchEngine()
except FileNotFoundError as e:
    print(e)
    # Exit gracefully if the database isn't found
    search_engine = None
    
# Initialize the search engine
search_engine = None
try:
    search_engine = VideoSearchEngine()
except FileNotFoundError as e:
    print(f"Error: {e}")
    search_engine = None

@app.route('/initial-videos', methods=['GET'])
def get_initial_videos():
    """
    API endpoint to get initial videos for the home page with pagination
    Query params:
        offset: Number of results to skip (default: 0)
        limit: Maximum number of results to return (default: 10, max: 50)
    """
    if not search_engine:
        return jsonify({"error": "Search engine not initialized"}), 500

    try:
        # Get pagination parameters
        offset = max(0, int(request.args.get('offset', 0)))
        limit = min(50, max(1, int(request.args.get('limit', 10))))
        
        # Check if offset exceeds total collection count
        total_count = search_engine.collection.count()
        if offset >= total_count:
            # Return empty result when offset exceeds available data
            return jsonify({
                'videos': [],
                'has_more': False,
                'total': 0
            })
        
        # Use an empty query to get random videos with pagination
        results = search_engine.search("", offset, limit)
        videos = []
        
        if 'results' in results:
            for result in results['results']:
                video = {
                    'video_id': result.get('video_id', ''),
                    'title': result.get('title', ''),
                    'channel': result.get('channel', ''),
                    'views': result.get('views', 0),
                    'likes': result.get('likes', 0),
                    'published_at': result.get('published_at', ''),
                    'description': result.get('description', ''),
                    'duration': result.get('duration', 0),
                    'is_short': bool(result.get('is_short', False)),
                    'thumbnail_url': result.get('thumbnail_url', ''),
                    'video_url': result.get('video_url', '')
                }
                videos.append(video)
        
        # Check if there are more videos available
        has_more = (offset + len(videos)) < total_count
        
        return jsonify({
            'videos': videos,
            'has_more': has_more,
            'total': len(videos)
        })
    except Exception as e:
        print(f"Error in get_initial_videos: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/search', methods=['POST'])
def search_api():
    """
    API endpoint to handle semantic search queries.
    Accepts JSON body: {"query": "...", "offset": N, "limit": M}
    """
    if not search_engine:
        return jsonify({"error": "Semantic search engine not initialized. Check server logs."}), 500
        
    data = request.get_json()
    query = (data or {}).get('query', '')
    offset = max(0, int((data or {}).get('offset', 0)))
    limit = min(50, max(1, int((data or {}).get('limit', 10))))

    # 1. Input Validation
    if not query or len(query.strip()) < 3:
        return jsonify({"error": "Invalid query provided. Query must be at least 3 characters long."}), 400

    try:
        # 2. Perform Search with pagination
        results = search_engine.search(query, offset=offset, limit=limit)
        videos = []

        if 'results' in results:
            for result in results['results']:
                video = {
                    'video_id': result.get('video_id', ''),
                    'title': result.get('title', ''),
                    'channel': result.get('channel', ''),
                    'views': result.get('views', 0),
                    'likes': result.get('likes', 0),
                    'published_at': result.get('published_at', ''),
                    'description': result.get('description', ''),
                    'duration': result.get('duration', 0),
                    'is_short': bool(result.get('is_short', False)),
                    'thumbnail_url': result.get('thumbnail_url', ''),
                    'video_url': result.get('video_url', ''),
                    'similarity_score': result.get('similarity_score', 0)
                }
                videos.append(video)

        return jsonify({
            'results': videos,
            'has_more': results.get('has_more', False),
            'total': len(videos)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Flask runs in debug mode by default, suitable for testing
    app.run(host='0.0.0.0', port=5000)
