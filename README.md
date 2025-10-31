# 🎯 QueryTube – A YouTube Semantic Search Engine

**QueryTube** is an AI-powered YouTube Semantic Search Engine that goes beyond keyword matching. It understands the *context* of user queries to find the most relevant YouTube videos using **embeddings**, **ChromaDB**, and **FastAPI**.

---

## 🚀 Features
- 🔍 **Semantic Search:** Finds videos based on meaning, not just keywords.  
- 🎥 **YouTube API Integration:** Fetches video data and transcriptions directly from YouTube.  
- 🧠 **Embeddings & NLP:** Generates embeddings to understand contextual relationships.  
- 💾 **ChromaDB Vector Store:** Stores and retrieves embeddings for fast similarity search.  
- ⚡ **FastAPI Backend:** Handles search requests and delivers relevant video results.  
- 🖥️ **Frontend Interface:** Simple and responsive UI for smooth user experience.

---

## 🧩 Tech Stack
- **Python**
- **FastAPI**
- **YouTube Data API**
- **ChromaDB**
- **LangChain / Sentence Transformers**
- **HTML, CSS, JavaScript**

---

## ⚙️ How It Works
1. Fetch YouTube video metadata and transcriptions using **YouTube Data API**.  
2. Clean and preprocess transcription data.  
3. Generate **text embeddings** for each video using a pre-trained model.  
4. Store embeddings in **ChromaDB** for semantic retrieval.  
5. Use **FastAPI** to serve search queries and fetch relevant results.  
6. Display top-matching videos on the **frontend interface**.


---

## 🧠 Project Architecture

QueryTube/
│

├── backend/
│ ├── main.py # FastAPI backend
│ ├── embeddings.py # Embedding generation logic
│ ├── db.py # ChromaDB setup and storage
│ └── utils.py # Data cleaning and helpers
│

├── frontend/
│ ├── index.html # Main UI
│ ├── style.css # Styling
│ └── script.js # API calls and interactivity
│

├── requirements.txt
└── README.md


## 🧰 Installation

```bash
# Clone the repository
git clone https://github.com/<your-username>/QueryTube.git

# Navigate to project directory
cd QueryTube

# Install dependencies
pip install -r requirements.txt
