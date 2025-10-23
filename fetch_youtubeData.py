import os
import csv
import googleapiclient.discovery

# --- CONFIG ---
API_KEY = "AIzaSyB6ATjf8iyUgTI08g1psWP4OD_SZ2S__lA"
CHANNEL_ID = "UCJHA_jMfCvEnv-3kRjTCQXw"
CSV_FILE = "New_youtube_dataset.csv"

# Initialize YouTube API client
youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=API_KEY)
api_units_used = 0

# ---------------- CHANNEL API ----------------
def get_channel_details(channel_id):
    global api_units_used
    request = youtube.channels().list(part="id,snippet,statistics", id=channel_id)
    response = request.execute()
    api_units_used += 1

    item = response["items"][0]
    return {
        "channel_id": item.get("id", ""),
        "channel_title": item["snippet"].get("title", ""),
        "channel_description": item["snippet"].get("description", ""),
        "country": item["snippet"].get("country", ""),
        "channel_thumbnail": item["snippet"]["thumbnails"]["default"]["url"],
        "subscriber_count": item["statistics"].get("subscriberCount", 0),
        "video_count": item["statistics"].get("videoCount", 0)
    }

# ---------------- VIDEOS API ----------------
def get_all_videos(channel_id):
    global api_units_used
    videos = []

    next_page_token = None
    while True:
        request = youtube.search().list(
            part="id",
            channelId=channel_id,
            maxResults=50,
            type="video",
            pageToken=next_page_token
        )
        response = request.execute()
        api_units_used += 1

        video_ids = [item["id"]["videoId"] for item in response.get("items", []) if "videoId" in item["id"]]
        if video_ids:
            video_request = youtube.videos().list(
                part="snippet,contentDetails,statistics,status",
                id=",".join(video_ids)
            )
            video_response = video_request.execute()
            api_units_used += 1

            for v in video_response.get("items", []):
                snippet = v.get("snippet", {})
                stats = v.get("statistics", {})
                content = v.get("contentDetails", {})
                status = v.get("status", {})
                thumbnails = snippet.get("thumbnails", {})

                videos.append({
                    "video_id": v.get("id", ""),
                    "video_title": snippet.get("title", ""),
                    "video_description": snippet.get("description", ""),
                    "publishedAt": snippet.get("publishedAt", ""),
                    "tags": "|".join(snippet.get("tags", [])),
                    "categoryId": snippet.get("categoryId", "NA"),
                    "defaultLanguage": snippet.get("defaultLanguage", "NA"),
                    "defaultAudioLanguage": snippet.get("defaultAudioLanguage", "NA"),
                    "video_thumbnails": {
                        "default": thumbnails.get("default", {}).get("url", ""),
                        "high": thumbnails.get("high", {}).get("url", "")
                    },
                    "duration": content.get("duration", "NA"),
                    "viewCount": stats.get("viewCount", 0),
                    "likeCount": stats.get("likeCount", 0),
                    "commentCount": stats.get("commentCount", 0),
                    "privacyStatus": status.get("privacyStatus", "NA")
                })

        next_page_token = response.get("nextPageToken")
        if not next_page_token:
            break

    return videos

# ---------------- SAVE TO CSV ----------------
def save_to_csv(channel_meta, videos, filename=CSV_FILE):
    headers = [
        "id", "title", "description", "publishedAt", "tags",
        "categoryId", "defaultLanguage", "defaultAudioLanguage",
        "thumbnail_default", "thumbnail_high", "duration",
        "viewCount", "likeCount", "commentCount", "privacyStatus",
        "channel_id", "channel_title", "channel_description",
        "channel_country", "channel_thumbnail",
        "channel_subscriberCount", "channel_videoCount"
    ]

    file_exists = os.path.isfile(filename)

    with open(filename, "a", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        if not file_exists:
            writer.writeheader()

        for v in videos:
            row = {
                "id": v.get("video_id", ""),
                "title": v.get("video_title", ""),
                "description": v.get("video_description", ""),
                "publishedAt": v.get("publishedAt", ""),
                "tags": v.get("tags", ""),
                "categoryId": v.get("categoryId", "NA"),
                "defaultLanguage": v.get("defaultLanguage", "NA"),
                "defaultAudioLanguage": v.get("defaultAudioLanguage", "NA"),
                "thumbnail_default": v.get("video_thumbnails", {}).get("default", ""),
                "thumbnail_high": v.get("video_thumbnails", {}).get("high", ""),
                "duration": v.get("duration", ""),
                "viewCount": v.get("viewCount", 0),
                "likeCount": v.get("likeCount", 0),
                "commentCount": v.get("commentCount", 0),
                "privacyStatus": v.get("privacyStatus", ""),
                "channel_id": channel_meta.get("channel_id", ""),
                "channel_title": channel_meta.get("channel_title", ""),
                "channel_description": channel_meta.get("channel_description", ""),
                "channel_country": channel_meta.get("country", ""),
                "channel_thumbnail": channel_meta.get("channel_thumbnail", ""),
                "channel_subscriberCount": channel_meta.get("subscriber_count", 0),
                "channel_videoCount": channel_meta.get("video_count", 0)
            }
            writer.writerow(row)

    return filename

# ---------------- MAIN ----------------
if __name__ == "__main__":
    try:
        channel_meta = get_channel_details(CHANNEL_ID)
        print("Channel details fetched successfully.")
        videos = get_all_videos(CHANNEL_ID)
        print(f"Fetched {len(videos)} videos.")
        csv_name = save_to_csv(channel_meta, videos)
        print(f"Data saved to {csv_name}")
        print(f"API units consumed: {api_units_used}")
    except Exception as e:
        print("Error occurred:", e)
