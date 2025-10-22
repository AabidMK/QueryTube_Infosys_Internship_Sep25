import requests
import csv
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound

API_KEY = "AIzaSyCNod8nYfM12A2uNIaTZ33mP7xAG-EStKc"
CHANNEL_ID = "UCJW3oUy5NZHSOexmp-aVwUg"
OUTPUT_CSV = "youtube_transcripts.csv"
MAX_RESULTS = 50

SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"


def get_video_ids(channel_id, max_results=50):
    params = {
        "part": "id",
        "channelId": channel_id,
        "maxResults": max_results,
        "order": "date",
        "type": "video",
        "key": API_KEY,
    }
    r = requests.get(SEARCH_URL, params=params).json()
    return [item["id"]["videoId"] for item in r.get("items", [])]


def fetch_transcript(video_id, languages=None):
    try:
        # Try English transcripts
        fetched = YouTubeTranscriptApi.get_transcript(video_id, languages=languages or ["en"])
        return " ".join([s["text"] for s in fetched if s["text"].strip()])
    except (TranscriptsDisabled, NoTranscriptFound):
        # Try auto-generated English if manual not found
        try:
            fetched = YouTubeTranscriptApi.get_transcript(video_id, languages=["a.en"])
            return " ".join([s["text"] for s in fetched if s["text"].strip()])
        except (TranscriptsDisabled, NoTranscriptFound):
            return "Transcript not available"
    except Exception as e:
        return f"Error: {str(e)}"


def save_to_csv(videos):
    fieldnames = ["videoId", "transcript"]
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for v in videos:
            writer.writerow(v)


if __name__ == "__main__":
    print("Fetching video IDs...")
    video_ids = get_video_ids(CHANNEL_ID, MAX_RESULTS)
    print(f"Fetched {len(video_ids)} videos.")

    print("Fetching transcripts...")
    videos = []
    for vid in video_ids:
        transcript_text = fetch_transcript(vid)
        videos.append({"videoId": vid, "transcript": transcript_text})

    print("Saving to CSV...")
    save_to_csv(videos)

    print(f"Done! Data saved to {OUTPUT_CSV}")
