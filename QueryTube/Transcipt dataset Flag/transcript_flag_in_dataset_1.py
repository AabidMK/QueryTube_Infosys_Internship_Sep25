import pandas as pd
import os

# --- Configuration for Data Preparation ---

# Base directory where your files are located
BASE_DIR = r"C:\Users\dream\Desktop\Internships\Infosys Springboard\QueryTube" 

# File paths for the two datasets (Input)
MAIN_DATASET_FILENAME = r'C:\Users\dream\Desktop\Internships\Infosys Springboard\QueryTube\Dataset Cleaning\Task_1_cleaned_dataset_.csv'
TRANSCRIPT_DATASET_FILENAME = r'C:\Users\dream\Desktop\Internships\Infosys Springboard\QueryTube\Dataset Cleaning\task2_cleaned_transcripts.csv'

MAIN_DATASET_PATH = os.path.join(BASE_DIR, MAIN_DATASET_FILENAME)
TRANSCRIPT_DATASET_PATH = os.path.join(BASE_DIR, TRANSCRIPT_DATASET_FILENAME)

# NEW OUTPUT PATH
OUTPUT_DIR = r"C:\Users\dream\Desktop\Internships\Infosys Springboard\QueryTube\Transcipt dataset Flag"
OUTPUT_FILENAME = "Task_1_Flagged_dataset.csv"
OUTPUT_FULL_PATH = os.path.join(OUTPUT_DIR, OUTPUT_FILENAME)

def add_transcript_flag():
    """
    Loads the main dataset and the transcript dataset, adds a boolean 
    flag indicating if a transcript is available for each video ID, 
    and saves the result to the specified OUTPUT_DIR.
    """
    print("--- Starting Transcript Availability Flagging ---")
    
    # --- 0. Ensure Output Directory Exists ---
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"Ensuring output directory exists: {OUTPUT_DIR}")

    # --- 1. Load Data ---
    try:
        # Load the main dataset (Task 1)
        main_df = pd.read_csv(MAIN_DATASET_PATH)
        print(f"Loaded main dataset from: {MAIN_DATASET_PATH} (Shape: {main_df.shape})")
    except FileNotFoundError:
        print(f"ERROR: Main dataset not found at {MAIN_DATASET_PATH}. Please check the path and filename.")
        return

    try:
        # Load the transcript dataset (Task 2)
        transcript_df = pd.read_csv(TRANSCRIPT_DATASET_PATH)
        print(f"Loaded transcript dataset from: {TRANSCRIPT_DATASET_PATH} (Shape: {transcript_df.shape})")
    except FileNotFoundError:
        print(f"ERROR: Transcript dataset not found at {TRANSCRIPT_DATASET_PATH}. Please check the path and filename.")
        return
        
    # --- 2. Data Cleaning and ID Extraction ---

    # Ensure 'id' column in main_df is string type
    if 'id' not in main_df.columns:
        print("ERROR: 'id' column not found in the main dataset. Aborting flag process.")
        return

    main_df['id'] = main_df['id'].astype(str).str.strip()

    # Determine the ID column in the transcript dataset and extract unique IDs
    if 'id' in transcript_df.columns:
        id_column = 'id'
    elif 'video_id' in transcript_df.columns:
        id_column = 'video_id'
    else:
        print("ERROR: Neither 'id' nor 'video_id' found in the transcript dataset. Aborting flag process.")
        return

    # Extract unique IDs that actually have a transcript (filtering out errors)
    if 'transcript' in transcript_df.columns:
        transcript_df['transcript'] = transcript_df['transcript'].astype(str).str.strip()
        
        ERROR_PREFIX = "Error:" 
        raw_transcript_ids_count = transcript_df.shape[0]

        clean_transcript_df = transcript_df[
            (transcript_df['transcript'] != 'nan') & 
            (transcript_df['transcript'].str.len() > 10) &
            (~transcript_df['transcript'].str.startswith(ERROR_PREFIX))
        ]
        
        transcript_ids = set(clean_transcript_df[id_column].astype(str).str.strip())
        
        print(f"Initial transcript records: {raw_transcript_ids_count}")
        print(f"Cleaned unique transcript IDs available: {len(transcript_ids)}")
    else:
        print("Warning: 'transcript' column not found. Relying solely on the presence of the ID for availability.")
        transcript_ids = set(transcript_df[id_column].astype(str).str.strip())


    # --- 3. Flagging and Saving ---

    # Add the transcript_available column (True if ID is in the set of available IDs)
    main_df['transcript_available'] = main_df['id'].isin(transcript_ids)

    # Save the result to the new specified path
    main_df.to_csv(OUTPUT_FULL_PATH, index=False)

    videos_with_transcript = main_df['transcript_available'].sum()
    
    print(f"\n✅ 'transcript_available' column added successfully!")
    print(f"Total videos with transcript available: {videos_with_transcript} out of {len(main_df)}")
    print(f"Flagged dataset saved to: {OUTPUT_FULL_PATH}")
    print("----------------------------------------------------\n")

if __name__ == "__main__":
    add_transcript_flag()
