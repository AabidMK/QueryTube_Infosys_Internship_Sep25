import pandas as pd
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from isodate import parse_duration

print(hasattr(YouTubeTranscriptApi, "get_transcript"))

# ==============================
# CONFIG
# ==============================
API_KEY = "AIzaSyCnnMJaTHxktf6PYClfh3sc3v2RqfI_7DQ"   # <-- replace with your valid API key
CHANNEL_ID = "UCz456K_p_K30hNf9JgK-M6w"
OUTPUT_FILE = "videos_with_transcripts.csv"

# ==============================
# INIT
# ==============================
youtube = build("youtube", "v3", developerKey=API_KEY)

# ==============================
# 1. Get channel details
# ==============================
channel_response = youtube.channels().list(
    part="snippet,statistics,contentDetails",
    id=CHANNEL_ID
).execute()

channel_data = channel_response["items"][0]
channel_info = {
    "channel_id": CHANNEL_ID,
    "channel_title": channel_data["snippet"]["title"],
    "channel_description": channel_data["snippet"].get("description", ""),
    "channel_country": channel_data["snippet"].get("country", ""),
    "channel_thumbnail": channel_data["snippet"]["thumbnails"]["high"]["url"],
    "channel_subscriberCount": channel_data["statistics"].get("subscriberCount", 0),
    "channel_videoCount": channel_data["statistics"].get("videoCount", 0),
}

uploads_playlist_id = channel_data["contentDetails"]["relatedPlaylists"]["uploads"]

# ==============================
# 2. Get at least 50 non-shorts videos
# ==============================
video_ids = []
next_page_token = None

while len(video_ids) < 200:  # fetch more, since many are shorts
    playlist_items_response = youtube.playlistItems().list(
        part="contentDetails",
        playlistId=uploads_playlist_id,
        maxResults=50,
        pageToken=next_page_token
    ).execute()

    for item in playlist_items_response["items"]:
        video_ids.append(item["contentDetails"]["videoId"])

    next_page_token = playlist_items_response.get("nextPageToken")
    if not next_page_token:
        break

print(f"Fetched {len(video_ids)} uploaded videos (including shorts)")

# ==============================
# 3. Fetch details + transcripts (filter shorts)
# ==============================
all_videos = []

for i in range(0, len(video_ids), 50):
    batch_ids = video_ids[i:i+50]

    video_response = youtube.videos().list(
        part="snippet,contentDetails,statistics,status",
        id=",".join(batch_ids)
    ).execute()

    for video in video_response["items"]:
        snippet = video["snippet"]
        stats = video.get("statistics", {})
        content = video.get("contentDetails", {})
        status = video.get("status", {})

        # Check if it's a short
        duration = content.get("duration", "")
        seconds = 0
        try:
            seconds = parse_duration(duration).total_seconds()
        except:
            pass

        title = snippet.get("title", "").lower()
        description = snippet.get("description", "").lower()

        if seconds < 60 or "#shorts" in title or "#shorts" in description:
            continue  # skip shorts

        # Fetch transcript
        transcript_text = ""
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video["id"])
            transcript_text = " ".join([t["text"] for t in transcript])
        except (TranscriptsDisabled, NoTranscriptFound):
            transcript_text = "Transcript not available"
        except Exception as e:
            transcript_text = f"Error: {str(e)}"

        video_info = {
            "id": video["id"],
            "title": snippet.get("title", ""),
            "description": snippet.get("description", ""),
            "publishedAt": snippet.get("publishedAt", ""),
            "tags": "|".join(snippet.get("tags", [])),
            "categoryId": snippet.get("categoryId", ""),
            "defaultLanguage": snippet.get("defaultLanguage", ""),
            "defaultAudioLanguage": snippet.get("defaultAudioLanguage", ""),
            "thumbnail_default": snippet["thumbnails"]["default"]["url"],
            "thumbnail_high": snippet["thumbnails"]["high"]["url"],
            "duration": duration,
            "viewCount": stats.get("viewCount", 0),
            "likeCount": stats.get("likeCount", 0),
            "commentCount": stats.get("commentCount", 0),
            "privacyStatus": status.get("privacyStatus", "public"),
            "transcript": transcript_text,
            **channel_info
        }

        all_videos.append(video_info)

        if len(all_videos) >= 50:  # ✅ stop when we have 50 non-shorts
            break
    if len(all_videos) >= 50:
        break

print(f"Collected {len(all_videos)} non-shorts videos")

# ==============================
# 4. Save to CSV
# ==============================
df = pd.DataFrame(all_videos)

columns_order = [
    "id", "title", "description", "publishedAt", "tags", "categoryId",
    "defaultLanguage", "defaultAudioLanguage", "thumbnail_default", "thumbnail_high",
    "duration", "viewCount", "likeCount", "commentCount", "privacyStatus",
    "transcript",
    "channel_id", "channel_title", "channel_description", "channel_country",
    "channel_thumbnail", "channel_subscriberCount", "channel_videoCount"
]

df = df[columns_order]
df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8")

print(f"✅ Saved {len(df)} non-shorts videos with transcripts to {OUTPUT_FILE}")