import polars as pl
import yt_dlp
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.feature_extraction.text import CountVectorizer
import re
from collections import Counter
import time
import os

def fetch_upload_date(video_id):
    """Fetch upload_date for a video_id using yt_dlp."""
    url = f"https://www.youtube.com/watch?v={video_id}"
    ydl_opts = {
        'quiet': True,
        'extract_flat': True,
        'logger': None,  # Suppress ffmpeg warnings
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return info.get('upload_date', None)
    except Exception as e:
        print(f"Error fetching date for {video_id}: {e}")
        return None

def load_data(csv_path):
    """Load cleaned CSV into a Polars DataFrame."""
    try:
        df = pl.read_csv(csv_path)
        print(f"Loaded {len(df)} rows and {len(df.columns)} columns from {csv_path}")
        return df
    except Exception as e:
        print(f"Error loading CSV: {e}")
        return None

def add_upload_dates(df):
    """Fetch and add upload_date column to DataFrame."""
    print("Fetching upload dates...")
    dates = []
    for video_id in df["video_id"].to_list():
        date = fetch_upload_date(video_id)
        dates.append(date)
        time.sleep(2)  # Rate limiting
    df = df.with_columns(pl.Series(name="upload_date", values=dates))
    return df

def check_uniqueness(df):
    """Check row and column uniqueness."""
    duplicate_rows = df.filter(df.is_duplicated()).height
    unique_rows = df.unique().height
    print(f"\nTotal rows: {df.height}, Unique rows: {unique_rows}, Duplicate rows: {duplicate_rows}")
    
    uniqueness = {}
    for col in df.columns:
        unique_count = df[col].n_unique()
        total_count = df[col].len()
        uniqueness[col] = {
            "unique_values": unique_count,
            "unique_percentage": (unique_count / total_count) * 100 if total_count > 0 else 0
        }
    print("\nColumn Uniqueness:")
    for col, stats in uniqueness.items():
        print(f"{col}: {stats['unique_values']} unique values ({stats['unique_percentage']:.2f}% unique)")
    
    return uniqueness

def analyze_title_distribution(df):
    """Analyze title distribution and common words."""
    titles = df["video_title"].drop_nulls().to_list()
    print(f"\nTitle Analysis: {len(titles)} titles, {df['video_title'].n_unique()} unique titles")
    
    vectorizer = CountVectorizer(stop_words="english", min_df=2)
    try:
        X = vectorizer.fit_transform(titles)
        words = vectorizer.get_feature_names_out()
        word_counts = X.sum(axis=0).A1
        word_freq = dict(zip(words, word_counts))
        
        word_df = pl.DataFrame({"word": list(word_freq.keys()), "frequency": list(word_freq.values())})
        word_df.write_csv("title_word_frequencies.csv")
        print("Saved title word frequencies to 'title_word_frequencies.csv'")
        
        top_words = dict(sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10])
        plt.figure(figsize=(10, 6))
        sns.barplot(x=list(top_words.values()), y=list(top_words.keys()))
        plt.title("Top 10 Words in Video Titles")
        plt.xlabel("Frequency")
        plt.ylabel("Word")
        plt.savefig("title_word_distribution.png")
        plt.close()
        print("Saved title word distribution plot to 'title_word_distribution.png'")
    except Exception as e:
        print(f"Error in title analysis: {e}")

def analyze_word_counts(df):
    """Analyze word counts in transcripts and descriptions."""
    transcript_counts = df["full_transcript"].drop_nulls().map_elements(
        lambda x: len(x.split()), return_dtype=pl.Int64
    )
    description_counts = df["video_description"].drop_nulls().map_elements(
        lambda x: len(x.split()), return_dtype=pl.Int64
    )
    
    print("\nWord Count Statistics:")
    print(f"Transcript word counts - Mean: {transcript_counts.mean():.2f}, "
          f"Max: {transcript_counts.max()}, Min: {transcript_counts.min()}")
    print(f"Description word counts - Mean: {description_counts.mean():.2f}, "
          f"Max: {description_counts.max()}, Min: {description_counts.min()}")
    
    plt.figure(figsize=(12, 5))
    plt.subplot(1, 2, 1)
    sns.histplot(transcript_counts, bins=20)
    plt.title("Transcript Word Count Distribution")
    plt.xlabel("Word Count")
    plt.subplot(1, 2, 2)
    sns.histplot(description_counts, bins=20)
    plt.title("Description Word Count Distribution")
    plt.xlabel("Word Count")
    plt.tight_layout()
    plt.savefig("word_count_distribution.png")
    plt.close()
    print("Saved word count distribution plot to 'word_count_distribution.png'")

