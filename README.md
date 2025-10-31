# 🎥 QueryTube: YouTube Data Collection, Embedding & Semantic Search Platform

**QueryTube** is an end-to-end project that collects, processes, and analyzes YouTube video data, embeds textual content using AI models, and enables semantic search through vector similarity.  
It integrates **Python**, **ChromaDB**, **embedding models**, and a **React frontend** to deliver an intelligent video discovery experience.

---

## 📘 Table of Contents
1. [Overview](#overview)
2. [Features](#features)
3. [Tech Stack](#tech-stack)
4. [Project Structure](#project-structure)
5. [Pipeline Overview](#pipeline-overview)
6. [How to Run](#how-to-run)

---

## 🧠 Overview
QueryTube automates the collection of YouTube metadata and transcripts, processes them for quality, converts text into vector embeddings, and allows users to search semantically — finding videos by meaning, not just keywords.

---

## 🚀 Features
- 📦 Collect and preprocess YouTube video data and transcripts  
- 🧠 Generate text embeddings using transformer-based models  
- 💾 Store embeddings via **ChromaDB** vector database  
- 🔍 Expose a **search API** for semantic similarity queries  
- 💡 Simple, responsive **React frontend** for searching

---

## ⚙️ Tech Stack
**Backend:** Python, Flask, FastAPI, ChromaDB, Sentence Transformers  
**Frontend:** ReactJS  
**Database:** Local ChromaDB vector store  
**Other Tools:** Pandas, NumPy, Parquet, dotenv

---

## 📁 Project Structure
QueryTube/ │ ├── app.py                  # Flask API entry point ├── chromadb_manager.py     # Handles ChromaDB operations ├── embedding.py            # Embedding generation logic ├── search_engine.py        # Semantic search logic ├── test_api.py             # API testing and debugging ├── requirements.txt        # Python dependencies │ ├── Data/ │   ├── final_dataset_with_flag_transcript.csv │   ├── final_embedded_dataset.csv │   └── final_embedded_dataset.parquet │ ├── Frontend/ │   ├── App.jsx │   └── index.js │ └── README.md
 ---

## 🔄 Pipeline Overview

### 1️⃣ Data Preparation  
**Dataset:** `Data/final_dataset_with_flag_transcript.csv`  
- Cleans, filters, and validates YouTube video and transcript data.  
- Adds flags for missing transcripts or incomplete entries.

---

### 2️⃣ Embedding Generation  
**Script:** `embedding.py`  
- Uses a **Sentence Transformer model** to convert video transcripts into numerical embeddings.  
- Saves the results as:  
  - `Data/final_embedded_dataset.csv`  
  - `Data/final_embedded_dataset.parquet`

---

### 3️⃣ Vector Database (ChromaDB)  
**Script:** `chromadb_manager.py`  
- Loads and stores all embeddings inside a **ChromaDB collection** for fast similarity search.  
- Enables quick retrieval of top matches using cosine similarity.

---

### 4️⃣ Semantic Search Engine  
**Script:** `search_engine.py`  
- Handles **query preprocessing**, embedding generation for user text, and similarity comparison with stored vectors.  
- Returns **top 5–10 most relevant videos** with their similarity scores.

---

### 5️⃣ Backend API  
**Script:** `app.py`  
- Flask-based API that exposes semantic search functionality.  
- Accepts text queries and returns ranked video results in JSON format.

---

### 6️⃣ Frontend (React)  
**Directory:** `Frontend/`  
**Files:** `App.jsx`, `index.js`  
- Provides a simple and responsive **UI** for entering search queries.  
- Displays matching YouTube videos **ranked by semantic relevance**.  
- Built using **ReactJS** with dynamic rendering and clean layout.
