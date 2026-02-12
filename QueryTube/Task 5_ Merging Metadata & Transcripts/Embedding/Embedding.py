import pandas as pd
import os
import time
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

# Set to suppress pandas warnings when creating copies
pd.options.mode.chained_assignment = None  

# --- Configuration ---
# 1. Input File Path (The merged dataset from the previous step)
INPUT_PATH = r"C:\Users\dream\Desktop\Internships\Infosys Springboard\QueryTube\Task 5_ Merging Metadata & Transcripts\Final_Merged_Dataset.csv"

# 2. Output Path for the EMBEDDED dataset
OUTPUT_DIR = r"C:\Users\dream\Desktop\Internships\Infosys Springboard\QueryTube\Task 5_ Merging Metadata & Transcripts\Embedding"
EMBEDDED_CSV_FILENAME = "Embedded_Merged_Dataset.csv"
EMBEDDED_PARQUET_FILENAME = "Embedded_Merged_Dataset.parquet"
EMBEDDED_CSV_FULL_PATH = os.path.join(OUTPUT_DIR, EMBEDDED_CSV_FILENAME)
EMBEDDED_PARQUET_FULL_PATH = os.path.join(OUTPUT_DIR, EMBEDDED_PARQUET_FILENAME)

# 3. Model Configuration
# We use a highly efficient model for demonstration
EMBEDDING_MODEL_NAME = 'all-MiniLM-L6-v2' 

def process_data_for_embeddings(df):
    """
    Cleans the merged dataframe and creates the combined text field ('text_for_embedding') 
    which the model will use to generate the vector.
    """
    print("-> Data Cleaning and Text Combination...")
    
    # 1. Fill missing transcripts with empty string (crucial for clean concatenation)
    df['transcript'] = df['transcript'].fillna('')
    
    # 2. Filter out videos without a transcript, as we only want to embed full content
    df_clean = df[df['transcript_available'] == True].copy()
    
    if df_clean.empty:
        print("   WARNING: No rows found with 'transcript_available=True'. Embedding process halted.")
        return None

    # 3. Create the combined text source: Title + Description + Transcript
    # This is the primary input for the semantic embedding model.
    df_clean['text_for_embedding'] = df_clean['title'].fillna('') + ' ' + df_clean['description'].fillna('') + ' ' + df_clean['transcript']
    
    # 4. Add 'is_short' column: True if video duration < 120 seconds (2 minutes), False otherwise
    df_clean['is_short'] = df_clean['duration'].apply(
        lambda x: True if (x > 0 and x < 120) else False
    )
    
    # Keep only the columns needed for embedding and ID
    df_clean = df_clean[['id', 'title', 'description', 'transcript', 'text_for_embedding', 'publishedAt', 'channel_title', 'channel_id', 'viewCount', 'likeCount', 'commentCount', 'duration', 'is_short']]
    
    print(f"-> Cleaned dataset size for embedding: {len(df_clean)} rows.")
    return df_clean

def generate_embeddings(df):
    """
    Loads the SentenceTransformer model, generates embeddings for the 'text_for_embedding'
    column, and saves the resulting DataFrame to both a new CSV and Parquet file.
    """
    print(f"\n--- 2. GENERATING EMBEDDINGS (Model: {EMBEDDING_MODEL_NAME}) ---")
    start_time = time.time()
    
    # Load the pre-trained model
    try:
        model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    except Exception as e:
        print(f"ERROR: Could not load the embedding model. Check your internet connection or model name. {e}")
        return None

    # Get the list of texts to embed
    texts_to_embed = df['text_for_embedding'].tolist()
    
    print(f"-> Generating {len(texts_to_embed)} embeddings...")

    # Generate embeddings with a progress bar using tqdm
    embeddings = model.encode(texts_to_embed, show_progress_bar=True)
    
    # Store embeddings in a new column as a list (saved as a string in CSV/Parquet)
    df['embedding_vector'] = [vec.tolist() for vec in embeddings]
    
    end_time = time.time()
    print(f"-> Embedding generation complete in {end_time - start_time:.2f} seconds.")
    
    # Save the dataframe with vectors
    os.makedirs(OUTPUT_DIR, exist_ok=True) # Ensure output directory exists

    # 1. Save to CSV
    df.to_csv(EMBEDDED_CSV_FULL_PATH, index=False)
    print(f"-> Embedded dataset saved successfully to CSV: {EMBEDDED_CSV_FULL_PATH}")
    
    # 2. Save to Parquet (Requires 'pyarrow')
    try:
        df.to_parquet(EMBEDDED_PARQUET_FULL_PATH, index=False)
        print(f"-> Embedded dataset saved successfully to Parquet: {EMBEDDED_PARQUET_FULL_PATH}")
    except ImportError:
        print("\n*** WARNING: Parquet save failed. Please run 'pip install pyarrow' to enable Parquet output. ***")
    
    return embeddings # Returns vectors for the next ChromaDB step

def main():
    """
    Main function to run the embedding generation process.
    """
    print("\n--- Starting Embedding Generation Pipeline ---")
    
    # --- 1. LOAD DATA ---
    try:
        data = pd.read_csv(INPUT_PATH)
        print(f"Loaded merged data from: {INPUT_PATH}")
    except FileNotFoundError:
        print(f"FATAL ERROR: Input file not found at {INPUT_PATH}. Please verify the path: {INPUT_PATH}")
        return
    except Exception as e:
        print(f"FATAL ERROR: Could not load data: {e}")
        return

    # --- 2. PROCESS DATA ---
    processed_df = process_data_for_embeddings(data)
    if processed_df is None:
        return

    # --- 3. GENERATE AND SAVE EMBEDDINGS ---
    generate_embeddings(processed_df)
    
    print("\nEmbedding Generation and Saving Complete.")

if __name__ == "__main__":
    main()
