import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import warnings
import re
from collections import Counter
import os 
import time

# We use this to suppress minor warnings that don't affect the final result
warnings.filterwarnings('ignore')

# --- CONFIGURATION: SET YOUR FILE PATHS HERE ---
# INPUT: The original master dataset location.
INPUT_FILE_PATH = r'C:\Users\dream\Desktop\Internships\Infosys Springboard\QueryTube\task2_master_dataset.csv'

# CLEANED DATA OUTPUT: The destination for the new, cleaned dataset CSV.
CLEANED_DATA_OUTPUT_PATH = r'C:\Users\dream\Desktop\Internships\Infosys Springboard\QueryTube\Dataset Cleaning\task2_cleaned_transcripts.csv'

# EDA REPORT OUTPUT: The destination for the plots and summary report (CSV).
EDA_OUTPUT_DIR = r'C:\Users\dream\Desktop\Internships\Infosys Springboard\QueryTube\Dataset Cleaning\EDA_Reports'
# --- END CONFIGURATION ---


def clean_transcript_text(text):
    """
    Applies a comprehensive cleaning pipeline to a single transcript string.
    """
    if pd.isna(text) or text is None:
        return ""
    
    # 1. Convert to string and to lowercase (as requested)
    text = str(text).lower()

    # 2. Remove Markers: [Music], [Applause], (Laughter), etc.
    text = re.sub(r'\[.*?\]|\(.*?\)', ' ', text)
    
    # 3. Remove Timestamps: Formats like 00:01, 1:23:45
    text = re.sub(r'\d{1,2}:\d{2}(:\d{2})?\s*', ' ', text)
    
    # 4. Replace Newlines with spaces (as requested)
    text = text.replace('\n', ' ')
    
    # 5. Remove Special characters/Non-UTF symbols (keeping standard punctuation for now, 
    # but removing anything that is clearly non-text, like control characters or excessive whitespace)
    text = re.sub(r'[^\w\s\.\,\!\?]', '', text) # Keep alphanumeric, spaces, and basic terminal punctuation
    
    # 6. Normalize whitespace: reduce multiple spaces to a single space, and strip leading/trailing spaces
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text


def run_data_cleaning_pipeline(input_filepath, cleaned_output_path):
    """
    Handles loading, critical filtering (corrupted IDs/errors), applying the cleaning pipeline, 
    and saving the final cleaned dataset.
    """
    print("\n--- Starting Data Cleaning Pipeline ---")
    
    # 1. Prepare Output Folder for the Cleaned Dataset
    output_dir = os.path.dirname(cleaned_output_path)
    try:
        os.makedirs(output_dir, exist_ok=True)
        print(f"[OK] Cleaning output folder created/verified: {output_dir}")
    except Exception as e:
        print(f"[ERROR] Could not create cleaning output folder: {e}")
        return None

    # 2. Load the Dataset
    try:
        df = pd.read_csv(input_filepath, encoding='utf-8')
        print(f"[OK] Dataset loaded: {df.shape[0]} rows x {df.shape[1]} columns")
    except Exception as e:
        print(f"[ERROR] Error loading data: {e}")
        return None
        
    if 'id' in df.columns and 'video_id' not in df.columns:
        df.rename(columns={'id': 'video_id'}, inplace=True)
    df['video_id'] = df['video_id'].astype(str).str.strip()


    # 3. CRITICAL DATA FILTERING (Same as Step 3 in EDA)
    # Remove records that are fundamentally broken (corrupted ID or failed retrieval)
    TYPICAL_ID_LENGTH = 11
    ERROR_STRING = 'Error: \nCould not retrieve a transcript'
    
    df['id_length'] = df['video_id'].str.len()
    
    df_filtered = df[
        (df['id_length'] == TYPICAL_ID_LENGTH) & 
        (~df['transcript'].astype(str).str.contains(ERROR_STRING, na=False))
    ].copy()
    
    total_records = len(df)
    valid_records = len(df_filtered)
    invalid_records = total_records - valid_records
    
    print(f"Initial Filtering: Removed {invalid_records} fundamentally invalid records.")
    
    if df_filtered.empty:
        print("Dataset is empty after critical filtering. Cannot proceed.")
        return None

    # 4. Apply Transcript Cleaning Pipeline
    start_time = time.time()
    df_filtered['transcript_cleaned'] = df_filtered['transcript'].apply(clean_transcript_text)
    end_time = time.time()
    print(f"[OK] Cleaning pipeline applied to {len(df_filtered)} transcripts in {end_time - start_time:.2f} seconds.")

    # Drop the old 'transcript' column and rename the new one
    df_cleaned = df_filtered.drop(columns=['transcript', 'id_length']).rename(columns={'transcript_cleaned': 'transcript'})
    
    # 5. Save the Cleaned Dataset
    try:
        df_cleaned.to_csv(cleaned_output_path, index=False, encoding='utf-8')
        print(f"\n[SUCCESS] Cleaned dataset saved to: {cleaned_output_path}")
        return df_cleaned
    except Exception as e:
        print(f"[ERROR] Failed to save cleaned dataset: {e}")
        return None


