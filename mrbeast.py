import yt_dlp
import webvtt
import pandas as pd
import re
import time
import os
from datetime import datetime, timedelta

def get_all_channel_videos(channel_name):
    """Fetch ALL video URLs from a channel by paginated searches."""
    all_videos = []
    max_per_search = 50  # Safe batch size
    search_count = 0
    oldest_date = None  # For pagination via date filters

    while True:
        search_count += 1
        # Base search
        base_query = f"ytsearch{max_per_search}:from:{channel_name}"
        if oldest_date:
            # Filter older videos for pagination
            date_str = oldest_date.strftime('%Y-%m-%d')
            query = f"{base_query} before:{date_str}"
        else:
            query = base_query

        try:
            ydl_opts = {
                'quiet': True,
                'extract_flat': True,
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                result = ydl.extract_info(query, download=False)
                new_videos = [
                    {
                        'video_id': entry['id'],
                        'url': f"https://www.youtube.com/watch?v={entry['id']}",
                        'title': entry['title'],
                        'upload_date': entry.get('upload_date', '')  # YYYYMMDD for sorting
                    }
                    for entry in result.get('entries', [])
                ]
                if not new_videos:
                    break  # No more videos
                all_videos.extend(new_videos)
                print(f"Search {search_count}: Fetched {len(new_videos)} videos (total: {len(all_videos)})")
                
                # Update oldest date for next pagination (subtract 1 day from oldest)
                if new_videos:
                    oldest_upload = min(entry.get('upload_date', '99991231') for entry in new_videos)
                    oldest_date = datetime.strptime(oldest_upload, '%Y%m%d') - timedelta(days=1)
                
                if len(new_videos) < max_per_search:
                    break  # End of videos
                time.sleep(2)  # Delay between searches
        except Exception as e:
            print(f"Error in search {search_count}: {e}")
            break

    # Sort by upload date (newest first) and remove duplicates
    all_videos = list({v['video_id']: v for v in all_videos}.values())
    all_videos.sort(key=lambda x: x.get('upload_date', '99991231'), reverse=True)
    print(f"Total unique videos found: {len(all_videos)}")
    return all_videos

def download_metadata_and_subtitles(url, video_id, output_name):
    """Download subtitles, description, and other metadata using yt-dlp."""
    ydl_opts = {
        'writeautomaticsub': True,
        'skip_download': True,
        'outtmpl': output_name,
        'quiet': False,
        'get_title': True,
        'get_uploader': True,
        'get_description': True,  # New: Fetch video description
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            subtitle_file = f"{output_name}.en.vtt"
            title = info.get('title', 'Unknown Title')
            channel = info.get('uploader', 'Unknown Channel')
            description = info.get('description', 'No description available')  # New
            return subtitle_file, title, channel, description
    except Exception as e:
        print(f"Error downloading for {url}: {e}")
        return None, None, None, None

def clean_text(text):
    """Clean text (transcript or description) by removing tags and excess whitespace."""
    # Remove [Music], [Applause], etc.
    text = re.sub(r'\[.*?\]', '', text)
    # Remove extra newlines and spaces
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def vtt_to_transcript(vtt_file):
    """Convert VTT subtitles to a single, cleaned transcript string."""
    try:
        full_text = ' '.join(caption.text for caption in webvtt.read(vtt_file))
        # Deduplicate consecutive words
        words = full_text.split()
        cleaned_words = []
        prev_word = None
        for word in words:
            if word != prev_word:
                cleaned_words.append(word)
                prev_word = word
        cleaned_text = ' '.join(cleaned_words)
        return clean_text(cleaned_text)
    except Exception as e:
        print(f"Error parsing VTT {vtt_file}: {e}")
        return None

def get_existing_video_ids(csv_file='transcripts.csv'):
    """Get set of existing video_ids from CSV."""
    if os.path.exists(csv_file):
        try:
            df = pd.read_csv(csv_file)
            return set(df['video_id'].astype(str))
        except Exception as e:
            print(f"Error reading existing CSV: {e}")
    return set()

def save_to_csv(data, csv_file='transcripts.csv', existing_ids=None):
    """Append new data to CSV."""
    if not data:
        return
    new_df = pd.DataFrame(data)
    if existing_ids:
        # Append to existing
        existing_df = pd.read_csv(csv_file) if os.path.exists(csv_file) else pd.DataFrame()
        combined_df = pd.concat([existing_df, new_df], ignore_index=True)
    else:
        combined_df = new_df
    combined_df.to_csv(csv_file, index=False, encoding='utf-8')
    print(f"Updated {csv_file} with {len(data)} new videos (total rows: {len(combined_df)}).")

def main():
    """Main function: Incremental processing of all videos from a channel."""
    channel_name = input("Enter YouTube channel name (e.g., Beast Philanthropy): ").strip()
    if not channel_name:
        print("No channel name. Exiting.")
        return

    existing_ids = get_existing_video_ids()
    print(f"Existing videos in CSV: {len(existing_ids)}")

    # Fetch all videos
    videos = get_all_channel_videos(channel_name)
    if not videos:
        print(f"No videos found for '{channel_name}'. Try 'Beast Philanthropy'.")
        return

    new_videos = [v for v in videos if v['video_id'] not in existing_ids]
    print(f"New videos to process: {len(new_videos)} (skipping {len(videos) - len(new_videos)} duplicates)")

    data = []
    for i, video in enumerate(new_videos):
        video_id = video['video_id']
        url = video['url']
        print(f"Processing new video {i+1}/{len(new_videos)}: {url} ({video['title']})")
        
        subtitle_file, title, channel, description = download_metadata_and_subtitles(url, video_id, f"subtitles_{video_id}")
        if subtitle_file and title and channel:
            transcript = vtt_to_transcript(subtitle_file)
            cleaned_description = clean_text(description)
            if transcript:  # Require transcript for addition
                data.append({
                    'video_id': video_id,
                    'video_title': title,
                    'channel_name': channel,
                    'full_transcript': transcript,
                    'video_description': cleaned_description  # New column
                })
                print(f"Added: {title}")
                # Cleanup
                try:
                    os.remove(subtitle_file)
                except:
                    pass
            else:
                print(f"Skipped {url} (no transcript)")
        else:
            print(f"Failed for {url}")
        
        time.sleep(5)  # Rate limit

    if data:
        save_to_csv(data, existing_ids=bool(existing_ids))
    else:
        print("No new videos added (all had no transcripts or already processed).")

if __name__ == "__main__":
    main()
