import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import string

# =========================================================
# CONFIGURATION
# =========================================================

# File names of the uploaded datasets
META_FILE = 'youtube_dataset.csv'
TRANSCRIPT_FILE = 'video_id_and_transcript_only.csv'

# Error keywords used in the transcript fetching script
ERROR_KEYWORDS = [
    "Error:",
    "Transcript not available"
]

# =========================================================
# 1. LOAD, CLEAN, AND MERGE DATA
# =========================================================

print("--- 1. Loading and Merging Data ---")

# 1. Load DataFrames
try:
    df_meta = pd.read_csv(META_FILE)
    df_transcript_raw = pd.read_csv(TRANSCRIPT_FILE)
except FileNotFoundError as e:
    print(f"❌ ERROR: Could not find required file: {e}")
    # Raise exception to halt execution if files are missing
    raise

# 2. Standardize column names and prepare for merge
# The metadata file uses 'id', the transcript file uses 'Video ID'
df_meta.rename(columns={'id': 'Video ID'}, inplace=True)

# 3. Final Cleaning of Transcript Data
def is_valid_transcript(text):
    """Checks if the text is a valid, non-error transcript."""
    if not isinstance(text, str) or len(text) < 50:
        return False
    return not any(keyword in text for keyword in ERROR_KEYWORDS)

df_transcript_cleaned = df_transcript_raw[
    df_transcript_raw['Transcript'].apply(is_valid_transcript)
].copy()
print(f"Cleaned {len(df_transcript_raw) - len(df_transcript_cleaned)} transcript rows containing errors/missing data.")

# 4. Merge DataFrames
# Use 'inner' merge to keep only videos with both complete metadata and a clean transcript
df_combined = pd.merge(
    df_meta,
    df_transcript_cleaned,
    on='Video ID',
    how='inner'
)
df = df_combined # Use 'df' for simplicity

# 5. Type Conversion
STAT_COLS = ['viewCount', 'likeCount', 'commentCount']
for col in STAT_COLS:
    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

df['publishedAt'] = pd.to_datetime(df['publishedAt'], utc=True)
df['publish_date'] = df['publishedAt'].dt.date

print(f"✅ Data merged successfully. Final clean dataset size: {len(df)} rows.")

# =========================================================
# 2. DATA QUALITY CHECK
# =========================================================

print("\n--- 2. Data Quality Check ---")

# 1. Structure and Missing Values
print("\nDataFrame Info (Final):")
df.info()

# 2. Duplicate Check
num_duplicates = df.duplicated().sum()
if num_duplicates > 0:
    df.drop_duplicates(inplace=True)
    print(f"⚠️ Dropped {num_duplicates} duplicate rows.")

# 3. Ensure key columns are clean (should be 0)
print("\nMissing Value Check on Key Columns:")
print(df[['title', 'Transcript', 'viewCount']].isnull().sum())

# =========================================================
# 3. BASIC EXPLORATORY DATA ANALYSIS (EDA)
# =========================================================

print("\n--- 3. Basic Exploratory Data Analysis (EDA) ---")

# 1. Feature Engineering (Text Length)
df['char_count'] = df['Transcript'].apply(len)
df['word_count'] = df['Transcript'].apply(lambda x: len(str(x).split()))

# 2. Descriptive Statistics
print("\nDescriptive Statistics (Length & Engagement):")
print(df[['word_count', 'viewCount', 'likeCount', 'commentCount']].describe().T)

# 3. Visualization: Word Count Distribution
plt.figure(figsize=(10, 5))
sns.histplot(df['word_count'], bins=10, kde=True, color='skyblue')
plt.title('Distribution of Transcript Word Count')
plt.xlabel('Word Count (Video Length Proxy)')
plt.ylabel('Number of Videos')
plt.axvline(df['word_count'].median(), color='red', linestyle='--', label=f'Median: {df["word_count"].median():.0f}')
plt.legend()
plt.show() #

# 4. Top Word Frequency Analysis
all_text = ' '.join(df['Transcript']).lower()
cleaned_words = [
    word.strip(string.punctuation)
    for word in all_text.split()
    if len(word.strip(string.punctuation)) > 2
]

word_counts = Counter(cleaned_words)
top_words_df = pd.DataFrame(word_counts.most_common(10), columns=['Word', 'Count'])

print("\nTop 10 Most Frequent Words (Raw Counts):")
print(top_words_df)

# 5. Relationship Analysis
plt.figure(figsize=(10, 5))
sns.scatterplot(x='word_count', y='viewCount', data=df, color='coral', alpha=0.7)
plt.title('Transcript Length vs. Views')
plt.xlabel('Word Count')
plt.ylabel('Views (Log Scale)')
plt.yscale('log')
plt.show() #

print(f"\n🎉 Analysis complete. Final clean dataset contains {len(df)} videos.")