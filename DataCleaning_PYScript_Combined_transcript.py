import pandas as pd
import re

# Function to clean transcript text
def clean_transcript(text):
    if pd.isna(text) or str(text).strip() == "":
        return "missing transcript"
    
    # Convert to string
    text = str(text)
    
    # Remove [Music], [Applause], [Laughter], etc.
    text = re.sub(r'\[.*?\]', '', text)
    
    # Remove timestamps (formats like 00:01 or 1:23:45)
    text = re.sub(r'\b\d{1,2}:\d{2}(?::\d{2})?\b', '', text)
    
    # Remove special characters / non-UTF symbols (keep alphanumeric and spaces)
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    
    # Replace newlines with spaces
    text = text.replace("\n", " ")
    
    # Convert to lowercase
    text = text.lower()
    
    # Remove extra spaces
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def clean_transcript_csv(input_file, output_file):
    # Load CSV
    df = pd.read_csv(input_file)
    
    # Ensure 'transcript' column exists
    if 'transcript' not in df.columns:
        raise ValueError("Input CSV must have a 'transcript' column")
    
    # Apply cleaning
    df['clean_transcript'] = df['transcript'].apply(clean_transcript)
    
    # Save cleaned dataset
    df.to_csv(output_file, index=False, encoding="utf-8")
    print(f"✅ Cleaned transcript saved at: {output_file}")

# Example usage
if __name__ == "__main__":
    input_file = r"C:\Users\balak\OneDrive\Desktop\Combined_dataset\master_task2_datset.csv"         # Your uncleaned input file
    output_file = "cleaned_youtube_transcripts.csv"
    clean_transcript_csv(input_file, output_file)
