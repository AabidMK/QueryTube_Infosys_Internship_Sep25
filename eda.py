import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.feature_extraction.text import CountVectorizer
from isodate import parse_duration # Used to convert video duration format

# Set plot style for better visualization
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)
pd.set_option('display.max_columns', None)

# ===========================================================
# 1. SETUP AND DATA LOADING (STORE DATA IN DATAFRAME)
# ===========================================================

# NOTE: Replace 'video_metadata.csv' with your actual file path.
FILE_PATH = 'merged_data.csv'

try:
    # Assuming your file is a CSV. Adjust sep= if needed.
    df = pd.read_csv(FILE_PATH)
except FileNotFoundError:
    print(f"ERROR: File not found at '{FILE_PATH}'. Loading a mock DataFrame for demonstration.")
    # --- Mock DataFrame Creation ---
    data = {
        'id': ['v1', 'v2', 'v3', 'v1', 'v5', 'v6', 'v7', 'v8', 'v9', 'v10'],
        'title': ['Best Prince of Persia Game Review', 'Top 5 PoP Mistakes', 'Beginners Guide to Gaming', 'Best Prince of Persia Game Review', 'New Release Trailer', 'Short Gaming Clip', 'Podcast on History', 'Tech News 2024', 'Quick Guide', 'Old Classic Review'],
        'description': ['Long description about the game.', 'Short summary.', np.nan, 'Long description about the game.', 'Trailer.', 'Clip.', 'History podcast.', 'News segment.', 'Guide.', 'Classic game review.'],
        'tags': ['pop, review', 'top5, mistakes', np.nan, 'pop, review', 'trailer, new', 'clip', 'podcast, history', 'tech, news', 'guide', 'classic, review'],
        'category': ['Gaming', 'Gaming', 'Tutorial', 'Gaming', 'Trailer', 'Clip', 'Podcast', 'News', 'Tutorial', 'Gaming'],
        'publishedAt': ['2023-10-01T10:00:00Z', '2023-10-05T12:00:00Z', '2024-01-15T18:30:00Z', '2023-10-01T10:00:00Z', '2024-03-20T09:00:00Z', '2023-11-01T10:00:00Z', '2023-12-05T12:00:00Z', '2024-04-15T18:30:00Z', '2024-04-22T09:00:00Z', '2023-09-01T10:00:00Z'],
        'viewCount': [100000, 50000, 100, 100000, 5000, 8000, 25000, 15000, 300, 40000],
        'likeCount': [9500, 4000, 10, 9500, np.nan, 500, 2000, 1000, 20, 3500],
        'duration': ['PT15M30S', 'PT5M0S', 'PT2H10M', 'PT15M30S', 'PT1M30S', 'PT0M45S', 'PT30M', 'PT8M15S', 'PT3M', 'PT20M'],
        'channelId': ['c1', 'c2', 'c3', 'c1', 'c4', 'c2', 'c1', 'c5', 'c3', 'c4']
    }
    df = pd.DataFrame(data)

print("--- Initial Data Load & Info ---")
df.info()
print("\n")

# ===========================================================
# 2. DATA CLEANING AND PREPROCESSING
# ===========================================================

# --- A. Data Type Conversion ---
print("--- Data Preprocessing ---")

# 1. Convert 'publishedAt' to datetime objects
df['publishedAt'] = pd.to_datetime(df['publishedAt'], errors='coerce')

# 2. Convert count columns to numeric (using 'Int64' to allow for NaN/missing values)
count_cols = ['viewCount', 'likeCount', 'commentCount']
for col in count_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce').astype('Int64')

# 3. Convert ISO 8601 'duration' (e.g., 'PT15M30S') to total seconds
def convert_duration_to_seconds(duration):
    if pd.isna(duration) or duration is None:
        return np.nan
    try:
        return parse_duration(duration).total_seconds()
    except Exception:
        return np.nan

if 'duration' in df.columns:
    df['duration_sec'] = df['duration'].apply(convert_duration_to_seconds)

# 4. Extract time features for EDA
df['publish_year'] = df['publishedAt'].dt.year
df['publish_year_month'] = df['publishedAt'].dt.to_period('M')
df['publish_dayofweek'] = df['publishedAt'].dt.day_name()

print("Preprocessing complete. New columns added (e.g., 'duration_sec', 'publish_year').")
print("\n")


# ===========================================================
# 3. EDA ON METADATA (UNIQUENESS, MISSING VALUES)
# ===========================================================

print("--- 3. Uniqueness and Missing Values Analysis ---")

# --- Row and column uniqueness ---
# Check for and remove exact duplicate rows
num_duplicates = df.duplicated().sum()
if num_duplicates > 0:
    df_cleaned = df.drop_duplicates(keep='first').copy()
    print(f"Total Duplicate Rows found and removed: {num_duplicates}. New size: {len(df_cleaned)}")
else:
    df_cleaned = df.copy()
    print("No exact duplicate rows found.")

# Column Uniqueness Ratio
unique_ratios = df_cleaned.drop(columns=['id'], errors='ignore').nunique() / len(df_cleaned)
print("\nUnique Value Ratio per Column (closer to 1.0 means more unique content):")
print(unique_ratios.sort_values(ascending=False))


