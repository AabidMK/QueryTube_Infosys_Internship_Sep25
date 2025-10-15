import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os # Import the os library for directory operations

# --- Configuration ---
# Updated FILE_PATH using a raw string (r"...") to safely handle Windows backslashes.
FILE_PATH = r"C:\Users\dream\Desktop\Internships\Infosys Springboard\QueryTube\task1_master_dataset.csv" 
REPORT_FILENAME = "data_quality_and_eda_report.txt"

# New: Define the output directory where all results (plots and report) will be saved
OUTPUT_DIR = r"C:\Users\dream\Desktop\Internships\Infosys Springboard\QueryTube\EDA_and_Data_Quality_Check\Results\Task_1_dataset"

def create_output_directory(output_path):
    """Creates the specified directory if it does not already exist."""
    os.makedirs(output_path, exist_ok=True)
    print(f"Ensuring output directory exists: {output_path}\n")

def load_and_prepare_data(file_path):
    """Loads the dataset and performs initial data type conversions."""
    print(f"Loading data from: {file_path}")
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        # This error message is now more informative given the absolute path
        print(f"ERROR: File not found at the specified path: {file_path}")
        print("Please double-check that the file exists and the path is correct.")
        return None

    # Rename the first column for clarity
    if 'Unnamed: 0' in df.columns:
        df = df.rename(columns={'Unnamed: 0': 'index_col'})
    
    # Convert 'publishedAt' to datetime object
    df['publishedAt'] = pd.to_datetime(df['publishedAt'], errors='coerce')
    
    # Convert large number columns to numeric (in case of subtle string representations)
    for col in ['viewCount', 'likeCount', 'commentCount', 'channel_subscriberCount', 'channel_videoCount']:
        # Ensure they are numeric, forcing non-convertible values to NaN (though they appear to be int64 already)
        df[col] = pd.to_numeric(df[col], errors='coerce')

    print("Data loaded and initial preparation complete.\n")
    return df

def run_data_quality_check(df):
    """Performs Data Quality Checks (Missing values, Duplicates, Unique values)."""
    
    # --- 1. Missing Values Analysis ---
    print("--- 1. DATA QUALITY CHECK: MISSING VALUES ---")
    
    missing_data = df.isnull().sum().sort_values(ascending=False)
    missing_data = missing_data[missing_data > 0]
    
    if missing_data.empty:
        print("Great! No missing values found in the entire dataset.")
    else:
        missing_data_percent = (missing_data / len(df)) * 100
        missing_df = pd.DataFrame({
            'Missing Count': missing_data,
            'Percentage (%)': missing_data_percent.round(2)
        })
        print(missing_df.to_markdown(numalign="left", stralign="left"))
        
        # Visualization for missing data
        plt.figure(figsize=(10, 6))
        missing_data_percent.plot(kind='bar', color='#3b82f6')
        plt.title('Percentage of Missing Values per Column (Data Quality)', fontsize=14)
        plt.ylabel('Percentage Missing (%)', fontsize=12)
        plt.xlabel('Column Name', fontsize=12)
        plt.xticks(rotation=45, ha='right')
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()
        
        # Save Plot to the output directory
        plot_path = os.path.join(OUTPUT_DIR, "dqc_missing_values.png")
        plt.savefig(plot_path)
        print(f"Saved plot: {plot_path}")
        plt.close() # Close plot to prevent multiple windows from opening if running interactively
        


    # --- 2. Duplicate Check ---
    total_duplicates = df.duplicated().sum()
    print("\n--- 2. DATA QUALITY CHECK: DUPLICATE ROWS ---")
    print(f"Total Duplicate Rows Found: {total_duplicates}")

    # Check for duplicates in critical columns ('id', 'title', 'publishedAt')
    critical_duplicates = df.duplicated(subset=['id', 'title'], keep=False).sum()
    print(f"Total Rows with Duplicate 'id' or 'title': {critical_duplicates}")

    return missing_data

