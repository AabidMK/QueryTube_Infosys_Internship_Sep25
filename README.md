# QueryTube: YouTube Data Collection, Analysis and Semantic Search Platform

QueryTube is an end-to-end YouTube data intelligence system that automates the process of collecting, analyzing, cleaning, and searching YouTube video data and transcripts.  
It uses Python, ChromaDB, and embedding models, and includes Flask and FastAPI APIs along with a simple frontend for semantic video search.

---

## Table of Contents

- Project Overview  
- Project Structure  
- Pipeline Overview  
- Tech Stack   
- Future Enhancements  

---

## Project Overview

QueryTube provides a complete workflow for handling YouTube data. It starts with fetching metadata from the YouTube Data API, extracting video transcripts, cleaning and analyzing the collected data, generating embeddings, and finally providing a semantic search interface through APIs and a basic web frontend.

---

## Project Structure

The repository is organized into several modules and folders for different stages of the workflow:

- modules: Contains all Python scripts for data collection, cleaning, embedding generation, and semantic search.
- Output: Stores all generated CSV files, cleaned datasets, and analysis results.
- frontend: Contains a simple HTML-based interface for performing semantic searches.
- api.py and ai_app.py: Provide FastAPI and Flask backends respectively.
- requirements.txt: Lists Python dependencies.
- .env: Stores API keys and configuration variables.

---

## Pipeline Overview

1. **YouTube Video Metadata Collection**  
   The script uses the YouTube Data API to collect metadata for a set of long-form videos from a chosen channel.  
   It filters out Shorts and live streams, merges channel information, and stores the results in a CSV file.

2. **Transcript Extraction**  
   Extracts transcripts for the collected videos using reliable fetching methods with retries and resume support.  
   The output is stored as a structured dataset containing text content for each video.

3. **Data Cleaning and Processing**  
   Separate scripts handle metadata and transcript cleaning.  
   They remove duplicates, check for missing values, and generate new statistical or NLP-based features like word count and sentiment.

4. **Exploratory Data Analysis and Reporting**  
   Generates data quality and exploratory analysis reports with visual summaries such as correlation matrices and feature distributions.  
   The reports help identify data gaps and validate preprocessing results.

5. **Embeddings and Vector Database**  
   Converts video transcripts into embeddings using models such as Sentence Transformers.  
   These embeddings are stored in ChromaDB to enable efficient semantic similarity search.

6. **Semantic Search API and UI**  
   Two backend options (Flask and FastAPI) expose endpoints for semantic search.  
   The frontend allows users to enter natural language queries and retrieves related videos based on transcript similarity.

---

## Tech Stack

- Python  
- Flask and FastAPI  
- YouTube Data API  
- ChromaDB (Vector Database)  
- Sentence Transformers for embeddings  
- HTML, CSS, and JavaScript for frontend  
- Matplotlib, Seaborn, and Plotly for visualization  

---

## Future Enhancements

- Add support for multilingual transcripts.  
- Integrate large language models for intelligent summarization.  
- Improve the frontend using React with advanced filters and search analytics.  
- Add Docker support for deployment and scalability.  

---

