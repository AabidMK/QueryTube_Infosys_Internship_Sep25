# QueryTube: YouTube Data Collection, Analysis & Semantic Search Platform

This repository provides an end-to-end pipeline for collecting, analyzing, cleaning, and searching YouTube video data and transcripts. It leverages Python, ChromaDB vector store, embedding models, and exposes a semantic search API with both Flask and FastAPI APIs, plus a simple frontend.

---

## Table of Contents

1. [Project Structure](#project-structure)
2. [Sequential Pipeline Overview](#sequential-pipeline-overview)
3. [Detailed File & Folder Guide](#detailed-file--folder-guide)
4. [How to Run the Full Pipeline](#how-to-run-the-full-pipeline)
5. [Tips, Best Practices, and Troubleshooting](#tips-best-practices-and-troubleshooting)

---

## Project Structure

<details>
<summary><b>💡 Click to expand full folder tree & descriptions</b></summary>

```
📦 QueryTube_Infosys_Internship_Sep25/
├── 🐍 Python modules/         # Main Python scripts (collect, clean, backend)
│   ├── Yt_video_data_collection_task_1.py
│   ├── transcripts.py
│   ├── EDA and Data_Quality_check_task_1.py
│   ├── EDA_and_Data_Quality_Check_Task_2_Dataset.py
│   ├── Search_Query_main.py
│   ├── ai_app.py
│   ├── api.py
│   └── ...
├── 📊 data/                  # Input/output datasets (raw, processed, embeddings)
│   ├── raw/              # Initial master datasets
│   ├── processed/        # Cleaned and filtered files
│   ├── Embeddings/       # Embedding files (CSV, parquet)
│   └── ...
├── 📊 EDA_and_DataQuality_Results/  # Automated EDA graphs & reports
│   ├── dqc_missing_values.png
│   ├── eda_correlation_matrix.png
│   ├── ...
├── 🗃️ chroma_db/             # ChromaDB vector database (for similarity search)
├── 🌐 frontend/               # HTML Search UI
│   └── index1.html
├── 📓 Notebooks/             # Jupyter notebooks for prototyping
├── 📄 channel_metadata_retrievalcode.py # Standalone metadata fetcher
└── 📚 README.md
```
</details>

---
## Sequential Pipeline Overview

### 1. YouTube Video Metadata Collection
- **Script**: `Python modules/Yt_video_data_collection_task_1.py`
  - Uses the YouTube Data API to crawl up to 50–70 long-form (not Shorts) videos from a selected channel, filters out short videos, collects channel info, and saves a merged CSV.
  - API key is loaded from `.env`.
- **Key Outputs**: `YT_DataCollection_Task_1.csv`

### 2. Transcript Extraction
- **Script**: `Python modules/transcripts.py`
  - Extracts video transcripts (using proxies, retries, resuming) for each video in the CSV above.
- **Key Outputs**: `Output/all_transcripts.csv`

### 3. Data Cleaning & Processing
- **Scripts**:
  - Video metadata: `EDA and Data_Quality_check_task_1.py`
  - Transcripts: `EDA_and_Data_Quality_Check_Task_2_Dataset.py`
- Cleans, validates, adds key NLP/statistics columns, and saves new cleaned outputs and summary stats.

### 4. EDA & Data Quality Reporting
- **Outputs**: automatic reports and plots—see samples below:

> **Sample EDA Result Plots:**
>
> ![Missing values heatmap/dist](EDA_and_DataQuality_Results/dqc_missing_values.png)
> *Missing values report*
>
> ![Correlation matrix](EDA_and_DataQuality_Results/eda_correlation_matrix.png)
> *Feature correlation matrix*
>
> ![Distribution (numerical)](EDA_and_DataQuality_Results/eda_numerical_distributions.png)
> *Numerical feature distributions*
>
> (More plots in EDA_and_DataQuality_Results/...)

### 5. Embeddings & Vector DB (ChromaDB)
- Generate embeddings (e.g. using Sentence Transformers) and store into ChromaDB for similarity search.

### 6. Semantic Search API & UI
- Flask (`ai_app.py`) and FastAPI (`api.py`) backends; both call `Search_Query_main.py` for ChromaDB search.
- Frontend at [`frontend/index1.html`](frontend/index1.html) for searching videos semantically by text.

---

## Detailed File & Folder Guide

➤ See <details> above, or browse this repo with your IDE for inline comments in the scripts.

---
## How to Run the Full Pipeline

### **PRE-REQUISITES**
1. **Python 3.8+** recommended; install all dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Create a `.env` file in the root folder (same directory as README.md):
   ```
   YOUTUBE_API_KEY=your_youtube_data_api_key_here
   ```

---
### **STEP 1: Collect YouTube Video Metadata**
```bash
cd "Python modules"
python Yt_video_data_collection_task_1.py
```
- Output: `YT_DataCollection_Task_1.csv`

---
### **STEP 2: Extract Video Transcripts**
```bash
python transcripts.py
```
- Output: `Output/all_transcripts.csv`

---
### **STEP 3: Clean the Datasets & Run EDA**
Video dataset:
```bash
python "EDA and Data_Quality_check_task_1.py"
```
Transcript dataset:
```bash
python EDA_and_Data_Quality_Check_Task_2_Dataset.py
```
Outputs: PNG plots and `.txt` reports in `EDA_and_DataQuality_Results/`

---
### **STEP 4: (Optional) Generate Embeddings & Populate Vector DB**
You may use your notebook/scripts to:
- Compute transcript/video embeddings (e.g., using SentenceTransformer)
- Store them (with video/channel metadata) into ChromaDB (`chroma_db/`)

---
### **STEP 5: Launch the Search API & Web App**
Default: Flask
```bash
python ai_app.py
```
- UI: [http://localhost:8000](http://localhost:8000)
- API: `/search` endpoint (see example request in code)

Alternative: FastAPI
```bash
uvicorn api:app --reload
```
- Docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---
## Tips, Best Practices, and Troubleshooting

- **Store API keys only in `.env`, never in code or repo**.
- Check CSV/parquet in Excel, pandas, or a text editor.
- If transcript extraction breaks (e.g., proxies fail): rerun `transcripts.py`, it resumes progress.
- **Chroma model versions must match**: the embedding model in retrieval and search must be the same.
- **Back up `chroma_db/` and dataset outputs** before software or codebase changes.
- The notebooks are great references for manual inspection and advanced pipeline dev.

---
