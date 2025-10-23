import pandas as pd
import re

# --- CONFIGURATION ---
INPUT_FILE_NAME = "master_task1_datset_14.csv"
ID_COLUMN = 'id'
OUTPUT_FILE_NAME = 'data_transformed_final.csv'
DURATION_COLUMN = 'duration'
TAGS_COLUMN = 'tags'

# --- FUNCTIONS ---

def clean_text_aggressive(text):
    """Applies aggressive cleaning to text columns."""
    if pd.isna(text): return ""
    text = str(text)
    text = re.sub(r'https?://\S+|www\.\S+', ' ', text)
    text = re.sub(r'<.*?>', ' ', text)
    text = re.sub(r'[^A-Za-z0-9\s.,:!?-]', ' ', text)
    text = ' '.join(text.split()).strip()
    return text

def process_tags(tags):
    """
    Cleans and standardizes the tags column.
    Modified to fill missing values with the string 'nan'.
    """
    if pd.isna(tags):
        # 🎯 CHANGE: Fill missing tags with the string "nan"
        return "nan"

    # This code only runs if a tag value is present.
    tags_str = str(tags).replace('|', ' ')
    return clean_text_aggressive(tags_str)

def convert_duration_to_seconds(duration):
    """
    Converts any valid ISO 8601 duration string to total seconds.
    This version is highly robust and finds time components individually.
    """
    if pd.isna(duration) or not isinstance(duration, str):
        return 0

    parts = re.findall(r'(\d+)([DHMS])', duration.upper())
    if not parts:
        return 0

    total_seconds = 0
    time_multipliers = { 'D': 86400, 'H': 3600, 'M': 60, 'S': 1 }

    for value, unit in parts:
        total_seconds += int(value) * time_multipliers.get(unit, 0)

    return total_seconds

# --- MAIN EXECUTION ---
try:
    df = pd.read_csv(INPUT_FILE_NAME, encoding='latin-1')
    print(f"Successfully loaded '{INPUT_FILE_NAME}'.")

    # Clean text columns
    for col in ['title', 'description', 'channel_description']:
        if col in df.columns:
            df[col] = df[col].apply(clean_text_aggressive)

    # Process and clean the tags column
    if TAGS_COLUMN in df.columns:
        df[TAGS_COLUMN] = df[TAGS_COLUMN].apply(process_tags)
        print("Tags column successfully processed (missing values filled with 'nan').")

    # Drop duplicates
    df.drop_duplicates(subset=[ID_COLUMN], keep='first', inplace=True)

    # Convert to lowercase
    for col in df.select_dtypes(include='object').columns:
        if col not in [ID_COLUMN, 'channel_id']:
            df[col] = df[col].str.lower()

    # Convert numeric and date columns
    for col in ['viewCount', 'likeCount', 'commentCount', 'channel_subscriberCount', 'channel_videoCount']:
          if col in df.columns:
              df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype('Int64')

    if 'publishedAt' in df.columns:
        df['publishedAt'] = pd.to_datetime(df['publishedAt'], errors='coerce')

    # Convert the duration column
    if DURATION_COLUMN in df.columns:
        df[DURATION_COLUMN] = df[DURATION_COLUMN].apply(convert_duration_to_seconds).astype('Int64')
        print("Duration column successfully converted to seconds.")

    # Save the final file
    df.to_csv(OUTPUT_FILE_NAME, index=False)
    print(f"✅ Processing complete. Final file saved as '{OUTPUT_FILE_NAME}'.")

except FileNotFoundError:
    print(f"Error: Make sure '{INPUT_FILE_NAME}' is in the same folder as the script.")
except Exception as e:
    print(f"An error occurred: {e}")