# QueryTube: YouTube Video Analysis and Semantic Search Platform

## Project Overview
QueryTube is a comprehensive YouTube video analysis platform that combines video metadata collection, transcript analysis, and semantic search capabilities. The project enables users to gather insights from YouTube videos through advanced data processing and natural language understanding.

## Features

### 1. Data Collection and Processing
- YouTube video metadata collection
- Video transcript extraction and processing
- Dataset cleaning and preprocessing
- Merging metadata with transcripts

### 2. Analysis Capabilities
- Extensive Exploratory Data Analysis (EDA)
- Data quality checks and reporting
- Statistical analysis of video metrics
- Visualization of trends and patterns

### 3. Advanced Features
- Semantic embedding generation
- Vector database integration with ChromaDB
- RESTful API for semantic search
- Interactive data visualization dashboards

## Project Structure
```
├── requirements.txt              # Project dependencies
├── Dataset Cleaning/            # Data preprocessing scripts
├── EDA_and_Data_Quality_Check/  # Analysis and visualization
│   └── Results/                 # Generated reports and visualizations
├── Task 5_ Merging Metadata & Transcripts/
│   └── Embedding/              # Vector embeddings generation
│   └── Storing_in_ChromaDB/    # Vector database implementation
├── TASK_1/                     # Video data collection
├── Task_6_Semantic_Search/     # Search implementation
└── Task_7_Semantic_Search_API_Flask/ # REST API implementation
```

## Technologies Used
- Python 3.x
- Flask for API development
- ChromaDB for vector storage
- Hugging Face Transformers for embeddings
- Pandas for data processing
- Matplotlib and Seaborn for visualization
- Scikit-learn for data analysis
- sentence-transformers for semantic embeddings

## Setup and Installation

1. Clone the repository
```bash
git clone https://github.com/AabidMK/QueryTube_Infosys_Internship_Sep25.git
git checkout Md-Faizan
cd QueryTube_Infosys_Internship_Sep25
```

2. Create and activate a virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

## Usage

### 1. Data Collection
Run the YouTube data collector:
```bash
python TASK_1/Video\ Data\ Collections/youtube_data_collector.py
```

### 2. Transcript Collection
Execute the transcript collector:
```bash
python TASK_1/Videos_transcripts/YT_Transcript_collection.py
```

### 3. Data Processing and Analysis
Run the data cleaning scripts:
```bash
python Dataset\ Cleaning/Task_1_Dataset_Cleaning.py
python Dataset\ Cleaning/Task_2_Dataset_Cleaning.py
```

### 4. Running the Semantic Search API
Start the Flask API server:
```bash
python Task_7_Semantic_Search_API_Flask/app.py
```

## API Endpoints

### Search Endpoint
- **URL**: `/search`
- **Method**: POST
- **Body**:
```json
{
    "query": "your search query",
    "top_k": 5
}
```
- **Response**: Returns relevant videos based on semantic similarity

## Project Workflow

1. **Data Collection**: Gather YouTube video metadata and transcripts
2. **Data Processing**: Clean and preprocess the collected data
3. **Analysis**: Perform EDA and generate insights
4. **Embedding Generation**: Create vector embeddings for semantic search
5. **Database Storage**: Store embeddings in ChromaDB
6. **API Development**: Implement search functionality through REST API

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

## Contact
For any queries or suggestions, please open an issue in the repository.
