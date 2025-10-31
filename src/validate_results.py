# validate_results.py
import chromadb
from sentence_transformers import SentenceTransformer
import numpy as np
import requests
import re

# CONFIG
CHROMA_PATH = "../chroma_db"
COLLECTION_NAME = "youtube_videos"
MODEL_NAME = "all-MiniLM-L6-v2"
TOP_K = 5
SIMILARITY_THRESHOLD = 0.45   # adjust: >0.6 is strong, 0.4-0.6 borderline

# Helpers
def normalize_text(s: str) -> str:
    return (s or "").lower()

def token_matches(text: str, query: str) -> bool:
    # basic token presence check (all tokens)
    qtok = [t for t in re.split(r"\s+", query.lower().strip()) if t]
    if not qtok:
        return False
    text_low = normalize_text(text)
    return all(any(tok in part for part in [text_low]) for tok in qtok)

def is_reachable(url: str, timeout=4):
    if not url or not url.startswith("http"):
        return False
    try:
        resp = requests.head(url, allow_redirects=True, timeout=timeout)
        return resp.status_code == 200
    except Exception:
        return False

# Connect
print("Connecting to ChromaDB...")
client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = client.get_collection(COLLECTION_NAME)
print("Loading embedding model...")
model = SentenceTransformer(MODEL_NAME)

# Queries to test — modify or add more
queries = [
    "python",
    "pandas and numpy",
    "dsa for beginners",
    "AI Roadmap",
    "funny vloggers"
]

for query in queries:
    print("\n" + "="*70)
    print(f"Query: {query}")
    q_emb = model.encode(query)
    results = collection.query(query_embeddings=[q_emb], n_results=TOP_K, include=["metadatas", "embeddings"])
    for i in range(len(results["ids"][0])):
        meta = results["metadatas"][0][i]
        emb = np.array(results["embeddings"][0][i])
        # cosine
        cos_sim = float(np.dot(q_emb, emb) / (np.linalg.norm(q_emb)*np.linalg.norm(emb)))
        sim01 = round(cos_sim, 3)

        title = meta.get("title","")
        channel = meta.get("channel_title","")
        desc = meta.get("description","")
        url = meta.get("url","")

        t_match = token_matches(title, query)
        d_match = token_matches(desc, query)
        c_match = token_matches(channel, query)
        reachable = is_reachable(url)

        relevance = "OK" if (sim01 >= SIMILARITY_THRESHOLD or t_match or d_match) else "SUSPICIOUS"

        print(f"\n#{i+1}  Title: {title}")
        print(f"     Channel: {channel}")
        print(f"     Sim: {sim01}  | Relevance: {relevance}")
        print(f"     title_has_query: {t_match}  desc_has_query: {d_match}  channel_has_query: {c_match}")
        print(f"     URL: {url}  reachable: {reachable}")
        clean_desc = desc[:180].replace("\n", " ")
    print(f"     Desc-preview: {clean_desc}...")

    print("="*70)
