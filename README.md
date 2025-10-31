# 🧠 YouTube Semantic Search

![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-green)
![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector%20Database-orange)
![License](https://img.shields.io/badge/License-MIT-blue.svg)
![Stars](https://img.shields.io/github/stars/<your-username>/youtube-semantic-search?style=social)

> 🚀 A semantic search engine that finds **YouTube videos by meaning**, not just keywords — built with FastAPI, ChromaDB, and Sentence Transformers.

---

## 🌟 Features

- 🎯 **Semantic Search:** Understands *meaning*, not just keywords  
- 🧠 **Transformer Embeddings:** Uses `all-MiniLM-L6-v2` for vector encoding  
- 💾 **Persistent Storage:** Powered by **ChromaDB**  
- ⚡ **FastAPI Backend:** Handles search requests efficiently  
- 🌐 **Frontend Integration:** Built with HTML, CSS, and JS  
- 🖼️ **Smart Thumbnails:** Auto-fallback to YouTube logo when unavailable  
- 🔒 **CORS Enabled:** Easy connection between frontend and backend  

---

## 🏗️ Project Structure

```
youtube-semantic-search/
│
├── data/
│   ├── Merged_Video_Transcript.csv       # Dataset with transcript info
│   └── chroma_db/                        # Persistent ChromaDB storage
│
├── src/
│   ├── embed.py                          # Embedding + ChromaDB storage
│   └── main.py                           # FastAPI backend API
│
├── frontend/
│   ├── index.html                        # Web interface
│   ├── script.js                         # Frontend logic + API calls
│   └── styles.css                        # Styling (optional)
│
└── README.md
```

---

## ⚙️ Tech Stack

| Component | Technology |
|------------|-------------|
| **Backend** | FastAPI |
| **Database** | ChromaDB |
| **Embedding Model** | SentenceTransformer (`all-MiniLM-L6-v2`) |
| **Frontend** | HTML, CSS, JavaScript |
| **Language** | Python 3.10+ |

---

## 🧩 Setup & Installation

### 1️⃣ Clone Repository
```bash
git clone https://github.com/<your-username>/youtube-semantic-search.git
cd youtube-semantic-search
```

### 2️⃣ Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate       # macOS/Linux
venv\Scripts\activate          # Windows
```

### 3️⃣ Install Dependencies
```bash
pip install fastapi uvicorn chromadb sentence-transformers pandas
```

### 4️⃣ Prepare Dataset
Place your dataset at:
```
data/Merged_Video_Transcript.csv
```
Ensure it includes:
`id`, `title`, `channel_title`, `description`, `transcript`, `thumbnail_high`

### 5️⃣ Generate Embeddings
```bash
python src/embed.py
```
✅ Creates vector database in `data/chroma_db/`

### 6️⃣ Run Backend Server
```bash
uvicorn src.main:app --reload
```
API: [http://127.0.0.1:8000](http://127.0.0.1:8000)

### 7️⃣ Launch Frontend
Open `frontend/index.html` in your browser and start searching 🔍

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|---------|-----------|-------------|
| `GET` | `/search?query=<text>&top_k=5` | Returns top relevant YouTube videos |

**Example Response**
```json
{
  "query": "machine learning basics",
  "results": [
    {
      "rank": 1,
      "title": "Intro to Machine Learning",
      "channel_title": "Simplilearn",
      "description": "An overview of ML concepts...",
      "url": "https://www.youtube.com/watch?v=abcd1234",
      "thumbnail": "https://i.ytimg.com/vi/abcd1234/hqdefault.jpg",
      "similarity_score": 0.873
    }
  ]
}
```

---

## 💡 How It Works

### 🔹 Embedding Phase (`embed.py`)
- Loads dataset  
- Cleans missing data  
- Generates vector embeddings using `SentenceTransformer`  
- Stores in **ChromaDB** using cosine similarity  

### 🔹 Search Phase (`main.py`)
- Takes user query  
- Encodes into a semantic vector  
- Finds top-k similar videos  
- Returns metadata to frontend  

---

## 🖼️ Screenshots

| Interface | Description |
|------------|-------------|
| ![YouTube Logo](https://upload.wikimedia.org/wikipedia/commons/b/b8/YouTube_Logo_2017.svg) | Minimal Search Interface |
| *(Coming Soon)* | Semantic Search Results View |

---

## 🔮 Future Enhancements

- ✅ Add result pagination  
- 🧩 Support for multiple channels  
- 📊 Integrate LangChain for advanced retrieval  
- ☁️ Deploy via Render / Vercel / HuggingFace Spaces  

---

## 🧾 License

This project is licensed under the [MIT License](LICENSE).

---

## ⭐ Support

If you found this project helpful:
- Star ⭐ the repository  
- Contribute 🤝 via PRs  
- Share your feedback 💬  

---

**Made with ❤️ using FastAPI, Sentence Transformers, and ChromaDB**