def run_exploratory_data_analysis(df):
    """Performs Exploratory Data Analysis (EDA) and generates visualizations."""
    
    print("\n--- EXPLORATORY DATA ANALYSIS (EDA) ---")

    # --- 1. Analysis of Numerical Metrics (Views, Likes, Comments) ---
    numerical_cols = ['viewCount', 'likeCount', 'commentCount', 'channel_subscriberCount']
    
    # Create histograms to see the distribution (often highly skewed)
    df[numerical_cols].hist(figsize=(15, 10), bins=50, color='#10b981', edgecolor='black', alpha=0.7)
    plt.suptitle('Distribution of Key Numerical Metrics (View, Like, Comment Counts)', y=1.02, fontsize=16)
    plt.tight_layout()
    
    # Save Plot
    plot_path = os.path.join(OUTPUT_DIR, "eda_numerical_distributions.png")
    plt.savefig(plot_path)
    print(f"Saved plot: {plot_path}")
    plt.close()

    # Use a log transformation for better visualization of highly skewed data
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle('Log-Transformed Distribution of Key Numerical Metrics', y=1.02, fontsize=16)
    
    for i, col in enumerate(numerical_cols):
        row = i // 2
        col_idx = i % 2
        # Use log1p (log(1+x)) to handle zero or near-zero values
        log_data = np.log1p(df[col])
        log_data.hist(ax=axes[row, col_idx], bins=50, color='#3b82f6', edgecolor='black', alpha=0.7)
        axes[row, col_idx].set_title(f'Log(1 + {col}) Distribution', fontsize=12)
        axes[row, col_idx].set_xlabel(f'Log(1 + {col})', fontsize=10)
        axes[row, col_idx].set_ylabel('Frequency', fontsize=10)

    plt.tight_layout()
    
    # Save Plot
    plot_path = os.path.join(OUTPUT_DIR, "eda_log_distributions.png")
    plt.savefig(plot_path)
    print(f"Saved plot: {plot_path}")
    plt.close()
    

    # --- 2. Analysis of Categorical Data (Categories and Channels) ---
    
    # Top 10 Channel Titles
    top_channels = df['channel_title'].value_counts().nlargest(10)
    plt.figure(figsize=(10, 6))
    top_channels.plot(kind='barh', color=sns.color_palette("viridis", 10))
    plt.title('Top 10 Most Frequent Channels', fontsize=14)
    plt.xlabel('Number of Videos', fontsize=12)
    plt.ylabel('Channel Title', fontsize=12)
    plt.gca().invert_yaxis() # Put highest count at the top
    plt.tight_layout()
    
    # Save Plot
    plot_path = os.path.join(OUTPUT_DIR, "eda_top_channels.png")
    plt.savefig(plot_path)
    print(f"Saved plot: {plot_path}")
    plt.close()
    

    # Top 10 Video Categories 
    top_categories = df['categoryId'].value_counts().nlargest(10)
    plt.figure(figsize=(10, 6))
    top_categories.plot(kind='bar', color=sns.color_palette("plasma", 10))
    plt.title('Top 10 Most Frequent Video Categories (by ID)', fontsize=14)
    plt.xlabel('Category ID', fontsize=12)
    plt.ylabel('Number of Videos', fontsize=12)
    plt.xticks(rotation=0)
    plt.tight_layout()
    
    # Save Plot
    plot_path = os.path.join(OUTPUT_DIR, "eda_top_categories.png")
    plt.savefig(plot_path)
    print(f"Saved plot: {plot_path}")
    plt.close()
    

    # --- 3. Correlation Matrix 
    
    # Calculate correlation matrix
    correlation_matrix = df[numerical_cols].corr()
    
    plt.figure(figsize=(8, 6))
    sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt=".2f", linewidths=.5, linecolor='black')
    plt.title('Correlation Matrix of Key Numerical Metrics', fontsize=14)
    plt.tight_layout()
    
    # Save Plot
    plot_path = os.path.join(OUTPUT_DIR, "eda_correlation_matrix.png")
    plt.savefig(plot_path)
    print(f"Saved plot: {plot_path}")
    plt.close()
    

    # --- 4. Time Series Analysis 
    
    df['publish_date'] = df['publishedAt'].dt.date
    daily_videos = df['publish_date'].value_counts().sort_index()
    
    plt.figure(figsize=(12, 6))
    daily_videos.plot(kind='line', marker='o', linestyle='-', color='#ef4444')
    plt.title('Video Publishing Trend Over Time', fontsize=14)
    plt.xlabel('Publish Date', fontsize=12)
    plt.ylabel('Number of Videos Published', fontsize=12)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    
    # Save Plot
    plot_path = os.path.join(OUTPUT_DIR, "eda_publishing_trend.png")
    plt.savefig(plot_path)
    print(f"Saved plot: {plot_path}")
    plt.close()