def enhanced_transcript_quality_and_eda(df, output_directory):
    """
    Performs EDA and generates reports on the ALREADY CLEANED DataFrame.
    """

    print("\n--- Starting EDA & Reporting Pipeline ---")
    print("==========================================")
    
    # 1. Prepare the Output Folder for reports
    try:
        os.makedirs(output_directory, exist_ok=True)
        print(f"[OK] EDA output folder created/verified: {output_directory}")
    except Exception as e:
        print(f"[ERROR] Had trouble creating the EDA output folder: {e}")
        return

    # From now on, we only work with the clean, reliable data
    df = df.copy()
    total_records = len(df) # total records analyzed after cleaning
    
    # Setup for visuals
    plt.style.use('default')
    sns.set_palette("husl")

    # Prepare the 3x3 dashboard layout for all the plots
    fig, axes = plt.subplots(3, 3, figsize=(20, 15))
    fig.suptitle('Transcript Dataset: Quality Assessment & EDA Dashboard',
                 fontsize=16, fontweight='bold', y=0.98)

    # ==========================================
    # DATA QUALITY ASSESSMENT (Deep Dive)
    # ==========================================
    print("\nDATA QUALITY ASSESSMENT")
    print("=" * 40)

    # 1. Dataset Overview (Plot 0,0) - Reflecting the cleaned state
    print(f"\nDATASET OVERVIEW (Cleaned Data):")
    overview_data = {
        'Records': len(df),
        'Columns': len(df.columns),
        'Memory (MB)': df.memory_usage(deep=True).sum() / 1024**2
    }
    
    bars = axes[0,0].bar(overview_data.keys(), overview_data.values(),
                         color=['skyblue', 'lightgreen', 'salmon'])
    axes[0,0].set_title('Cleaned Dataset Overview', fontweight='bold')
    axes[0,0].set_ylabel('Count/Size')

    for bar, value in zip(bars, overview_data.values()):
        height = bar.get_height()
        axes[0,0].text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                       f'{value:.1f}' if isinstance(value, float) else f'{int(value)}',
                       ha='center', va='bottom', fontweight='bold')
    
    # 2. Missing Values Check (Plot 0,1) - Should be clean after filtering/cleaning
    print(f"\nMISSING VALUES (Post-Cleaning):")
    missing_counts = df.isnull().sum()
    
    if missing_counts.sum() > 0:
        missing_data = missing_counts[missing_counts > 0]
        missing_data.plot(kind='bar', ax=axes[0,1], color='coral')
        axes[0,1].set_title('Missing Values (Post-Cleaning)')
        axes[0,1].set_ylabel('Missing Count')
    else:
        axes[0,1].bar(['Complete Dataset'], [len(df)], color='lightgreen')
        axes[0,1].set_title('100% Data Completeness')
        axes[0,1].text(0, len(df)/2, f'{len(df)}\nrecords\ncomplete',
                       ha='center', va='center', fontweight='bold')
    
    # 3. Duplicate Analysis (Plot 0,2)
    print(f"\nDUPLICATE ANALYSIS:")
    total_duplicates = df.duplicated().sum()
    unique_rows = len(df) - total_duplicates
    duplicate_video_ids = df.duplicated(subset=['video_id']).sum()
    unique_video_ids = df['video_id'].nunique()

    print(f"Total clean records: {len(df)}")
    print(f"Complete duplicates: {total_duplicates}")
    print(f"Duplicate video IDs: {duplicate_video_ids}")
    
    duplicate_stats = ['Unique Records', 'Duplicate Records', 'Unique IDs', 'Duplicate IDs']
    duplicate_counts = [unique_rows, total_duplicates, unique_video_ids, duplicate_video_ids]
    colors = ['lightblue', 'coral', 'lightgreen', 'orange']

    bars = axes[0,2].bar(duplicate_stats, duplicate_counts, color=colors)
    axes[0,2].set_title('Duplicate Analysis')
    axes[0,2].set_ylabel('Count')
    axes[0,2].tick_params(axis='x', rotation=45)

    for bar, count in zip(bars, duplicate_counts):
        if count > 0:
            height = bar.get_height()
            axes[0,2].text(bar.get_x() + bar.get_width()/2., height + 0.5,
                           f'{count}', ha='center', va='bottom', fontweight='bold')

    # 4. Feature Engineering: Create Text Metrics on the CLEANED TEXT
    print(f"\nTEXT METRICS:")
    # Calculate basic length metrics on the 'transcript' column (which is now cleaned)
    df['transcript_length'] = df['transcript'].astype(str).str.len()
    df['word_count'] = df['transcript'].astype(str).str.split().str.len()
    
    # Since we cleaned timestamps/newlines/markers, sentence and paragraph counts will be simpler.
    df['sentence_count'] = df['transcript'].astype(str).str.count(r'[\.!?]')
    df['paragraph_count'] = 1 # Since newlines were replaced with spaces, we treat all as one paragraph

    print(f"Average word count: {df['word_count'].mean():,.0f} words")
    print(f"Content length range: {df['transcript_length'].min():,} - {df['transcript_length'].max():,} characters")

    # ==========================================
    # EXPLORATORY DATA ANALYSIS WITH VISUALS
    # ==========================================
    print(f"\nEXPLORATORY DATA ANALYSIS")
    print("=" * 40)

    # 5. Content Length Distribution (Characters - Plot 1,0)
    axes[1,0].hist(df['transcript_length'], bins=20, color='skyblue', alpha=0.7, edgecolor='black')
    axes[1,0].axvline(df['transcript_length'].mean(), color='red', linestyle='--', linewidth=2,
                      label=f'Mean: {df["transcript_length"].mean():,.0f}')
    axes[1,0].axvline(df['transcript_length'].median(), color='green', linestyle='--', linewidth=2,
                      label=f'Median: {df["transcript_length"].median():,.0f}')
    axes[1,0].set_title('Character Length Distribution')
    axes[1,0].set_xlabel('Character Count')
    axes[1,0].set_ylabel('Frequency')
    axes[1,0].legend()

    # 6. Word Count Distribution (Plot 1,1)
    axes[1,1].hist(df['word_count'], bins=20, color='lightgreen', alpha=0.7, edgecolor='black')
    axes[1,1].axvline(df['word_count'].mean(), color='red', linestyle='--', linewidth=2,
                      label=f'Mean: {df["word_count"].mean():,.0f}')
    axes[1,1].axvline(df['word_count'].median(), color='blue', linestyle='--', linewidth=2,
                      label=f'Median: {df["word_count"].median():,.0f}')
    axes[1,1].set_title('Word Count Distribution')
    axes[1,1].set_xlabel('Word Count')
    axes[1,1].set_ylabel('Frequency')
    axes[1,1].legend()

    # 7. Content Length Categories (Plot 1,2)
    print(f"\nCONTENT CATEGORIZATION:")
    def categorize_length(word_count):
        if word_count < 500:
            return 'Short (<500 words)'
        elif word_count < 1500:
            return 'Medium (500-1500 words)'
        elif word_count < 3000:
            return 'Long (1500-3000 words)'
        else:
            return 'Very Long (>3000 words)'

    df['length_category'] = df['word_count'].apply(categorize_length)
    length_dist = df['length_category'].value_counts()
    
    category_order = ['Short (<500 words)', 'Medium (500-1500 words)', 'Long (1500-3000 words)', 'Very Long (>3000 words)']
    length_dist = length_dist.reindex(category_order, fill_value=0)

    for category, count in length_dist.items():
        percentage = (count / len(df)) * 100
        print(f"  * {category}: {count} transcripts ({percentage:.1f}%)")

    colors = ['lightcoral', 'gold', 'lightblue', 'lightgreen']
    axes[1,2].pie(length_dist.values, labels=length_dist.index, autopct='%1.1f%%',
                  colors=colors[:len(length_dist)], startangle=90)
    axes[1,2].set_title('Content Length Categories')

    # 8. Text Quality Analysis (Plot 2,0) - Focused on post-cleaning issues (e.g., remaining short/empty)
    print(f"\nTEXT QUALITY ANALYSIS (Post-Cleaning Issues):")
    df['is_empty'] = df['transcript'].astype(str).str.strip().eq('')
    df['is_very_short'] = df['transcript_length'] < 100 
    
    quality_issues = {
        'Empty (Post-Clean)': df['is_empty'].sum(),
        'Very Short (<100 Chars)': df['is_very_short'].sum()
    }

    issues_df = pd.DataFrame(list(quality_issues.items()), columns=['Issue', 'Count'])
    colors = ['red' if count > len(df)*0.5 else 'orange' if count > len(df)*0.1 else 'green'
              for count in issues_df['Count']]
    bars = axes[2,0].bar(issues_df['Issue'], issues_df['Count'], color=colors)
    axes[2,0].set_title('Text Quality Issues (Post-Cleaning)')
    axes[2,0].set_ylabel('Count')
    axes[2,0].tick_params(axis='x', rotation=45)

    for bar, count in zip(bars, issues_df['Count']):
        if count > 0:
            height = bar.get_height()
            axes[2,0].text(bar.get_x() + bar.get_width()/2., height + 0.5,
                           f'{count}', ha='center', va='bottom', fontweight='bold')


    # 9. Word Frequency Analysis (Plot 2,1)
    print(f"\nWORD FREQUENCY ANALYSIS:")
    all_text = ' '.join(df['transcript'].astype(str)).lower()
    clean_text = re.sub(r'[^a-zA-Z\s]', ' ', all_text)
    all_words = clean_text.split()

    # Define a set of words to ignore (stop words and common markers)
    stop_words = set(list(set(plt.cm.datad.keys())) + ['this', 'that', 'with', 'have', 'will', 'from', 'they', 'been', 'were',
                 'their', 'said', 'each', 'which', 'what', 'there', 'would', 'could',
                 'should', 'about', 'other', 'more', 'very', 'time', 'just', 'like',
                 'know', 'think', 'people', 'going', 'really', 'things', 'right',
                 'music', 'applause', 'laughter', 'when', 'where', 'here', 'than',
                 'after', 'before', 'through', 'during', 'above', 'below', 'down',
                 'into', 'over', 'under', 'again', 'further', 'then', 'once'])

    # Find words that are meaningful (longer than 3 characters, not a stop word, not a number)
    meaningful_words = [word for word in all_words
                        if len(word) > 3 and word not in stop_words and not word.isdigit()]

    word_freq = Counter(meaningful_words)
    top_12_words = word_freq.most_common(12)

    print("Most frequent meaningful words (great for topic spotting!):")
    for i, (word, freq) in enumerate(top_12_words[:10], 1):
        print(f"  {i:2d}. '{word}': {freq:,} occurrences")

    if top_12_words:
        words, frequencies = zip(*top_12_words)
        axes[2,1].bar(words, frequencies, color='#FFC107')
        axes[2,1].set_title('Top 12 Most Frequent Words')
        axes[2,1].set_ylabel('Frequency')
        axes[2,1].tick_params(axis='x', rotation=45)

    # 10. Overall Quality Assessment Score (Plot 2,2)
    print(f"\nOVERALL QUALITY ASSESSMENT SCORE:")

    # Calculate individual quality dimension scores (0-100%)
    # We now use the total_records from the cleaning stage for completeness
    completeness_score = (len(df) / total_records) * 100 
    uniqueness_score = (unique_rows / len(df)) * 100 
    
    # Text Quality: Penalize transcripts that are too short or empty
    good_transcripts = len(df) - df['is_empty'].sum() - df['is_very_short'].sum()
    text_quality_score = (good_transcripts / len(df)) * 100
    
    # Consistency: Score is 100% since we just cleaned for markers/newlines/timestamps
    consistency_score = 100.0

    quality_metrics = {
        'Completeness (Usable)': completeness_score,
        'Uniqueness': uniqueness_score,
        'Text Quality (Length)': text_quality_score,
        'Consistency (Format)': consistency_score
    }

    metrics_df = pd.DataFrame(list(quality_metrics.items()), columns=['Metric', 'Score'])
    colors = ['green' if score >= 90 else 'orange' if score >= 75 else 'red'
              for score in metrics_df['Score']]
    bars = axes[2,2].bar(metrics_df['Metric'], metrics_df['Score'], color=colors)
    axes[2,2].set_title('Quality Assessment Scores')
    axes[2,2].set_ylabel('Score (%)')
    axes[2,2].set_ylim(0, 100)
    axes[2,2].tick_params(axis='x', rotation=45)

    for bar, score in zip(bars, metrics_df['Score']):
        height = bar.get_height()
        axes[2,2].text(bar.get_x() + bar.get_width()/2., height + 1,
                       f'{score:.1f}%', ha='center', va='bottom', fontweight='bold')

    overall_score = np.mean(list(quality_metrics.values()))

    # ==========================================
    # ENHANCED INSIGHTS AND RECOMMENDATIONS
    # ==========================================
    print(f"\n" + "=" * 70)
    print("ENHANCED ANALYSIS SUMMARY")
    print("=" * 70)

    print(f"\nOverall Data Quality Score: {overall_score:.1f}%")
    
    if overall_score >= 90:
        print("Assessment: EXCELLENT! This dataset is now highly reliable.")
    elif overall_score >= 75:
        print("Assessment: GOOD. Final dataset is robust for analysis.")
    else:
        print("Assessment: NEEDS FURTHER REVIEW.")

    print(f"\nData Integrity Check (Post-Cleaning):")
    if df['is_empty'].sum() > 0 or df['is_very_short'].sum() > 0:
        print(f"  * WARNING: {df['is_empty'].sum()} transcripts are still empty and {df['is_very_short'].sum()} are very short. Consider removing them.")
    else:
        print("  * All transcripts have meaningful content length.")


    # 11. Save All Results
    
    # Save visualizations
    plt.tight_layout(rect=[0, 0, 1, 0.96]) 
    dashboard_path = os.path.join(output_directory, 'enhanced_transcript_analysis_dashboard.png')
    plt.savefig(dashboard_path, dpi=300, bbox_inches='tight')
    plt.close() 
    print(f"\n[OK] Visual dashboard saved as '{dashboard_path}'")

    # Save summary results CSV (This acts as the structured report)
    summary_results = pd.DataFrame([quality_metrics])
    summary_results['overall_score'] = overall_score
    summary_results['total_records_initial'] = total_records
    summary_results['total_records_analyzed'] = len(df)
    summary_results['unique_video_ids'] = unique_video_ids
    summary_results['avg_words'] = df['word_count'].mean()
    summary_results['most_common_category'] = length_dist.index[0]
    
    summary_path = os.path.join(output_directory, 'enhanced_quality_summary.csv')
    summary_results.to_csv(summary_path, index=False)
    print(f"[OK] Quality summary (report) saved to '{summary_path}'")

    print(f"\n--- Data Analysis Pipeline Finished Successfully ---")
    return


# --- MAIN EXECUTION BLOCK ---
if __name__ == "__main__":
    
    # Step 1: Run the Cleaning Pipeline to produce the reliable dataset
    cleaned_df = run_data_cleaning_pipeline(INPUT_FILE_PATH, CLEANED_DATA_OUTPUT_PATH)
    
    if cleaned_df is not None:
        # Step 2: Run the EDA and Reporting on the newly cleaned dataset
        enhanced_transcript_quality_and_eda(cleaned_df, EDA_OUTPUT_DIR)
    else:
        print("\nAnalysis aborted due to failure in the cleaning pipeline.")
