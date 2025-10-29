# QueryTube: AI Semantic Search Tube
**Infosys Springboard Virtual Internship Project (September 2025)**  
Team Member: M. Sai Madhuri  

---

## Project Overview
QueryTube is an AI-powered semantic search system that allows users to find YouTube videos based on **meaning** rather than just matching keywords.  
It uses **Machine Learning** and **Natural Language Processing (NLP)** techniques to understand the intent behind the user’s query and fetch the most semantically relevant YouTube videos.

This project was developed as part of the **Infosys Springboard Virtual Internship** under the AI domain.

---

## Objective
The main objective of this project is to:
- Create a **semantic video search engine** using YouTube data.
- Implement **transformer-based embeddings** for meaning-based similarity.
- Display the **top 5 most relevant videos** for a given user query.
- Build an **interactive frontend** for users to test the system.

---

## Project Workflow

### **Module 1: Data Extraction**
- Used **YouTube Data API v3** to fetch video metadata like:
  - Video ID, Title, Description, Published Date, Tags, View Count, Like Count, Comment Count.
- Collected data from an educational YouTube channel (Traversy Media / Computerphile).

### **Module 2: Transcript Extraction**
- Used **YouTube Transcript API** to retrieve transcripts (captions) for videos.
- Stored transcripts with their respective video IDs.

### **Module 3: Data Cleaning & Merging**
- Cleaned the metadata and transcript datasets.
- Removed missing values, duplicates, and videos without transcripts.
- Merged both datasets into one master CSV file.

### **Module 4: Embedding Generation**
- Used **Sentence Transformer (all-MiniLM-L6-v2)** model to create semantic embeddings for both:
  - Video titles  
  - Video transcripts  
- These embeddings represent the meaning of text in vector form.

### **Module 5: Semantic Search and Vector Database**
- Stored embeddings and metadata in **ChromaDB**, a vector database.
- Implemented **cosine similarity** to find how close a user query is to each video.
- Retrieved and displayed the **Top-5 most relevant videos** based on similarity score.

### **Module 6: Frontend and Backend Integration**
- Built a **Gradio-based web interface** for user interaction.
- Backend implemented using **FastAPI** to handle:
  - Query processing  
  - Embedding generation  
  - Database retrieval  
- The interface displays:
  - Video Title  
  - Similarity Score  
  - Watch Button (link to YouTube video)

### **Module 7: Final Output**
- The final output is an **interactive web app** where:
  - Users can type a natural language query (e.g., *"How does machine learning work?"*)
  - The system instantly displays the top-5 YouTube videos semantically related to the query.
  - Each result shows a **title**, **similarity score**, and **watch button** linking to the actual video.

---

## 📊 Results and Performance
- Successfully fetched and processed hundreds of YouTube videos.
- Generated meaningful embeddings and stored them efficiently in ChromaDB.
- Achieved accurate semantic retrieval using cosine similarity.
- The system gives results within seconds of the user’s input.

---

## Tools and Technologies Used
| Category | Tools / Libraries |
|-----------|------------------|
| **Programming Language** | Python |
| **APIs Used** | YouTube Data API, YouTube Transcript API |
| **Libraries** | Pandas, NumPy, SentenceTransformers, Scikit-learn |
| **Database** | ChromaDB |
| **Frameworks** | FastAPI (Backend), Gradio (Frontend) |
| **Environment** | Google Colab, GitHub |

---

## Skills Gained
- API integration and data extraction from YouTube.
- Data cleaning, preprocessing, and EDA.
- NLP and embedding generation using Transformer models.
- Building and querying vector databases (ChromaDB).
- Full-stack project integration using FastAPI and Gradio.
- Documentation and version control using GitHub.

---

## Conclusion
Through this project, I learned the complete process of building an AI-powered semantic search system — from data collection to deployment.  
It gave me hands-on experience in working with real-world data, APIs, and AI models.  
This project helped improve both technical and teamwork skills while understanding how **semantic search** enhances user experience in content discovery.

---

## 📸 Example Output
<img width="512" height="441" alt="image" src="https://github.com/user-attachments/assets/eaf06233-768a-4e99-a691-638a9c6a8ea1" />

