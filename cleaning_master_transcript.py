import pandas as pd
import re

# --- CONFIGURATION ---
INPUT_FILE_NAME = 'master_task2_datset.csv'
OUTPUT_FILE_NAME = 'cleaned_transcript_data.csv'

# Define the column names to be used in the script.
# This makes it easy to adapt the script if your CSV has different column headers.
ID_COLUMN = 'id'
TRANSCRIPT_COLUMN = 'transcript'

# --- PRE-COMPILED REGEX PATTERNS ---
# Compiling regex patterns once outside the main function improves performance,
# as it avoids re-compiling the pattern for every single row in the dataset.

# Matches standard 11-character YouTube video IDs (e.g., "dQw4w9WgXcQ")
VIDEO_ID_PATTERN = re.compile(r'^[a-zA-Z0-9_-]{11}$')
# Matches timestamps (e.g., 00:01, 1:23:45)
TIMESTAMP_PATTERN = re.compile(r'\d{1,2}:\d{2}(:\d{2})?')
# Matches event tags in brackets (e.g., [Music], [Applause])
BRACKET_PATTERN = re.compile(r'\[.*?\]')
# Matches characters that are NOT letters, numbers, or basic punctuation.
SPECIAL_CHAR_PATTERN = re.compile(r'[^a-z0-9\s.,:!?-]')


def clean_transcript(text):
    """
    Applies a series of cleaning steps to the raw transcript text.
    The steps are ordered for clarity and efficiency.

    1.  Handle missing data (though primary filtering is done before this function is called).
    2.  Ensure text is a string.
    3.  Replace newlines with spaces for consistency.
    4.  Remove event tags (e.g., [Music]) and timestamps.
    5.  Convert all text to lowercase.
    6.  Remove special characters, keeping only essential text and punctuation.
    7.  Standardize whitespace to single spaces.
    """
    # 1. Handle any potential missing data that slips through
    if pd.isna(text) or text is None:
        return ""

    # 2. Ensure text is a string
    text = str(text)

    # 3. Replace newlines with spaces
    text = text.replace('\n', ' ')

    # 4. Remove event tags and timestamps using pre-compiled patterns
    text = BRACKET_PATTERN.sub(' ', text)
    text = TIMESTAMP_PATTERN.sub(' ', text)

    # 5. Convert text to lowercase
    text = text.lower()

    # 6. Remove special characters
    text = SPECIAL_CHAR_PATTERN.sub(' ', text)

    # 7. Standardize whitespace (remove leading/trailing/multiple spaces)
    text = ' '.join(text.split()).strip()

    return text

# --- MAIN EXECUTION BLOCK ---
if __name__ == "__main__":
    try:
        # Load the dataset
        df = pd.read_csv(INPUT_FILE_NAME)
        original_rows = len(df)
        print(f"✅ Initial dataset loaded with {original_rows} rows.")

        # --- Step 1: Filter by Video ID format ---
        # We first remove rows that don't have a validly formatted Video ID.
        if ID_COLUMN in df.columns:
            df.dropna(subset=[ID_COLUMN], inplace=True)
            valid_video_ids_mask = df[ID_COLUMN].astype(str).str.match(VIDEO_ID_PATTERN)
            df = df[valid_video_ids_mask]
            rows_after_video_id_filter = len(df)
            print(f"➡️  Filtered by Video ID. Kept {rows_after_video_id_filter} rows with valid format.")
        else:
            print(f"⚠️  Warning: Video ID column '{ID_COLUMN}' not found. Skipping this filtering step.")

        # --- Step 2: Filter by Transcript availability ---
        # Now, remove rows where the transcript itself is missing.
        df.dropna(subset=[TRANSCRIPT_COLUMN], inplace=True)
        rows_after_na_filter = len(df)
        print(f"➡️  Removed rows with unavailable transcripts. {rows_after_na_filter} rows remain.")

        # --- Step 3: Clean the transcripts ---
        # Apply the detailed cleaning function only to the valid rows.
        df[TRANSCRIPT_COLUMN] = df[TRANSCRIPT_COLUMN].apply(clean_transcript)
        print("➡️  Transcript text has been cleaned.")

        # --- Step 4: Final filter for empty transcripts ---
        # Remove rows where the transcript became an empty string after cleaning
        # (e.g., it only contained timestamps and tags).
        df = df[df[TRANSCRIPT_COLUMN] != ""].copy()

        # --- Final Summary ---
        final_rows = len(df)
        total_rows_removed = original_rows - final_rows
        print(f"\n✅ Processing complete. Removed {total_rows_removed} rows in total.")

        # Save the final cleaned and filtered dataset
        df.to_csv(OUTPUT_FILE_NAME, index=False)
        print(f"🎉 Final data saved to '{OUTPUT_FILE_NAME}' with {final_rows} rows.")

    except FileNotFoundError:
        print(f"❌ Error: The file '{INPUT_FILE_NAME}' was not found. Please check the file name and path.")
    except KeyError as e:
        print(f"❌ Error: A required column was not found in the CSV: {e}.")