def generate_report(df, missing_data):
    """Generates a structured, human-readable report."""
    
    # Generate the full path for the report file
    report_path = os.path.join(OUTPUT_DIR, REPORT_FILENAME)
    print(f"\nWriting comprehensive report to {report_path}...")
    
    # Get descriptive stats for numerical data
    desc_stats = df[['viewCount', 'likeCount', 'commentCount', 'channel_subscriberCount']].describe().round(2)
    
    # Get top 3 categories and channels (Series objects)
    top_categories_series = df['categoryId'].value_counts().nlargest(3)
    top_channels_series = df['channel_title'].value_counts().nlargest(3)

    # Convert Series to DataFrame explicitly for reliable to_markdown formatting
    top_categories_df = top_categories_series.rename_axis('Category ID').to_frame('Count')
    top_channels_df = top_channels_series.rename_axis('Channel Name').to_frame('Video Count')

    report = [
        "==================================================",
        "          DATA QUALITY & EDA REPORT               ",
        "==================================================",
        f"\n1. DATA OVERVIEW",
        f"--------------------",
        f"Total Records: {len(df)}",
        f"Total Columns: {len(df.columns)}",
        f"Duplicate Rows (Exact Match): {df.duplicated().sum()}",
        f"Critical Duplicates ('id' or 'title'): {df.duplicated(subset=['id', 'title'], keep=False).sum()}",
        
        f"\n2. DATA QUALITY CHECK: MISSING VALUES",
        f"-----------------------------------",
        "Summary of columns with missing data (and percentage):",
    ]
    
    if missing_data.empty:
        report.append("-> No missing values found in any column! Excellent data quality.")
    else:
        missing_data_percent = (missing_data / len(df)) * 100
        for col, count in missing_data.items():
            report.append(f"-> {col}: {count} records ({missing_data_percent[col]:.2f}%)")
        report.append("Note: 'tags' and 'description' have the most missing values, which is common in web scraping.")

    report.extend([
        f"\n3. EXPLORATORY DATA ANALYSIS (EDA): NUMERICAL METRICS",
        f"----------------------------------------------------",
        "The distribution of views, likes, and comments is highly skewed (most videos have low counts, a few are viral).",
        "\n--- Descriptive Statistics ---",
        desc_stats.to_markdown(numalign="left", stralign="left"),
        
        f"\nKey Insights from Numerical Metrics:",
        f"-> View Count Range: {df['viewCount'].min()} to {df['viewCount'].max()}",
        f"-> Average Like Count: {desc_stats.loc['mean', 'likeCount']}",
        f"-> Max Subscriber Count: {df['channel_subscriberCount'].max()} (indicating high-profile channels are included).",

        f"\n4. EDA: CATEGORICAL TRENDS",
        f"-----------------------------",
        "\n--- Top 3 Most Frequent Categories (by ID) ---",
        top_categories_df.to_markdown(numalign="left", stralign="left"),
        "Note: Category IDs need an external lookup table for human-readable names.",
        
        f"\n--- Top 3 Most Frequent Publishing Channels ---",
        top_channels_df.to_markdown(numalign="left", stralign="left"),
        "These channels dominate the dataset's video volume.",
        
        f"\n5. CONCLUSION & NEXT STEPS",
        f"-----------------------------",
        "The data is generally high quality, but requires imputation or dropping rows for 'tags', 'description', 'defaultLanguage', 'defaultAudioLanguage', and 'channel_country' before model training.",
        "The numerical data is highly skewed, suggesting log-transformation will be necessary for regression models.",
        "The dataset is dominated by a few large channels and categories, which should be considered in any subsequent analysis."
    ])
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report))
        
    print(f"\nReport saved successfully to {report_path}")
    print("--------------------------------------------------")
    print("ANALYSIS COMPLETE. Check the generated report and visualizations.")


