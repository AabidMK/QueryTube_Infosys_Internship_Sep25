import os
import csv
import googleapiclient.discovery

# ✅ Your API key here
API_KEY = "AIzaSyAWcOyJyYF_F72DcyGjZob77o6E4qmdcUI"

# ✅ One channel (Google Developers as example)
CHANNEL_ID = "UCq9dV0PMEdQFzD4JTCNfK3A"

# Build YouTube API client
youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=API_KEY)

# Track API usage
api_units_used = 0


def get_channel_details(channel_id):
    """Fetch channel metadata."""
    global api_units_used
    request = youtube.channels().list(
        part="snippet,statistics",
        id=channel_id
    )
    response = request.execute()
    api_units_used += 1  # channels.list = 1 unit

    channel = response["items"][0]
    channel_meta = {
        "channel_id": channel["id"],
        "channel_title": channel["snippet"]["title"],
        "channel_description": channel["snippet"]["description"],
        "channel_country": channel["snippet"].get("country", ""),
        "channel_thumbnail": channel["snippet"]["thumbnails"]["high"]["url"],
        "channel_subscriberCount": channel["statistics"].get("subscriberCount", ""),
        "channel_videoCount": channel["statistics"].get("videoCount", "")
    }
    return channel_meta


def get_all_videos(channel_id):
    """Fetch all videos with metadata from a channel."""
    global api_units_used
    videos = []
    next_page_token = None

    # Step 1: Get uploads playlist
    request = youtube.channels().list(
        part="contentDetails",
        id=channel_id
    )
    response = request.execute()
    api_units_used += 1
    uploads_playlist_id = response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

    # Step 2: Loop with pagination
    while True:
        request = youtube.playlistItems().list(
            part="snippet",
            playlistId=uploads_playlist_id,
            maxResults=50,
            pageToken=next_page_token
        )
        response = request.execute()
        api_units_used += 1

        video_ids = [item["snippet"]["resourceId"]["videoId"] for item in response["items"]]

        if video_ids:
            # Batch fetch video details (50 at a time)
            vid_request = youtube.videos().list(
                part="snippet,contentDetails,statistics,status",
                id=",".join(video_ids)
            )
            vid_response = vid_request.execute()
            api_units_used += 1  # batched call saves quota!

            for v in vid_response["items"]:
                snippet = v["snippet"]
                stats = v.get("statistics", {})
                content = v.get("contentDetails", {})
                status = v.get("status", {})

                videos.append({
                    "id": v["id"],
                    "title": snippet.get("title", ""),
                    "description": snippet.get("description", ""),
                    "publishedAt": snippet.get("publishedAt", ""),
                    "tags": "|".join(snippet.get("tags", [])),
                    "categoryId": snippet.get("categoryId", ""),
                    "defaultLanguage": snippet.get("defaultLanguage", ""),
                    "defaultAudioLanguage": snippet.get("defaultAudioLanguage", ""),
                    "thumbnail_default": snippet.get("thumbnails", {}).get("default", {}).get("url", ""),
                    "thumbnail_high": snippet.get("thumbnails", {}).get("high", {}).get("url", ""),
                    "duration": content.get("duration", ""),
                    "viewCount": stats.get("viewCount", ""),
                    "likeCount": stats.get("likeCount", ""),
                    "commentCount": stats.get("commentCount", ""),
                    "privacyStatus": status.get("privacyStatus", "")
                })

        next_page_token = response.get("nextPageToken")
        if not next_page_token:
            break

    return videos


def save_to_csv(channel_meta, videos):
    """Save merged channel + video metadata into CSV."""
    filename = "tech_pre.csv"

    fieldnames = [
        "id", "title", "description", "publishedAt", "tags", "categoryId",
        "defaultLanguage", "defaultAudioLanguage", "thumbnail_default",
        "thumbnail_high", "duration", "viewCount", "likeCount",
        "commentCount", "privacyStatus", "channel_id", "channel_title",
        "channel_description", "channel_country", "channel_thumbnail",
        "channel_subscriberCount", "channel_videoCount"
    ]

    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for video in videos:
            row = {**video, **channel_meta}
            writer.writerow(row)

    return filename


if __name__ == "__main__":
    channel_meta = get_channel_details(CHANNEL_ID)
    videos = get_all_videos(CHANNEL_ID)
    csv_name = save_to_csv(channel_meta, videos)

    print(f"📊 API units consumed: {api_units_used}")
    print(f"📹 Total videos fetched: {len(videos)}")
    print(f"✅ Data saved to {csv_name}")
 tis is u r code