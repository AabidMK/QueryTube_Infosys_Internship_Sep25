import pandas as pd

# Load your two CSV files into pandas DataFrames
try:
    metadata_df = pd.read_csv('Metadata_cleaned.csv')
    transcript_df = pd.read_csv('cleaned_transcript.csv')
except FileNotFoundError as e:
    print(f"Error: {e}. Please make sure both CSV files are in the same directory as the script.")
    exit()

# Use the correct column name 'id'
transcript_video_ids = set(transcript_df['id'])

# Create the new column using the correct column name 'id'
metadata_df['has_transcript'] = metadata_df['id'].isin(transcript_video_ids)

# --- CHANGE IS HERE ---
# Save the updated DataFrame, preserving NaN values as the string 'NaN'
metadata_df.to_csv(
    'metadata_with_transcript_flag1.csv', 
    index=False, 
    na_rep='NaN'  # This tells pandas to write 'NaN' for missing values
)

print("Successfully created 'metadata_with_transcript_flag.csv'.")
print("Missing values in the 'tag' column are now saved as 'NaN'.")