import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import warnings
import re
from collections import Counter
import os # Necessary for handling file system tasks (like creating folders)

# We use this to suppress minor warnings that don't affect the final result
warnings.filterwarnings('ignore')

# --- CONFIGURATION: SET YOUR FILE PATHS HERE ---
# IMPORTANT: These paths are set up to be relative and portable.
# Place 'task2_master_dataset.csv' in the same folder as this script to run it easily.

# INPUT: Assumes your file is in the same directory as this script.
INPUT_FILE_PATH = r'C:\Users\dream\Desktop\Internships\Infosys Springboard\QueryTube\task2_master_dataset.csv'

# OUTPUT: This is where all the plots and cleaned CSVs will be saved.
# It will create the full directory structure if it doesn't exist.
OUTPUT_DIR = './Result' 
# --- END CONFIGURATION ---


def enhanced_transcript_quality_and_eda(input_filepath, output_directory):
    """
    This is the main engine! It performs a comprehensive Data Quality Check and
    Exploratory Data Analysis (EDA) on the YouTube Transcript Dataset, then
    generates a full visualization dashboard and summary reports.
    """

    print("Transcript Dataset Analysis with Visualizations")
    print("=" * 70)
    print(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # 1. Prepare the Output Folder
    # We make sure the folder for saving all our results exists before we start.
    try:
        os.makedirs(output_directory, exist_ok=True)
        print(f"[OK] Output folder created/verified: {output_directory}")
    except Exception as e:
        print(f"[ERROR] Had trouble creating the output folder: {e}")
        return

    # 2. Load the Dataset
    try:
        # We try 'utf-8' encoding first, as it's the standard for text data.
        df = pd.read_csv(input_filepath, encoding='utf-8')
        print(f"[OK] Dataset loaded: {df.shape[0]} rows x {df.shape[1]} columns")
    except FileNotFoundError:
        print(f"[ERROR] Could not find the file at '{input_filepath}'!")
        return None
    except Exception as e:
        print(f"[ERROR] Error loading data: {str(e)}")
        return None

    # Standardize column naming: We expect the video identifier to be 'id' or 'video_id'.
    if 'id' in df.columns and 'video_id' not in df.columns:
        df.rename(columns={'id': 'video_id'}, inplace=True)
        
    # Make sure the video IDs are clean strings before checking their length
    df['video_id'] = df['video_id'].astype(str).str.strip()

    # 3. CRITICAL DATA CLEANING AND FILTERING
    
    # We apply the specific data quality rules we discovered earlier:
    # A. Corrupted ID Check: A standard YouTube video ID must be 11 characters long.
    TYPICAL_ID_LENGTH = 11
    df['id_length'] = df['video_id'].str.len()
    
    # B. Transcript Retrieval Error Check: Filter out rows where the transcript
    # field contains the specific error message, plus the corrupted ID rows.
    ERROR_STRING = 'Error: \nCould not retrieve a transcript'
    
    # We create the final clean dataset containing ONLY high-quality, usable records
    df_clean = df[(df['id_length'] == TYPICAL_ID_LENGTH) & (~df['transcript'].astype(str).str.contains(ERROR_STRING, na=False))].copy()
    
    total_records = len(df)
    valid_records = len(df_clean)
    invalid_records = total_records - valid_records
    
    print(f"\nInitial Cleaning: Filtered out {invalid_records} invalid records (due to bad IDs or retrieval errors).")
    print(f"{valid_records} clean records remaining for in-depth analysis.")
    
    if df_clean.empty:
        print("Dataset is empty after cleaning. Cannot proceed with EDA.")
        return

    # From now on, we only work with the clean, reliable data
    df = df_clean
    
    # Setup for visuals: make the charts look professional
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

    # 1. Dataset Overview (Plot 0,0)
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
    
    # 2. Missing Values Check (Plot 0,1)
    print(f"\nMISSING VALUES (Post-Cleaning):")
    missing_counts = df.isnull().sum()
    
    if missing_counts.sum() > 0:
        missing_data = missing_counts[missing_counts > 0]
        missing_data.plot(kind='bar', ax=axes[0,1], color='coral')
        axes[0,1].set_title('Missing Values (Post-Cleaning)')
        axes[0,1].set_ylabel('Missing Count')
    else:
        # Show that the dataset is now fully complete
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

    # 4. Feature Engineering: Create Text Metrics
    print(f"\nTEXT METRICS:")
    # Calculate basic length metrics
    df['transcript_length'] = df['transcript'].astype(str).str.len()
    df['word_count'] = df['transcript'].astype(str).str.split().str.len()
    
    # Sentence Count: Count terminal punctuation and newlines
    df['sentence_count'] = (df['transcript'].astype(str).str.count(r'[\.!?](?=\s+\S|$)') + 
                            df['transcript'].astype(str).str.count(r'\n'))
    
    df['paragraph_count'] = df['transcript'].astype(str).str.count(r'\n') + 1

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
    # Helper function to assign a length category based on word count
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
    
    # Ensure all categories appear in order on the chart
    category_order = ['Short (<500 words)', 'Medium (500-1500 words)', 'Long (1500-3000 words)', 'Very Long (>3000 words)']
    length_dist = length_dist.reindex(category_order, fill_value=0)

    for category, count in length_dist.items():
        percentage = (count / len(df)) * 100
        print(f"  * {category}: {count} transcripts ({percentage:.1f}%)")

    colors = ['lightcoral', 'gold', 'lightblue', 'lightgreen']
    axes[1,2].pie(length_dist.values, labels=length_dist.index, autopct='%1.1f%%',
                  colors=colors[:len(length_dist)], startangle=90)
    axes[1,2].set_title('Content Length Categories')

    # 8. Text Quality Analysis (Plot 2,0)
    print(f"\nTEXT QUALITY ANALYSIS (Formatting Issues):")
    df['is_empty'] = df['transcript'].astype(str).str.strip().eq('')
    df['is_very_short'] = df['transcript_length'] < 100 
    # Check for common sound/action markers (e.g., [Music], (Applause))
    df['has_markers'] = df['transcript'].astype(str).str.contains(r'\[\w+\]|\(\w+\)',
                                                                 na=False, case=False)
    # Check for common timestamp patterns (e.g., 0:30, 1:45)
    df['has_timestamps'] = df['transcript'].astype(str).str.contains(r'\d{1,2}:\d{2}', na=False)
    df['has_newlines'] = df['transcript'].astype(str).str.contains(r'\n', na=False)

    quality_issues = {
        'Empty': df['is_empty'].sum(),
        'Very Short': df['is_very_short'].sum(),
        'Markers': df['has_markers'].sum(),
        'Timestamps': df['has_timestamps'].sum(),
        'Multi-line': df['has_newlines'].sum()
    }

    issues_df = pd.DataFrame(list(quality_issues.items()), columns=['Issue', 'Count'])
    colors = ['red' if count > len(df)*0.5 else 'orange' if count > len(df)*0.1 else 'green'
              for count in issues_df['Count']]
    bars = axes[2,0].bar(issues_df['Issue'], issues_df['Count'], color=colors)
    axes[2,0].set_title('Text Quality Issues')
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
    completeness_score = (valid_records / total_records) * 100 
    uniqueness_score = (unique_rows / len(df)) * 100 
    
    # Text Quality: Penalize transcripts that are too short or empty
    good_transcripts = len(df) - df['is_empty'].sum() - df['is_very_short'].sum()
    text_quality_score = (good_transcripts / len(df)) * 100
    
    # Consistency: Penalize transcripts with formatting markers (e.g., [MUSIC])
    consistency_score = (1 - (df['has_markers'].sum() / len(df))) * 100 

    quality_metrics = {
        'Completeness': completeness_score,
        'Uniqueness': uniqueness_score,
        'Text Quality': text_quality_score,
        'Consistency': consistency_score
    }

    metrics_df = pd.DataFrame(list(quality_metrics.items()), columns=['Metric', 'Score'])
    colors = ['green' if score >= 90 else 'orange' if score >= 75 else 'red'
              for score in metrics_df['Score']]
    bars = axes[2,2].bar(metrics_df['Metric'], metrics_df['Score'], color=colors)
    axes[2,2].set_title('Quality Assessment Scores')
    axes[2,2].set_ylabel('Score (C\%)')
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
    
    # Provide a simple, actionable assessment
    if overall_score >= 90:
        print("Assessment: EXCELLENT! This dataset is ready for serious NLP.")
    elif overall_score >= 75:
        print("Assessment: GOOD. It's usable with just a bit of pre-processing.")
    else:
        print("Assessment: NEEDS IMPROVEMENT. A thorough cleaning stage is highly recommended.")

    print(f"\nData Preprocessing Recommendations (What to do next):")
    if df['has_markers'].sum() > 0:
        print(f"  * We found {df['has_markers'].sum()} transcripts with sound markers. Remove them (e.g., delete [MUSIC]) before NLP tasks.")
    if df['has_timestamps'].sum() > 0:
        print(f"  * We found {df['has_timestamps'].sum()} transcripts that likely contain timestamps. Strip these out to clean the text flow.")
    if df['has_newlines'].sum() > 0:
        print(f"  * We found {df['has_newlines'].sum()} multi-line transcripts. Normalize them (replace '\\n' with a space) to create uniform blocks of text.")

    # 11. Save All Results
    
    # Save visualizations
    plt.tight_layout(rect=[0, 0, 1, 0.96]) # Adjust for suptitle
    dashboard_path = os.path.join(output_directory, 'enhanced_transcript_analysis_dashboard.png')
    plt.savefig(dashboard_path, dpi=300, bbox_inches='tight')
    plt.close() 
    print(f"\n[OK] Visual dashboard saved as '{dashboard_path}'")

    # --- REMOVED: Detailed CSV File Generation (as requested by the user) ---
    # The user only requested plots and a report, not a cleaned dataset for subsequent steps.
    # The summary CSV below still serves as the report.
    # --------------------------------------------------------------------------

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

# --- EXECUTION BLOCK ---
if __name__ == "__main__":
    # Call the main function to start the comprehensive analysis
    enhanced_transcript_quality_and_eda(INPUT_FILE_PATH, OUTPUT_DIR)
