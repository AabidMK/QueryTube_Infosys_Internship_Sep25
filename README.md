
# QueryTube_Infosys_Internship_Sep25
## AI_SemanticSearchTube. Building a Semantic Search App with YouTube Data 

> **AI_SemanticSearchTube** – A powerful semantic search application that enables intelligent, context-aware querying over YouTube video data using advanced AI and vector embeddings.




---

## 🚀 Features

- **Semantic Search** over YouTube videos using embeddings. Find content based on *meaning* rather than exact keywords.
- Natural language queries (e.g., *"what is the best way to explain deep learning to a beginner"* or *"building wells in Africa"*).
- Leverages **ChromaDB** for efficient vector storage and retrieval.
- Modular, full-stack design featuring a **FastAPI** backend and a **Streamlit** frontend.
- Indexes video titles, descriptions, and transcripts (up to 4000 characters) for high-relevance search.

---

## 🛠️ Technology Stack

| Component | Technology | Role |
| :--- | :--- | :--- |
| **Vector Database** | **ChromaDB** | Stores the vector embeddings of video content. |
| **Embedding Model** | **Sentence-BERT (SBERT)** | Converts natural language text (content and query) into numerical vectors. |
| **Backend API** | **FastAPI** | High-performance service for handling search requests and performing vector lookups (`http://localhost:8000`). |
| **Frontend UI** | **Streamlit** | Interactive, user-friendly interface for querying and displaying results (`http://localhost:8501`). |

---

## ⚙️ System Architecture

The search process follows a robust three-stage pipeline: 

1.  **Indexing (`chroma_upload_code.py`):** Video text data is converted into a vector using the SBERT model and stored in **ChromaDB**.
2.  **Querying (Backend `backend.py`):** The user's query is converted into a vector by the FastAPI backend.
3.  **Search (ChromaDB):** ChromaDB performs a nearest-neighbor search to find videos with the highest **cosine similarity** to the query vector.

---

## 📂 Project Structure

| File Name | Component | Description |
| :--- | :--- | :--- |
| `chroma_upload_code.py` | **Indexer** | **FIRST STEP:** Loads data, generates SBERT embeddings, and builds the ChromaDB vector index. |
| `backend.py` | **Backend API** | FastAPI application. Contains the `VideoSearchEngine` and exposes the `/search` endpoint. **Must be running first.** |
| `frontend.py` | **Frontend UI** | Streamlit application. Provides the GUI, calls the backend API, and formats the video results. |
| `query_search_code.py` | **Utility** | A simple command-line script to test the core search logic without the full web stack. |
| `videos_with_embeddings_cleaned.csv` | **Data Source** | The master CSV file containing the unique video metadata and transcripts used for indexing. |
| `chromadb_data/` | **Database** | Directory containing the persisted ChromaDB vector store. |

---

## 🛠️ Setup Instructions

### 1. Prerequisites

Ensure you have **Python 3.8+** installed.

### 2. Installation

Clone the repository and install the necessary dependencies:

```bash
# Clone the repository
git clone <YOUR_REPO_URL>
cd QueryTube_Infosys_Internship_Sep25

# Install dependencies (Required packages for all files)
pip install pandas numpy sentence-transformers chromadb fastapi uvicorn requests streamlit
````

### 3\. Build the Vector Database (Essential First Step)

You must run the indexing script first. This process downloads the **Sentence-BERT (SBERT)** model, loads your video data from the CSV, generates the embeddings, and populates the **ChromaDB** collection.

```bash
python chroma_upload_code.py
```

### 4\. Start the Backend API

The **FastAPI backend** handles all the heavy lifting (query embedding and vector search). Open your first terminal window and start this service; the frontend cannot function without it.

```bash
python backend.py
# The API will be available at http://localhost:8000
```

### 5\. Launch the Frontend

Open a second terminal window and start the **Streamlit application**.

```bash
streamlit run frontend.py
# The UI will open automatically in your browser (http://localhost:8501)
```

-----

## 💡 Usage

1.  **Open** the Streamlit application in your browser (`http://localhost:8501`).
2.  **Enter a conceptual query** in the search bar.
3.  Click **"Search Videos"**. The frontend communicates with the running backend API to retrieve the most semantically relevant videos based on your query's meaning.

<!-- end list -->
