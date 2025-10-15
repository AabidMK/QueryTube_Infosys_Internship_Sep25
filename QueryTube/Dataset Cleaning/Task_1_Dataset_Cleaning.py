import pandas as pd
import numpy as np
import re
import html
import unicodedata
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

def complete_video_data_cleaning():
    """
    COMPLETE Video Data Cleaning - ALL 6 Requirements + Duration Conversion

    1. Remove Emojis
    2. Remove Special characters (#, @, |, [], etc.)
    3. Remove HTML tags (<br>, <i>)
    4. Convert to lowercase
    5. Strip extra whitespace
    6. Ensure title uniqueness: check for duplicates across video_id
    7: Convert duration from PT format to seconds (replaces existing column)
    """

    print(" COMPLETE VIDEO DATA CLEANING + DURATION CONVERSION")


    # =====================================================
    # LOAD DATA
    # =====================================================
    print("\n Loading master dataset...")

    # Try to load original dataset first, fallback to cleaned version
    try:
        df = pd.read_csv(r'C:\Users\dream\Desktop\Internships\Infosys Springboard\QueryTube\task1_master_dataset.csv')
        print(f"Original dataset loaded: {df.shape}")
    except FileNotFoundError:
        try:
            df = pd.read_csv('cleaned_Master_dataset_Task_1_20250929_120319.csv')
            print(f"Previously cleaned dataset loaded: {df.shape}")
        except FileNotFoundError:
            print("No dataset found!")
            return None

    # Show sample before cleaning
    print("\nBEFORE CLEANING (Sample titles):")
    for i in range(min(3, len(df))):
        print(f"  {i+1}. {df.iloc[i]['title']}")

    # Show sample durations
    if 'duration' in df.columns:
        print("\n BEFORE DURATION CONVERSION (Samples):")
        for i in range(min(5, len(df))):
            duration = df.iloc[i]['duration']
            print(f"  {i+1}. {duration}")

    # =====================================================
    # BONUS: CONVERT DURATION TO SECONDS (REPLACE COLUMN)
    # =====================================================
    print("\n\n BONUS: Converting Duration to Seconds (Replacing Column)")
    print("-" * 60)

    def convert_duration_to_seconds(duration_str):
        """
        Convert YouTube duration format (PT1M17S) to seconds
        Examples:
        - PT1M17S -> 77 seconds (1*60 + 17)
        - PT30S -> 30 seconds
        - PT2M -> 120 seconds
        - PT1H30M45S -> 5445 seconds (1*3600 + 30*60 + 45)
        """
        if pd.isna(duration_str) or not duration_str:
            return np.nan

        duration_str = str(duration_str).strip()

        # Check if it's already in seconds (just a number)
        if duration_str.isdigit():
            return int(duration_str)

        # Check if it's in PT format
        if not duration_str.startswith('PT'):
            return np.nan  # Invalid format

        # Remove 'PT' prefix
        duration_str = duration_str[2:]

        total_seconds = 0

        # Extract hours (H)
        hours_match = re.search(r'(\d+)H', duration_str)
        if hours_match:
            total_seconds += int(hours_match.group(1)) * 3600

        # Extract minutes (M)
        minutes_match = re.search(r'(\d+)M', duration_str)
        if minutes_match:
            total_seconds += int(minutes_match.group(1)) * 60

        # Extract seconds (S)
        seconds_match = re.search(r'(\d+)S', duration_str)
        if seconds_match:
            total_seconds += int(seconds_match.group(1))

        return total_seconds

    # Apply duration conversion and replace the column
    if 'duration' in df.columns:
        print("Converting duration from PT format to seconds and replacing column...")

        # Show some before conversions
        print("\n SAMPLE CONVERSIONS:")
        sample_durations = df['duration'].head(10)
        for idx, duration in enumerate(sample_durations, 1):
            converted = convert_duration_to_seconds(duration)
            print(f"  {idx:2d}. {duration:12} -> {converted:4.0f} seconds")

        # Convert and replace the duration column
        df['duration'] = df['duration'].apply(convert_duration_to_seconds)

        # Statistics
        print(f"\n DURATION CONVERSION STATISTICS:")
        print(f"  Total records: {len(df)}")
        print(f"  Successfully converted: {df['duration'].notna().sum()}")
        print(f"  Failed conversions: {df['duration'].isna().sum()}")
        print(f"  Average duration: {df['duration'].mean():.1f} seconds")
        print(f"  Min duration: {df['duration'].min():.0f} seconds")
        print(f"  Max duration: {df['duration'].max():.0f} seconds")

        print(" Duration column converted to seconds (PT format replaced)")
    else:
        print(" No duration column found in dataset")

    # =====================================================
    # REQUIREMENT 1: REMOVE EMOJIS
    # =====================================================
    print("\n\n REQUIREMENT 1: Removing Emojis")
    print("-" * 50)

    def remove_emojis(text):
        if pd.isna(text):
            return text

        # Comprehensive emoji removal
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map
            "\U0001F1E0-\U0001F1FF"  # flags
            "\U00002702-\U000027B0"  # dingbats
            "\U000024C2-\U0001F251"  # enclosed characters
            "\U0001f926-\U0001f937"  # hand gestures
            "\U00010000-\U0010ffff"  # supplementary
            "\u2640-\u2642"           # gender symbols
            "\u2600-\u2B55"           # misc symbols
            "\u200d"                   # zero width joiner
            "\u23cf"                   # eject button
            "\u23e9"                   # fast forward
            "\u231a"                   # watch
            "\ufe0f"                   # variation selector
            "\u3030"                   # wavy dash
            "\U0001F900-\U0001F9FF"  # supplemental symbols
            "]+",
            flags=re.UNICODE
        )

        # Also remove by Unicode categories (additional safety)
        text = emoji_pattern.sub('', str(text))

        # Remove control characters that look like emojis
        text = re.sub(r'[\x80-\x9F]', '', text)

        return text

    # Apply to text columns
    text_columns = ['title', 'description', 'channel_title', 'channel_description']

    for col in text_columns:
        if col in df.columns:
            df[col] = df[col].apply(remove_emojis)

    print(" Emojis removed from all text columns")

    # =====================================================
    # REQUIREMENT 2: REMOVE SPECIAL CHARACTERS
    # =====================================================
    print("\n\n REQUIREMENT 2: Removing Special Characters")
    print("-" * 50)

    def remove_special_characters(text):
        if pd.isna(text):
            return text

        text = str(text)

        # Remove specific special characters: #, @, |, [], {}, *, &, %, $, ^, +, =, ~, `, <>
        special_chars = re.compile(r'[#@|\[\]{}*&%$^+=~`<>]')
        text = special_chars.sub(' ', text)

        # Remove additional symbols
        text = re.sub(r'[©®™§¶†‡°•·▶▪◦‣⁃]', ' ', text)

        # Remove currency and math symbols
        text = re.sub(r'[¤¥£€¢₹±²³¹∞≤≥≠×÷√]', ' ', text)

        # Handle quotation marks and dashes
        text = re.sub(r'[""''«»‚„‹›]', '"', text)
        text = re.sub(r'[–—−‒―]', '-', text)

        # Handle ellipsis
        text = re.sub(r'[…⋯]', '...', text)

        # Remove arrows
        text = re.sub(r'[→←↑↓➜➡⬅⬆⬇]', ' ', text)

        # Remove fractions
        text = re.sub(r'[¼½¾⅓⅔⅕⅖⅗⅘⅙⅚⅛⅜⅝⅞]', ' ', text)

        return text

    for col in text_columns:
        if col in df.columns:
            df[col] = df[col].apply(remove_special_characters)

    print(" Special characters (#, @, |, [], etc.) removed")

    # =====================================================
    # REQUIREMENT 3: REMOVE HTML TAGS
    # =====================================================
    print("\n\nREQUIREMENT 3: Removing HTML Tags")
    print("-" * 50)

    def remove_html_tags(text):
        if pd.isna(text):
            return text

        text = str(text)

        # Decode HTML entities first
        text = html.unescape(text)

        # Remove HTML tags
        html_pattern = re.compile(r'<[^>]+>')
        text = html_pattern.sub(' ', text)

        # Remove specific HTML entities
        text = text.replace('&nbsp;', ' ')
        text = text.replace('&amp;', '&')
        text = text.replace('&lt;', '<')
        text = text.replace('&gt;', '>')
        text = text.replace('&quot;', '"')
        text = text.replace('&#39;', "'")

        return text

    for col in text_columns:
        if col in df.columns:
            df[col] = df[col].apply(remove_html_tags)

    print(" HTML tags (<br>, <i>, etc.) and entities removed")

    # =====================================================
    # REQUIREMENT 4: CONVERT TO LOWERCASE
    # =====================================================
    print("\n\n REQUIREMENT 4: Converting to Lowercase")
    print("-" * 50)

    for col in text_columns:
        if col in df.columns:
            df[col] = df[col].apply(lambda x: str(x).lower() if pd.notna(x) else x)

    print(" All text converted to lowercase (title, description, channel_title, channel_description)")

    # =====================================================
    # REQUIREMENT 5: STRIP EXTRA WHITESPACE
    # =====================================================
    print("\n\n REQUIREMENT 5: Stripping Extra Whitespace")
    print("-" * 50)

    def normalize_whitespace(text):
        if pd.isna(text):
            return text

        text = str(text)

        # Replace multiple whitespace with single space
        text = re.sub(r'\s+', ' ', text)

        # Strip leading and trailing whitespace
        text = text.strip()

        # Return NaN if empty after cleaning
        return text if text else np.nan

    for col in text_columns:
        if col in df.columns:
            df[col] = df[col].apply(normalize_whitespace)

    print("Extra whitespace stripped and normalized")
    # Convert publishedAt to desired format (YYYY-MM-DD HH:MM:SS)
    if 'publishedAt' in df.columns:
        df['publishedAt'] = pd.to_datetime(df['publishedAt'], format='%Y-%m-%dT%H:%M:%SZ', errors='coerce')
        df['publishedAt'] = df['publishedAt'].dt.strftime('%Y-%m-%d %H:%M:%S')
        print("publishedAt column converted to 'YYYY-MM-DD HH:MM:SS' format.")


    # =====================================================
    # REQUIREMENT 6: ENSURE TITLE UNIQUENESS
    # =====================================================
    print("\n\nREQUIREMENT 6: Checking Title Uniqueness")
    print("-" * 50)

    if 'title' in df.columns:
        # Check for duplicate titles
        duplicate_titles = df.duplicated(subset=['title']).sum()
        unique_titles = df['title'].nunique()
        total_records = len(df)

        print(f"Total records: {total_records}")
        print(f"Unique titles: {unique_titles}")
        print(f"Duplicate titles: {duplicate_titles}")

        if duplicate_titles > 0:
            print("\nFound duplicate titles:")
            duplicates = df[df.duplicated(subset=['title'], keep=False)][['id', 'title']]
            for idx, (_, row) in enumerate(duplicates.iterrows()):
                if idx < 5:  # Show first 5
                    print(f"  • Video ID: {row['id']} | Title: {row['title'][:50]}...")
            if len(duplicates) > 5:
                print(f"  ... and {len(duplicates) - 5} more")
        else:
            print(" All titles are unique across video_id")

        # Check video_id uniqueness
        if 'id' in df.columns:
            duplicate_ids = df.duplicated(subset=['id']).sum()
            print(f"\nDuplicate video IDs: {duplicate_ids}")

            if duplicate_ids == 0:
                print(" All video IDs are unique")
            else:
                print(" Warning: Duplicate video IDs found")

    # =====================================================
    # HANDLE ACCENTED CHARACTERS (BONUS)
    # =====================================================
    print("\n\nBONUS: Normalizing Accented Characters")
    print("-" * 50)

    def normalize_accents(text):
        if pd.isna(text):
            return text

        # Convert accented characters to ASCII equivalents
        text = str(text)
        text = unicodedata.normalize('NFKD', text)
        text = ''.join(c for c in text if unicodedata.category(c) != 'Mn')

        # Remove any remaining non-ASCII characters
        text = re.sub(r'[^\x00-\x7F]', '', text)

        return text

    for col in text_columns:
        if col in df.columns:
            df[col] = df[col].apply(normalize_accents)

    print(" Accented characters normalized to ASCII")

    # =====================================================
    # SPECIAL HANDLING FOR TAGS
    # =====================================================
    print("\n\n SPECIAL: Tags Column Handling")
    print("-" * 50)

    if 'tags' in df.columns:
        def clean_tags_preserve_structure(tags_text):
            if pd.isna(tags_text):
                return tags_text

            # Split by pipe, clean each tag, rejoin
            if '|' in str(tags_text):
                tags = str(tags_text).split('|')
                cleaned_tags = []

                for tag in tags:
                    # Apply all cleaning steps to each tag
                    cleaned_tag = remove_emojis(tag)
                    cleaned_tag = remove_special_characters(cleaned_tag)
                    cleaned_tag = remove_html_tags(cleaned_tag)
                    cleaned_tag = cleaned_tag.lower() if pd.notna(cleaned_tag) else cleaned_tag
                    cleaned_tag = normalize_whitespace(cleaned_tag)
                    cleaned_tag = normalize_accents(cleaned_tag)

                    if cleaned_tag and cleaned_tag.strip():
                        cleaned_tags.append(cleaned_tag.strip())

                return '|'.join(cleaned_tags) if cleaned_tags else np.nan
            else:
                # Single tag or no pipes
                cleaned = remove_emojis(tags_text)
                cleaned = remove_special_characters(cleaned)
                cleaned = remove_html_tags(cleaned)
                cleaned = cleaned.lower() if pd.notna(cleaned) else cleaned
                cleaned = normalize_whitespace(cleaned)
                cleaned = normalize_accents(cleaned)
                return cleaned

        df['tags'] = df['tags'].apply(clean_tags_preserve_structure)
        print(" Tags cleaned while preserving pipe structure")

    # =====================================================
    # FINAL VALIDATION & RESULTS
    # =====================================================
    print("\n\n FINAL VALIDATION & RESULTS")
    print("-" * 50)

    # Show final samples
    print("\nAFTER COMPLETE CLEANING (Sample titles):")
    for i in range(min(5, len(df))):
        print(f"  {i+1}. {df.iloc[i]['title']}")

    # Show final duration samples
    if 'duration' in df.columns:
        print("\n FINAL DURATION VALUES (in seconds):")
        for i in range(min(5, len(df))):
            duration = df.iloc[i]['duration']
            print(f"  {i+1}. {duration:.0f} seconds")

    # Final character analysis
    if 'title' in df.columns:
        sample_text = ' '.join(df['title'].dropna().astype(str))
        ascii_chars = sum(1 for c in sample_text if ord(c) <= 127)
        non_ascii_chars = sum(1 for c in sample_text if ord(c) > 127)
        total_chars = len(sample_text)

        print(f"\nTEXT PURITY ANALYSIS:")
        print(f"  ASCII characters: {ascii_chars:,} ({(ascii_chars/total_chars)*100:.2f}%)")
        print(f"  Non-ASCII characters: {non_ascii_chars:,} ({(non_ascii_chars/total_chars)*100:.2f}%)")

        if non_ascii_chars == 0:
            print("100% ASCII text achieved!")
        else:
            print(f" {non_ascii_chars} non-ASCII characters remaining")

    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f'Task_1_cleaned_dataset_.csv'
    df.to_csv(output_filename, index=False)

    print(f"\nCOMPLETE CLEANED DATASET SAVED:")
    print(f"   File: {output_filename}")

    # Final summary
    print("\n" + "=" * 70)
    print(" ALL 6 REQUIREMENTS + DURATION CONVERSION COMPLETED!")
    print("=" * 70)
    print("1. Emojis removed")
    print("2. Special characters removed")
    print("3. HTML tags removed")
    print("4. Text converted to lowercase")
    print("5. Extra whitespace stripped")
    print("6. Title uniqueness verified")
    print("\n BONUS FEATURES:")
    print("Duration converted from PT format to seconds (column replaced)")
    print("Accented characters normalized to ASCII")
    print("Tags structure preserved")
    print("\n Your dataset is now 100% ready for analysis!")

    return df

# Execute the complete cleaning
if __name__ == "__main__":
    cleaned_df = complete_video_data_cleaning()
