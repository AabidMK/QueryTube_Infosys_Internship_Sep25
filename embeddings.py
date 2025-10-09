import pandas as pd
from sentence_transformers import SentenceTransformer

# Load the dataset from the CSV file
df = pd.read_csv('video_with_transcript.csv')

# Load a pre-trained sentence transformer model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Fill any potential missing values in the 'merged_transcript' column to avoid errors
df['merged_transcript'].fillna('', inplace=True)

# Create embeddings for the 'merged_transcript' column
sentences = df['merged_transcript'].tolist()
embeddings = model.encode(sentences, show_progress_bar=True)

# Add the embeddings to a new column in the DataFrame.
# Each embedding will be stored as a list of numbers in a single cell.
df['embedding'] = embeddings.tolist()

# Save the DataFrame with the new 'embedding' column to a new CSV file
df.to_csv('video_with_embeddings.csv', index=False)
print("Successfully created 'video_with_embeddings.csv'")