# --- Title Uniqueness ---
title_uniqueness = df_cleaned['title'].nunique() / len(df_cleaned)
print(f"\nTitle Uniqueness Ratio: {title_uniqueness:.4f}")

# --- Missing Values ---
print("\n--- Missing Values Report (Percentage) ---")
missing_info = df_cleaned.isnull().sum()
missing_percent = (missing_info / len(df_cleaned)) * 100
missing_df = pd.DataFrame({'Missing Count': missing_info, 'Missing %': missing_percent})
print(missing_df[missing_df['Missing Count'] > 0].sort_values(by='Missing %', ascending=False))

# --- Date Distribution (Visualization) ---
print("\n--- Date Distribution ---")
if 'publish_year' in df_cleaned.columns:
    plt.figure(figsize=(10, 5))
    df_cleaned['publish_year'].value_counts().sort_index().plot(kind='bar', color='darkgreen')
    plt.title('Distribution of Videos by Published Year')
    plt.xlabel('Year')
    plt.ylabel('Number of Videos')
    plt.xticks(rotation=45)
    plt.show()


# ===========================================================
# 4. ANALYSIS: TITLE DISTRIBUTIONS
# ===========================================================

print("\n--- 4. Title Distribution Analysis ---")

# --- Title Length Distribution ---
df_cleaned['title_length'] = df_cleaned['title'].astype(str).apply(len)
df_cleaned['title_word_count'] = df_cleaned['title'].astype(str).apply(lambda x: len(x.split()))

print("Title Word Count Statistics:")
print(df_cleaned['title_word_count'].describe())

plt.figure(figsize=(10, 5))
sns.histplot(df_cleaned['title_word_count'], bins=15, kde=True, color='indianred')
plt.title('Distribution of Title Word Count')
plt.xlabel('Word Count')
plt.ylabel('Frequency')
plt.show()

# --- Most Common Words in Titles (N-grams) ---
def get_top_n_ngrams(corpus, n=10, ngram_range=(1, 1)):
    # Use CountVectorizer to find word frequencies, ignoring English stop words
    vec = CountVectorizer(stop_words='english', ngram_range=ngram_range).fit(corpus.astype(str))
    bag_of_words = vec.transform(corpus.astype(str))
    sum_words = bag_of_words.sum(axis=0) 
    words_freq = [(word, sum_words[0, idx]) for word, idx in vec.vocabulary_.items()]
    words_freq.sort(key=lambda x: x[1], reverse=True)
    return pd.DataFrame(words_freq[:n], columns=['Phrase', 'Count'])

# Top 10 Unigrams (Single Words)
top_unigrams = get_top_n_ngrams(df_cleaned['title'], 10, ngram_range=(1, 1))
print("\nTop 10 Most Common Single Words (Unigrams):")
print(top_unigrams)

# Top 10 Bigrams (Two-Word Phrases)
top_bigrams = get_top_n_ngrams(df_cleaned['title'], 10, ngram_range=(2, 2))
print("\nTop 10 Most Common Two-Word Phrases (Bigrams):")
print(top_bigrams)


# ===========================================================
# 5. ANALYSIS: PUBLISH FREQUENCY OVER TIME
# ===========================================================

print("\n--- 5. Publish Frequency Over Time Analysis ---")

# --- Publish Frequency Trend (Monthly) ---
if 'publish_year_month' in df_cleaned.columns:
    # Calculate counts and convert PeriodIndex to datetime for plotting
    monthly_counts = df_cleaned['publish_year_month'].value_counts().sort_index()
    monthly_counts.index = monthly_counts.index.to_timestamp()

    plt.figure(figsize=(15, 6))
    monthly_counts.plot(kind='line', marker='o', color='royalblue')
    plt.title('Video Publish Frequency Over Time (Monthly Trend)')
    plt.xlabel('Time (Year-Month)')
    plt.ylabel('Number of Videos Published')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

# --- Publish Frequency by Day of Week ---
if 'publish_dayofweek' in df_cleaned.columns:
    # Ensure correct order of days
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    day_counts = df_cleaned['publish_dayofweek'].value_counts().reindex(day_order)

    plt.figure(figsize=(10, 5))
    day_counts.plot(kind='bar', color='goldenrod')
    plt.title('Publish Frequency by Day of the Week')
    plt.xlabel('Day of Week')
    plt.ylabel('Number of Videos')
    plt.xticks(rotation=0)
    plt.show()


# ===========================================================
# DELIVERABLE: CLEANED VIDEO METADATA DATASET
# ===========================================================

print("\n\n===============================================")
print("FINAL DELIVERABLE: CLEANED VIDEO METADATA DATASET")
print("===============================================")

print(f"Final Cleaned Dataset Size: {df_cleaned.shape}")
print("First 5 rows of the cleaned data (with added features):")
print(df_cleaned.head())

# Optional: Save the cleaned dataset to a new CSV
# df_cleaned.to_csv('cleaned_video_metadata.csv', index=False)
# print("\nCleaned dataset saved to 'cleaned_video_metadata.csv'")
