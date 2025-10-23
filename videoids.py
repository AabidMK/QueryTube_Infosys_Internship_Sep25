import requests
import csv
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound

# ===============================
# CONFIG
# ===============================
API_KEY = "AIzaSyBpRhcG-u0Thu6oe0meBftBPLxJiN_gga4"   # Replace with your YouTube API Key
CHANNEL_ID = "UCJskGeByzRRSvmOyZOz61ig"     # Replace with your target channel ID
CSV_FILE = "youtube_transcripts (2).csv"

BASE_URL = "https://www.googleapis.com/youtube/v3"

# ===============================
# Step 1: Get video IDs from channel
# ===============================
def get_video_ids(api_key, channel_id, max_results=50):
    url = f"{BASE_URL}/search"
    params = {
        "part": "snippet",
        "channelId": channel_id,
        "maxResults": max_results,
        "order": "date",
        "type": "video",
        "key": api_key
    }
    response = requests.get(url, params=params)
    data = response.json()

    video_data = []
    for item in data.get("items", []):
        video_id = item["id"]["videoId"]
        title = item["snippet"]["title"]
        video_data.append((video_id, title))
    return video_data

# ===============================
# Step 2: Fetch transcript
# ===============================
def fetch_transcript(video_id, languages=None):
    ytt_api = YouTubeTranscriptApi()
    try:
        if languages:
            fetched = ytt_api.fetch(video_id, languages=languages)
        else:
            fetched = ytt_api.fetch(video_id)

        return " ".join([snippet.text for snippet in fetched if snippet.text.strip() != ""])
    except (TranscriptsDisabled, NoTranscriptFound):
        return "Transcript not available"
    except Exception as e:
        return f"Error: {str(e)}"

# ===============================
# Step 3: Fetch video details (stats + category)
# ===============================
def get_video_details(api_key, video_ids):
    url = f"{BASE_URL}/videos"
    params = {
        "part": "snippet,statistics",
        "id": ",".join(video_ids),
        "key": api_key
    }
    response = requests.get(url, params=params).json()

    details = {}
    for item in response.get("items", []):
        vid = item["id"]
        snippet = item["snippet"]
        stats = item.get("statistics", {})

        details[vid] = {
            "publishedAt": snippet.get("publishedAt"),
            "description": snippet.get("description"),
            "categoryId": snippet.get("categoryId"),
            "viewCount": stats.get("viewCount", "0"),
            "likeCount": stats.get("likeCount", "0"),
            "commentCount": stats.get("commentCount", "0")
        }
    return details

# ===============================
# Step 4: Fetch category names
# ===============================
def get_category_map(api_key, region="US"):
    url = f"{BASE_URL}/videoCategories"
    params = {"part": "snippet", "regionCode": region, "key": api_key}
    response = requests.get(url, params=params).json()

    category_map = {item["id"]: item["snippet"]["title"] for item in response.get("items", [])}
    return category_map

# ===============================
# Step 5: Dump into CSV
# ===============================
def save_to_csv(video_data, csv_file, languages=None):
    video_ids = [vid for vid, _ in video_data]

    # Get details + categories
    details = get_video_details(API_KEY, video_ids)
    category_map = get_category_map(API_KEY)

    with open(csv_file, mode="w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([
            "Video ID", "Title", "Published At", "Description",
            "Category", "Views", "Likes", "Comments", "Transcript"
        ])

        for video_id, title in video_data:
            transcript = fetch_transcript(video_id, languages)

            # ✅ Only save if transcript exists (not error / not empty)
            if transcript and "Transcript not available" not in transcript and not transcript.startswith("Error:"):
                info = details.get(video_id, {})
                category_name = category_map.get(info.get("categoryId", ""), "Unknown")

                writer.writerow([
                    video_id,
                    title,
                    info.get("publishedAt", ""),
                    info.get("description", ""),
                    category_name,
                    info.get("viewCount", "0"),
                    info.get("likeCount", "0"),
                    info.get("commentCount", "0"),
                    transcript
                ])

    print(f"✅ Only videos with transcripts saved to {csv_file}")

# ===============================
# MAIN
# ===============================
if __name__ == "__main__":
    preferred_languages = ["en", "hi"]

    videos = get_video_ids(API_KEY, CHANNEL_ID, 50)
    save_to_csv(videos, CSV_FILE, preferred_languages)