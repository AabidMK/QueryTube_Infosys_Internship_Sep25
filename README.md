# QueryTube_Infosys_Internship_Sep25
### *AI_SemanticSearchTube. Building a Semantic Search App with YouTube Data*

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.8+-yellow.svg)
![Transformers](https://img.shields.io/badge/Transformers-NLP-orange.svg)
![YouTube API](https://img.shields.io/badge/API-YouTube-red.svg)

---

## 📘 Overview  
**QueryTube** is an intelligent semantic video search engine that understands *meaning*, not just keywords.  
It uses transformer-based NLP models to process **titles and transcripts** of YouTube videos, allowing users to search using natural language and find the **top-5 most semantically relevant results**.

---

## 🎯 Project Goal  
Traditional keyword-based YouTube search fails to capture context.  
QueryTube solves this by combining **YouTube Data APIs**, **sentence transformers**, and **semantic similarity techniques** to deliver results that *mean* what the user is looking for — not just what they typed.

---

## ⚙️ Key Features  
- 🔍 **Semantic Search:** Retrieves videos by meaning, not literal word match.  
- 🎥 **YouTube Data Integration:** Fetches video titles, metadata, and transcripts via YouTube APIs.  
- 🤖 **Transformer Embeddings:** Uses Sentence-BERT or MiniLM for text embeddings.  
- 📊 **Similarity Scoring:** Applies cosine similarity to rank videos.  
- 🌐 **Deployable Web App:** A simple interactive app built using Flask or Streamlit.  

---

## 🧱 Repository Structure  

```
QueryTube_Infosys_Internship_Sep25/
├── data/                          # Raw & cleaned data
├── notebooks/                     # Jupyter notebooks for analysis
│   ├── cleaning_transcripts.ipynb
│   ├── embeddings.ipynb
│   ├── chromadb.ipynb
│   └── other notebooks...
│
├── src/                          # Source code
│   ├── Milestone1.py            # YouTube Data Collection
│   ├── Milestone2.ipynb         # Transcript Cleaning
│   ├── video_search_engine.py   # Semantic search logic
│   ├── youtube_channel_details.py # Metadata & channel info
│   └── app.py                   # Frontend/backend interface
│
├── cleaned_transcripts.xls        # Clean transcript data
├── cleaned_video_details.csv      # Video metadata
├── merged_output.csv             # Combined dataset
├── requirements.txt              # Required Python libraries
└── README.md                     # Project documentation
```



## 🧠 How It Works  
1. **Data Collection** – Fetch video metadata (title, ID, publish date) using **YouTube Data API v3**.  
2. **Transcript Extraction & Cleaning** – Extract captions using `youtube-transcript-api`, remove unwanted text, and preprocess.  
3. **Embedding Generation** – Convert cleaned text into embeddings using transformer models (Sentence-BERT/MiniLM).  
4. **Semantic Search** – Compute cosine similarity between user query and video embeddings.  
5. **Ranking & Output** – Return **top-5 most relevant video titles and IDs**.

---

## 🛠️ Installation & Setup  

```bash
1️⃣ Clone the Repository  
git clone -b Dhruvin https://github.com/AabidMK/QueryTube_Infosys_Internship_Sep25.git
cd QueryTube_Infosys_Internship_Sep25

2️⃣ Create a Virtual Environment
python -m venv venv
source venv/bin/activate        # On Windows: venv\Scripts\activate

3️⃣ Install Dependencies
pip install -r requirements.txt
```
---

## 🔑 API Key Setup

You’ll need a YouTube Data API v3 Key.

Go to Google Cloud Console.

Enable YouTube Data API v3.

Create an API key and store it securely (e.g., .env or config.json).

Example config.json:
```json
{
  "YOUTUBE_API_KEY": "your_api_key_here"
}
```
---

## 💻 Usage

# Run the app
```bash
python app.py
```
Then open your browser at 👉 http://127.0.0.1:5000/
Type your natural-language query (e.g., “how to build a neural network”) and get the top-5 semantically relevant YouTube videos.

---

## 📆 Milestone Plan

| Milestone | Description | Duration |
|-----------|-------------|----------|
| 1️⃣ YouTube Data Collection | Learn & use YouTube Data API for fetching video info | Weeks 1–2 |
| 2️⃣ Transcript Extraction | Extract and clean transcripts | Weeks 3–4 |
| 3️⃣ Transformer Evaluation | Test & compare Sentence Transformer models | Weeks 5–6 |
| 4️⃣ Semantic Search Implementation | Build & tune full search engine | Weeks 7–8 |
---

## 🧩 Dependencies
Python 3.8+

youtube-transcript-api, Fastapi

sentence-transformers

pandas, numpy

scikit-learn

chromadb or faiss

Flask or Streamlit

Install them via:
```bash
pip install youtube-transcript-api sentence-transformers pandas numpy scikit-learn flask
```
---

## 🚀 Future Enhancements

🎨 Add modern web UI using React/Streamlit

🧠 Fine-tune embeddings for domain-specific search

⚙️ Integrate FAISS/ChromaDB for faster retrieval

☁️ Deploy to cloud (Render, GCP, AWS, etc.)

---
## 👨‍💻 Contributors

| Name | Role |
|------|------|
| Dhruvin Chudasama | Lead Developer, Semantic Search & NLP |
| Aabid MK | Repository Maintainer & Code Review |
---
## 📜 License
This project is licensed under the MIT License – see the [LICENSE](LICENSE) file for details.

💡 QueryTube combines AI, NLP, and information retrieval to make video search truly intelligent.

⭐ If you found this project interesting, don’t forget to star the repo!