def extract_keywords(df, column, top_n=10):
    """Extract top keywords from a text column."""
    text = " ".join(df[column].drop_nulls().to_list())
    words = re.findall(r'\b\w+\b', text.lower())
    stop_words = set(["the", "and", "to", "of", "in", "a", "for", "is", "are", "that", "this"])
    words = [w for w in words if w not in stop_words]
    word_freq = Counter(words).most_common(top_n)
    
    keyword_df = pl.DataFrame({"word": [w[0] for w in word_freq], "frequency": [w[1] for w in word_freq]})
    keyword_df.write_csv(f"{column}_keywords.csv")
    print(f"Saved {column} keywords to '{column}_keywords.csv'")
    
    plt.figure(figsize=(10, 6))
    sns.barplot(x=[w[1] for w in word_freq], y=[w[0] for w in word_freq])
    plt.title(f"Top {top_n} Keywords in {column.replace('_', ' ').title()}")
    plt.xlabel("Frequency")
    plt.ylabel("Word")
    plt.savefig(f"{column}_keywords.png")
    plt.close()
    print(f"Saved {column} keywords plot to '{column}_keywords.png'")

def perform_eda(df):
    """Perform EDA: missing values, title uniqueness, date distribution."""
    missing = df.select([pl.col(col).is_null().sum().alias(f"missing_{col}") for col in df.columns])
    print("\nMissing Values:")
    for col in missing.columns:
        count = missing[col][0]
        print(f"{col.replace('missing_', '')}: {count} missing ({count/df.height*100:.2f}%)")
    
    print(f"\nTitle Uniqueness: {df['video_title'].n_unique()} unique titles out of {df['video_title'].len()} total")
    
    if "upload_date" in df.columns and df["upload_date"].is_null().sum() < df.height:
        df = df.with_columns(
            pl.col("upload_date").str.strptime(pl.Date, "%Y%m%d", strict=False).alias("upload_date")
        )
        monthly_counts = df.group_by(pl.col("upload_date").dt.strftime("%Y-%m")).agg(count=pl.len()).sort("upload_date")
        print("\nMonthly Upload Frequency:")
        print(monthly_counts)
        
        plt.figure(figsize=(10, 6))
        sns.lineplot(data=monthly_counts, x="upload_date", y="count")
        plt.title("Video Upload Frequency Over Time")
        plt.xlabel("Month")
        plt.ylabel("Number of Videos")
        plt.xticks(rotation=45)
        plt.savefig("upload_frequency.png")
        plt.close()
        print("Saved upload frequency plot to 'upload_frequency.png'")
        
        plt.figure(figsize=(10, 6))
        sns.histplot(df["upload_date"].drop_nulls(), bins=20)
        plt.title("Upload Date Distribution")
        plt.xlabel("Upload Date")
        plt.ylabel("Count")
        plt.xticks(rotation=45)
        plt.savefig("upload_date_distribution.png")
        plt.close()
        print("Saved upload date distribution plot to 'upload_date_distribution.png'")
    else:
        print("\nDate Distribution: Not enough valid 'upload_date' values for analysis.")

def main():
    """Main function to fetch dates and analyze the cleaned CSV."""
    csv_path = "Beast_Philanthropy_transcript_cleaned.csv"
    output_csv = "Beast_Philanthropy_transcript_with_dates.csv"
    
    df = load_data(csv_path)
    if df is None:
        return
    
    df = add_upload_dates(df)
    df.write_csv(output_csv)
    print(f"Saved updated CSV with upload_date to {output_csv}")
    
    check_uniqueness(df)
    analyze_title_distribution(df)
    analyze_word_counts(df)
    extract_keywords(df, "full_transcript", top_n=10)
    extract_keywords(df, "video_description", top_n=10)
    perform_eda(df)

if __name__ == "__main__":
    main()
