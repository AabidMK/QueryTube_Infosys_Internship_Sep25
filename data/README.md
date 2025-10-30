# data

This directory contains all datasets used and generated throughout the QueryTube pipeline.

- **raw/** 🟡  
  Contains original downloaded master YouTube video datasets in CSV format. These are the unmodifed, source files used as the basis for all downstream work.

- **processed/** 🟢  
  Cleaned and filtered datasets, such as post-EDA video and transcript CSVs, suitable for exploratory analysis and machine learning.

- **Embeddings/** 🧠  
  Files holding vector (embedding) representations of videos/transcripts—usually produced by Sentence Transformer models. These are used for semantic similarity search operations.

- **flagged dataset/** 🚩  
  Datasets with flagged or anomalous records, e.g., videos with failed transcript downloads, duplicate entries, or special error cases.

- **temporary and junks datasets/** 🗑️  
  Temporary/utility files and intermediate datasets generated during cleaning, debugging, or experimental preprocessing. Not meant for primary analysis.

- **video_details_and_transcripts_merged/** 🔗  
  Datasets where detailed video metadata and associated transcripts are merged into a single file. Used for most downstream AI or embedding tasks.

**File Types:**
- CSV and Parquet files are included for efficient interoperability and storage.

**Usage:**
- Raw and processed folders are read by the analysis scripts and notebooks.
- Embeddings and merged outputs are critical inputs for building the semantic vector database and powering search features.
