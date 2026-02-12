import requests
import pandas as pd

# ==== SETUP ====
API_KEY = "AIzaSyDJm5R3yKFtcNDgkWeM6bH2sTQQh28kzuk"
CHANNEL_ID = "UCAuUUnT6oDeKwE6v1NGQxug"

# ==== STEP 1: Get channel info ====
channel_url = f"https://www.googleapis.com/youtube/v3/channels?part=snippet,statistics,contentDetails&id={CHANNEL_ID}&key={API_KEY}"
channel_response = requests.get(channel_url).json()

if "error" in channel_response:
    print("Error fetching channel info:", channel_response["error"])
    exit()

if "items" not in channel_response or len(channel_response["items"]) == 0:
    print("No channel info found.")
    exit()

channel_item = channel_response["items"][0]

channel_info = {
    "channelId": channel_item["id"],
    "channelTitle": channel_item["snippet"]["title"],
    "channelDescription": channel_item["snippet"].get("description", ""),
    "channelCountry": channel_item["snippet"].get("country", ""),
    "channelThumbnail": channel_item["snippet"]["thumbnails"]["default"]["url"],
    "subscriberCount": int(channel_item["statistics"].get("subscriberCount", 0)),
    "videoCount": int(channel_item["statistics"].get("videoCount", 0))
}

# ==== STEP 2: Get uploads playlist ID ====
uploads_playlist = channel_item["contentDetails"]["relatedPlaylists"]["uploads"]

# ==== STEP 3: Fetch all video IDs from uploads playlist safely ====
video_ids = []
next_page = None  # start with no page token
max_limit = 50  # Limit to first 50 videos for practicality
while True:
    pl_url = f"https://www.googleapis.com/youtube/v3/playlistItems?part=snippet&playlistId={uploads_playlist}&maxResults=50&key={API_KEY}"
    if next_page:
        pl_url += f"&pageToken={next_page}"

    pl_response = requests.get(pl_url).json()

    # Check for API errors
    if "error" in pl_response:
        print("API error while fetching playlist:", pl_response["error"])
        break

    items = pl_response.get("items", [])
    if not items:
        print("No items in response.")
        break

    for item in items:
        video_ids.append(item["snippet"]["resourceId"]["videoId"])

    next_page = pl_response.get("nextPageToken")
    if not next_page:
        break

print(f"Total videos fetched: {len(video_ids)}")

# ==== STEP 4: Get video details ====
all_videos = []

for i in range(0, len(video_ids), 50):  # API allows max 50 at a time
    batch_ids = ",".join(video_ids[i:i+50])
    vid_url = f"https://www.googleapis.com/youtube/v3/videos?part=snippet,contentDetails,statistics,status&id={batch_ids}&key={API_KEY}"
    vid_response = requests.get(vid_url).json()

    if "error" in vid_response:
        print("API error while fetching video details:", vid_response["error"])
        continue

    for item in vid_response.get("items", []):
        snippet = item["snippet"]
        stats = item.get("statistics", {})
        content = item.get("contentDetails", {})
        status = item.get("status", {})

        video_info = {
            "videoId": item["id"],
            "title": snippet.get("title", ""),
            "description": snippet.get("description", ""),
            "publishedAt": snippet.get("publishedAt", ""),
            "tags": ",".join(snippet.get("tags", [])),
            "categoryId": snippet.get("categoryId", ""),
            "defaultLanguage": snippet.get("defaultLanguage", ""),
            "defaultAudioLanguage": snippet.get("defaultAudioLanguage", ""),
            "thumbnail": snippet["thumbnails"]["default"]["url"],
            "duration": content.get("duration", ""),
            "viewCount": int(stats.get("viewCount", 0)),
            "likeCount": int(stats.get("likeCount", 0)),
            "commentCount": int(stats.get("commentCount", 0)),
            "privacyStatus": status.get("privacyStatus", ""),

            # Channel info added to each row
            "channelId": channel_info["channelId"],
            "channelTitle": channel_info["channelTitle"],
            "channelDescription": channel_info["channelDescription"],
            "channelCountry": channel_info["channelCountry"],
            "channelThumbnail": channel_info["channelThumbnail"],
            "subscriberCount": channel_info["subscriberCount"],
            "videoCount": channel_info["videoCount"]
        }
        all_videos.append(video_info)

# ==== STEP 5: Save to Excel safely ====
if not all_videos:
    print("No videos fetched. Exiting...")
else:
    df = pd.DataFrame(all_videos)

    # Reorder columns
    df = df[[
        "videoId", "title", "description", "publishedAt", "tags",
        "categoryId", "defaultLanguage", "defaultAudioLanguage", "thumbnail", "duration",
        "viewCount", "likeCount", "commentCount", "privacyStatus",
        "channelId", "channelTitle", "channelDescription", "channelCountry",
        "channelThumbnail", "subscriberCount", "videoCount"
    ]]

    df.to_csv("tedx_videos.csv", index=False)
    print("✅ Data exported to tedx_videos.csv")