# --- Main Execution Block ---
if __name__ == "__main__":
    
    # 0. Create Output Directory
    create_output_directory(OUTPUT_DIR)
    
    # Set a cleaner style for plots
    sns.set_style("whitegrid")
    
    # 1. Load Data
    data = load_and_prepare_data(FILE_PATH)
    
    if data is not None:
        # 2. Data Quality Check
        missing_info = run_data_quality_check(data)
        
        # 3. Exploratory Data Analysis (Visualizations)
        # Note: All plots are now saved to the OUTPUT_DIR instead of showing with plt.show()
        run_exploratory_data_analysis(data)
        
        # 4. Generate Final Report
        generate_report(data, missing_info)
    else:
        print("\nFailed to proceed with analysis due to data loading error.")

# import pandas as pd
# import matplotlib.pyplot as plt
# import seaborn as sns
# import numpy as np

# # --- Configuration ---
# FILE_PATH = r"C:\Users\dream\Desktop\Internships\Infosys Springboard\QueryTube\task1_master_dataset.csv" 
# REPORT_FILENAME = "data_quality_and_eda_report.txt"

# def load_and_prepare_data(file_path):
#     """Loads the dataset and performs initial data type conversions."""
#     print(f"Loading data from: {file_path}")
#     try:
#         df = pd.read_csv(file_path)
#     except FileNotFoundError:
#         print(f"ERROR: File not found at {file_path}. Please ensure the CSV file is in the same directory as this script.")
#         return None
#     # Rename the first column for clarity
#     if 'Unnamed: 0' in df.columns:
#         df = df.rename(columns={'Unnamed: 0': 'index_col'})
    
#     # Convert 'publishedAt' to datetime object
#     df['publishedAt'] = pd.to_datetime(df['publishedAt'], errors='coerce')
    
#     # Convert large number columns to numeric (in case of subtle string representations)
#     for col in ['viewCount', 'likeCount', 'commentCount', 'channel_subscriberCount', 'channel_videoCount']:
#         # Ensure they are numeric, forcing non-convertible values to NaN (though they appear to be int64 already)
#         df[col] = pd.to_numeric(df[col], errors='coerce')

#     print("Data loaded and initial preparation complete.\n")
#     return df

# def run_data_quality_check(df):
#     """Performs Data Quality Checks (Missing values, Duplicates, Unique values)."""
    
#     # --- 1. Missing Values Analysis ---
#     print("--- 1. DATA QUALITY CHECK: MISSING VALUES ---")
    
#     missing_data = df.isnull().sum().sort_values(ascending=False)
#     missing_data = missing_data[missing_data > 0]
    
#     if missing_data.empty:
#         print("Great! No missing values found in the entire dataset.")
#     else:
#         missing_data_percent = (missing_data / len(df)) * 100
#         missing_df = pd.DataFrame({
#             'Missing Count': missing_data,
#             'Percentage (%)': missing_data_percent.round(2)
#         })
#         print(missing_df.to_markdown(numalign="left", stralign="left"))
        
#         # Visualization for missing data
#         plt.figure(figsize=(10, 6))
#         missing_data_percent.plot(kind='bar', color='#3b82f6')
#         plt.title('Percentage of Missing Values per Column (Data Quality)', fontsize=14)
#         plt.ylabel('Percentage Missing (%)', fontsize=12)
#         plt.xlabel('Column Name', fontsize=12)
#         plt.xticks(rotation=45, ha='right')
#         plt.grid(axis='y', linestyle='--', alpha=0.7)
#         plt.tight_layout()
#         plt.show()
        


#     # --- 2. Duplicate Check ---
#     total_duplicates = df.duplicated().sum()
#     print("\n--- 2. DATA QUALITY CHECK: DUPLICATE ROWS ---")
#     print(f"Total Duplicate Rows Found: {total_duplicates}")

#     # Check for duplicates in critical columns ('id', 'title', 'publishedAt')
#     critical_duplicates = df.duplicated(subset=['id', 'title'], keep=False).sum()
#     print(f"Total Rows with Duplicate 'id' or 'title': {critical_duplicates}")

#     return missing_data

# def run_exploratory_data_analysis(df):
#     """Performs Exploratory Data Analysis (EDA) and generates visualizations."""
    
