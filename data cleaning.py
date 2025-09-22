import pandas as pd
import re
from collections import OrderedDict

def clean_text(text, max_words=200):
    """Clean transcript text: remove tags, deduplicate phrases/words, limit to max_words."""
    if not isinstance(text, str) or not text.strip():
        return None
    
    # Remove [Music], [Applause], etc.
    text = re.sub(r'\[.*?\]', '', text)
    
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Split into sentences to handle repetitions
    sentences = text.split('. ')
    # Remove duplicate sentences while preserving order
    seen = OrderedDict()
    for sentence in sentences:
        sentence = sentence.strip()
        if sentence and sentence not in seen:
            seen[sentence] = None
    cleaned_text = '. '.join(seen.keys())
    
    # Deduplicate consecutive words
    words = cleaned_text.split()
    cleaned_words = []
    prev_word = None
    for word in words:
        if word.lower() != prev_word:
            cleaned_words.append(word)
            prev_word = word.lower()
    
    # Truncate to max_words
    cleaned_words = cleaned_words[:max_words]
    cleaned_text = ' '.join(cleaned_words)
    
    # Ensure text ends with a period if it’s a complete sentence
    if cleaned_text and not cleaned_text.endswith('.'):
        cleaned_text += '.'
    
    return cleaned_text if cleaned_text.strip() else None

def clean_transcripts_csv(input_csv, output_csv):
    """Read CSV, clean transcripts, and save to a new CSV."""
    try:
        # Read CSV, skipping empty rows
        df = pd.read_csv(input_csv, encoding='utf-8')
        # Remove completely empty rows
        df = df.dropna(how='all')
        
        # Clean the 'full_transcript' column
        df['full_transcript'] = df['full_transcript'].apply(lambda x: clean_text(x) if pd.notna(x) else None)
        
        # Remove rows where transcript is None or empty after cleaning
        df = df[df['full_transcript'].notna() & (df['full_transcript'] != '')]
        
        # Save to new CSV
        df.to_csv(output_csv, index=False, encoding='utf-8')
        print(f"Cleaned data saved to {output_csv}. Total rows: {len(df)}")
        
    except Exception as e:
        print(f"Error processing CSV: {e}")

def main():
    """Main function to clean transcripts from the CSV."""
    input_csv = "Beast_Philanthropy_transcript.csv"
    output_csv = "Beast_Philanthropy_transcript_cleaned.csv"
    clean_transcripts_csv(input_csv, output_csv)

if __name__ == "__main__":
    main()
