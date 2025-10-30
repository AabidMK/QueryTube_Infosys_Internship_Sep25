import pandas as pd
import re

# Function to clean text
def clean_text(text):
    if pd.isna(text):
        return text
    # Remove emojis by keeping only ascii characters
    text = text.encode('ascii', 'ignore').decode('ascii')
    # Remove HTML tags
    text = re.sub(r'<.*?>', '', text)
    # Remove special characters (keep only letters, numbers, spaces)
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    # Convert to lowercase
    text = text.lower()
    # Strip extra whitespaces
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def clean_dataset(input_file, output_file):
    # Load dataset
    df = pd.read_csv(input_file)
    
    # Apply cleaning on title and description
    df['clean_title'] = df['title'].apply(clean_text)
    df['clean_description'] = df['description'].apply(clean_text)
    
    # Ensure title uniqueness across video_id
    df = df.drop_duplicates(subset=['id', 'clean_title'], keep='first')
    
    # Save cleaned dataset
    df.to_csv(output_file, index=False)
    print(f"✅ Cleaned dataset saved at: {output_file}")

# Example usage
if __name__ == "__main__":
    input_file = r"C:\Users\balak\OneDrive\Desktop\Combined_dataset\master_task1_datset.csv"          # Uncleaned input dataset
    output_file = "cleaned_video_data.csv" # Cleaned dataset
    clean_dataset(input_file, output_file)