#     print("\n--- EXPLORATORY DATA ANALYSIS (EDA) ---")

#     # --- 1. Analysis of Numerical Metrics (Views, Likes, Comments) ---
#     numerical_cols = ['viewCount', 'likeCount', 'commentCount', 'channel_subscriberCount']
    
#     # Create histograms to see the distribution (often highly skewed)
#     df[numerical_cols].hist(figsize=(15, 10), bins=50, color='#10b981', edgecolor='black', alpha=0.7)
#     plt.suptitle('Distribution of Key Numerical Metrics (View, Like, Comment Counts)', y=1.02, fontsize=16)
#     plt.tight_layout()
#     plt.show()
    

#     # Use a log transformation for better visualization of highly skewed data
#     fig, axes = plt.subplots(2, 2, figsize=(15, 10))
#     fig.suptitle('Log-Transformed Distribution of Key Numerical Metrics', y=1.02, fontsize=16)
    
#     for i, col in enumerate(numerical_cols):
#         row = i // 2
#         col_idx = i % 2
#         # Use log1p (log(1+x)) to handle zero or near-zero values
#         log_data = np.log1p(df[col])
#         log_data.hist(ax=axes[row, col_idx], bins=50, color='#3b82f6', edgecolor='black', alpha=0.7)
#         axes[row, col_idx].set_title(f'Log(1 + {col}) Distribution', fontsize=12)
#         axes[row, col_idx].set_xlabel(f'Log(1 + {col})', fontsize=10)
#         axes[row, col_idx].set_ylabel('Frequency', fontsize=10)

#     plt.tight_layout()
#     plt.show()
    

#     # --- 2. Analysis of Categorical Data (Categories and Channels) ---
    
#     # Top 10 Channel Titles
#     top_channels = df['channel_title'].value_counts().nlargest(10)
#     plt.figure(figsize=(10, 6))
#     top_channels.plot(kind='barh', color=sns.color_palette("viridis", 10))
#     plt.title('Top 10 Most Frequent Channels', fontsize=14)
#     plt.xlabel('Number of Videos', fontsize=12)
#     plt.ylabel('Channel Title', fontsize=12)
#     plt.gca().invert_yaxis() # Put highest count at the top
#     plt.tight_layout()
#     plt.show()
    

#     # Top 10 Video Categories (categoryId needs mapping for meaningful EDA, but we'll show raw count for now)
#     top_categories = df['categoryId'].value_counts().nlargest(10)
#     plt.figure(figsize=(10, 6))
#     top_categories.plot(kind='bar', color=sns.color_palette("plasma", 10))
#     plt.title('Top 10 Most Frequent Video Categories (by ID)', fontsize=14)
#     plt.xlabel('Category ID', fontsize=12)
#     plt.ylabel('Number of Videos', fontsize=12)
#     plt.xticks(rotation=0)
#     plt.tight_layout()
#     plt.show()
    

#     # --- 3. Correlation Matrix (Optional, for numerical relationship check) ---
    
#     # Calculate correlation matrix
#     correlation_matrix = df[numerical_cols].corr()
    
#     plt.figure(figsize=(8, 6))
#     sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt=".2f", linewidths=.5, linecolor='black')
#     plt.title('Correlation Matrix of Key Numerical Metrics', fontsize=14)
#     plt.tight_layout()
#     plt.show()
    

#     # --- 4. Time Series Analysis (Optional, to see publishing trend) ---
    
#     df['publish_date'] = df['publishedAt'].dt.date
#     daily_videos = df['publish_date'].value_counts().sort_index()
    
#     plt.figure(figsize=(12, 6))
#     daily_videos.plot(kind='line', marker='o', linestyle='-', color='#ef4444')
#     plt.title('Video Publishing Trend Over Time', fontsize=14)
#     plt.xlabel('Publish Date', fontsize=12)
#     plt.ylabel('Number of Videos Published', fontsize=12)
#     plt.grid(axis='y', linestyle='--', alpha=0.7)
#     plt.tight_layout()
#     plt.show()
    


# def generate_report(df, missing_data):
#     """Generates a structured, human-readable report."""
    
#     print(f"\nWriting comprehensive report to {REPORT_FILENAME}...")
    
