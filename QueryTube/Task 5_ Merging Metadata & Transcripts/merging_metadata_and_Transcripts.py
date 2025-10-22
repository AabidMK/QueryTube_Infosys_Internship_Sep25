import pandas as pd
import os

BASE_DIR = r"C:\Users\dream\Desktop\Internships\Infosys Springboard\QueryTube" 


MAIN_DATASET_FILENAME = 'Task_1_Flagged_dataset.csv'
MAIN_DATASET_PATH = r"C:\Users\dream\Desktop\Internships\Infosys Springboard\QueryTube\Transcipt dataset Flag\Task_1_Flagged_dataset.csv"

TRANSCRIPT_DATASET_FILENAME = 'task2_cleaned_transcripts.csv'
TRANSCRIPT_DATASET_PATH = r"C:\Users\dream\Desktop\Internships\Infosys Springboard\QueryTube\Dataset Cleaning\task2_cleaned_transcripts.csv"
OUTPUT_DIR = r"C:\Users\dream\Desktop\Internships\Infosys Springboard\QueryTube\Task 5_ Merging Metadata & Transcripts"
OUTPUT_FILENAME = "Final_Merged_Dataset.csv"
OUTPUT_FULL_PATH = os.path.join(OUTPUT_DIR, OUTPUT_FILENAME)

def merge_datasets():
    """
    Loads the flagged metadata and cleaned transcripts, performs a Left Merge 
    on the video ID, and saves the final comprehensive dataset.
    """
    print("--- Starting Data Processing: Merging Metadata & Transcripts ---")
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"Ensuring output directory exists: {OUTPUT_DIR}")

    try:
        main_df = pd.read_csv(MAIN_DATASET_PATH)
        print(f"Loaded Metadata (Flagged) from: {MAIN_DATASET_PATH} (Shape: {main_df.shape})")
    except FileNotFoundError:
        print(f"ERROR: Flagged Metadata dataset not found at {MAIN_DATASET_PATH}. Please check the path.")
        return

    try:
        # Load the Cleaned Transcripts Dataset
        transcript_df = pd.read_csv(TRANSCRIPT_DATASET_PATH)
        print(f"Loaded Transcripts from: {TRANSCRIPT_DATASET_PATH} (Shape: {transcript_df.shape})")
    except FileNotFoundError:
        print(f"ERROR: Transcripts dataset not found at {TRANSCRIPT_DATASET_PATH}. Please check the path.")
        return
        
    # --- 2. Prepare for Merge ---
    
    # Define the common merge key and ensure consistency (string type and stripped)
    main_df['id'] = main_df['id'].astype(str).str.strip()
    
    # Determine the ID column in the transcript dataset
    if 'id' in transcript_df.columns:
        merge_key_transcript = 'id'
    elif 'video_id' in transcript_df.columns:
        merge_key_transcript = 'video_id'
    else:
        print("ERROR: Transcript dataset must contain 'id' or 'video_id' for merging. Aborting merge.")
        return
    
    transcript_df[merge_key_transcript] = transcript_df[merge_key_transcript].astype(str).str.strip()


    # --- 3. Perform Left Merge ---
    # We use a left merge to keep ALL rows from the main (metadata) dataframe, 
    # adding the 'transcript' column where a match is found.
    print(f"Performing Left Merge on 'id' (Metadata) and '{merge_key_transcript}' (Transcripts)...")
    
    # Select only the ID and the transcript columns from the transcript file
    transcript_cols = [merge_key_transcript, 'transcript']
    transcript_subset = transcript_df[transcript_cols].copy()
    
    # Merge the dataframes
    final_df = pd.merge(
        main_df, 
        transcript_subset, 
        left_on='id', 
        right_on=merge_key_transcript, 
        how='left'
    )
    
    # Drop the redundant video ID column from the transcript file if it's different from 'id'
    if merge_key_transcript != 'id' and merge_key_transcript in final_df.columns:
        final_df = final_df.drop(columns=[merge_key_transcript])

    print(f"Merge successful. Final merged dataset shape: {final_df.shape}")

    # --- 4. Saving the Final Dataset ---

    # Save the result to the new specified path
    final_df.to_csv(OUTPUT_FULL_PATH, index=False)

    print(f"\n✅ Data Merging Complete!")
    print(f"Final merged dataset saved to: {OUTPUT_FULL_PATH}")
    print("----------------------------------------------------\n")

if __name__ == "__main__":
    merge_datasets()
