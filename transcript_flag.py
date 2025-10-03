import pandas as pd

# File paths
transcript_file = "cleaned_transcript_details.csv"
video_file = "cleaned_video_details.csv"

# Load CSV files
df_transcript = pd.read_csv(transcript_file)
df_video = pd.read_csv(video_file)

# Normalize column names
df_transcript.columns = df_transcript.columns.str.lower().str.strip()
df_video.columns = df_video.columns.str.lower().str.strip()

# Extract transcript IDs (from `id` column)
transcript_ids = set(df_transcript['id'].unique())

# Add transcript_flag column to video details
df_video['transcript_flag'] = df_video['id'].apply(lambda x: True if x in transcript_ids else False)

# Save output
output_file = "video_with_transcript_flag.csv"
df_video.to_csv(output_file, index=False)

print(f"File saved as {output_file}")