#     # Get descriptive stats for numerical data
#     desc_stats = df[['viewCount', 'likeCount', 'commentCount', 'channel_subscriberCount']].describe().round(2)
    
#     # Get top 3 categories and channels
#     top_categories_raw = df['categoryId'].value_counts().nlargest(3)
#     top_channels_raw = df['channel_title'].value_counts().nlargest(3)

#     report = [
#         "==================================================",
#         "          DATA QUALITY & EDA REPORT               ",
#         "==================================================",
#         f"\n1. DATA OVERVIEW",
#         f"--------------------",
#         f"Total Records: {len(df)}",
#         f"Total Columns: {len(df.columns)}",
#         f"Duplicate Rows (Exact Match): {df.duplicated().sum()}",
#         f"Critical Duplicates ('id' or 'title'): {df.duplicated(subset=['id', 'title'], keep=False).sum()}",
        
#         f"\n2. DATA QUALITY CHECK: MISSING VALUES",
#         f"-----------------------------------",
#         "Summary of columns with missing data (and percentage):",
#     ]
    
#     if missing_data.empty:
#         report.append("-> No missing values found in any column! Excellent data quality.")
#     else:
#         missing_data_percent = (missing_data / len(df)) * 100
#         for col, count in missing_data.items():
#             report.append(f"-> {col}: {count} records ({missing_data_percent[col]:.2f}%)")
#         report.append("Note: 'tags' and 'description' have the most missing values, which is common in web scraping.")

#     report.extend([
#         f"\n3. EXPLORATORY DATA ANALYSIS (EDA): NUMERICAL METRICS",
#         f"----------------------------------------------------",
#         "The distribution of views, likes, and comments is highly skewed (most videos have low counts, a few are viral).",
#         "\n--- Descriptive Statistics ---",
#         desc_stats.to_markdown(numalign="left", stralign="left"),
        
#         f"\nKey Insights from Numerical Metrics:",
#         f"-> View Count Range: {df['viewCount'].min()} to {df['viewCount'].max()}",
#         f"-> Average Like Count: {desc_stats.loc['mean', 'likeCount']}",
#         f"-> Max Subscriber Count: {df['channel_subscriberCount'].max()} (indicating high-profile channels are included).",

#         f"\n4. EDA: CATEGORICAL TRENDS",
#         f"-----------------------------",
#         "\n--- Top 3 Most Frequent Categories (by ID) ---",
#         top_categories_raw.to_markdown(header=['Category ID', 'Count'], numalign="left", stralign="left"),
#         "Note: Category IDs need an external lookup table for human-readable names.",
        
#         f"\n--- Top 3 Most Frequent Publishing Channels ---",
#         top_channels_raw.to_markdown(header=['Channel Name', 'Video Count'], numalign="left", stralign="left"),
#         "These channels dominate the dataset's video volume.",
        
#         f"\n5. CONCLUSION & NEXT STEPS",
#         f"-----------------------------",
#         "The data is generally high quality, but requires imputation or dropping rows for 'tags', 'description', 'defaultLanguage', 'defaultAudioLanguage', and 'channel_country' before model training.",
#         "The numerical data is highly skewed, suggesting log-transformation will be necessary for regression models.",
#         "The dataset is dominated by a few large channels and categories, which should be considered in any subsequent analysis."
#     ])
    
#     with open(REPORT_FILENAME, 'w', encoding='utf-8') as f:
#         f.write('\n'.join(report))
        
#     print(f"\nReport saved successfully to {REPORT_FILENAME}")
#     print("--------------------------------------------------")
#     print("ANALYSIS COMPLETE. Check the generated report and visualizations.")


# # --- Main Execution Block ---
# if __name__ == "__main__":
    
#     # Set a cleaner style for plots
#     sns.set_style("whitegrid")
    
#     # 1. Load Data
#     data = load_and_prepare_data(FILE_PATH)
    
#     if data is not None:
#         # 2. Data Quality Check
#         missing_info = run_data_quality_check(data)
        
#         # 3. Exploratory Data Analysis (Visualizations)
#         run_exploratory_data_analysis(data)
        
#         # 4. Generate Final Report
#         generate_report(data, missing_info)
#     else:
#         print("\nFailed to proceed with analysis due to data loading error.")
