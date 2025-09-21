import time
import pandas as pd
from datetime import datetime
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
from tabulate import tabulate  # for nice table printing


# ------------------ Transcript Extractor ------------------ #
class YouTubeTranscriptExtractor:
    def __init__(self):
        self.formatter = TextFormatter()

    def get_transcript(self, video_id):
        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            transcript = None
            try:
                transcript = transcript_list.find_manually_created_transcript(['en'])
            except:
                try:
                    transcript = transcript_list.find_generated_transcript(['en'])
                except:
                    return ""

            if transcript:
                transcript_data = transcript.fetch()
                formatted_text = self.formatter.format_transcript(transcript_data)
                return formatted_text
            else:
                return ""
        except Exception:
            return ""


# ------------------ YouTube API Fetcher ------------------ #
def fetch_channel_videos(api_key, channel_id, max_videos=50):
    youtube = build("youtube", "v3", developerKey=api_key)

    # Get channel details
    channel_response = youtube.channels().list(
        part="snippet,statistics",
        id=channel_id
    ).execute()

    channel = channel_response["items"][0]
    channel_info = {
        "channel_id": channel["id"],
        "channel_title": channel["snippet"]["title"],
        "channel_description": channel["snippet"].get("description", ""),
        "channel_country": channel["snippet"].get("country", ""),
        "channel_thumbnail": channel["snippet"]["thumbnails"]["default"]["url"],
        "channel_subscriberCount": channel["statistics"].get("subscriberCount", 0),
        "channel_videoCount": channel["statistics"].get("videoCount", 0)
    }

    # Fetch video IDs
    video_ids = []
    next_page_token = None
    while len(video_ids) < max_videos:
        search_response = youtube.search().list(
            part="id",
            channelId=channel_info["channel_id"],
            maxResults=min(50, max_videos - len(video_ids)),
            order="date",
            pageToken=next_page_token
        ).execute()

        for item in search_response["items"]:
            if item["id"]["kind"] == "youtube#video":
                video_ids.append(item["id"]["videoId"])
                if len(video_ids) >= max_videos:
                    break

        next_page_token = search_response.get("nextPageToken")
        if not next_page_token or len(video_ids) >= max_videos:
            break

    print(f"✅ Fetched {len(video_ids)} videos from {channel_info['channel_title']}")

    # Fetch details for these videos
    all_videos = []
    for i in range(0, len(video_ids), 50):
        video_response = youtube.videos().list(
            part="snippet,contentDetails,statistics,status",
            id=",".join(video_ids[i:i + 50])
        ).execute()

        for video in video_response["items"]:
            snippet = video["snippet"]
            stats = video["statistics"]
            content_details = video["contentDetails"]
            status = video["status"]

            video_data = {
                "ID": video["id"],
                "Title": snippet.get("title", ""),
                "PublishedAt": snippet.get("publishedAt", ""),
                "Views": stats.get("viewCount", 0),
                "Likes": stats.get("likeCount", 0),
                "Comments": stats.get("commentCount", 0),
                "Duration": content_details.get("duration", ""),
                "Definition": content_details.get("definition", ""),
                "Channel": channel_info["channel_title"]
            }
            all_videos.append(video_data)

    return all_videos


# ------------------ Main Workflow ------------------ #
if __name__ == "__main__":
    API_KEY = "AIzaSyDJTLCHV_A3zLe96ZfDIHyRu5L0ZUPgc2w"
    CHANNEL_ID = "UCtxD0x6AuNNqdXO9Wp5GHew"  # TraversyMedia example

    # Fetch metadata for first 50 videos
    videos_data = fetch_channel_videos(API_KEY, CHANNEL_ID, max_videos=50)

    # Extract transcripts
    extractor = YouTubeTranscriptExtractor()
    for idx, video in enumerate(videos_data, 1):
        print(f"[{idx}/{len(videos_data)}] Fetching transcript for {video['ID']}")
        video["Transcript"] = extractor.get_transcript(video["ID"])
        time.sleep(1)

    # Convert to DataFrame
    df = pd.DataFrame(videos_data)

    # Print in table format
    print("\n🎬 YouTube Videos Details:\n")
    print(tabulate(df, headers='keys', tablefmt='fancy_grid', showindex=False))
