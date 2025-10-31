import requests
import pandas as pd

# ---------- CONFIG ----------
API_KEY = ${Api_key}
CHANNEL_ID = "UCteRPiisgIoHtMgqHegpWAQ"
MAX_RESULTS = 50   # per page (YouTube API limit)
# ----------------------------

# Base URLs
SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
VIDEOS_URL = "https://www.googleapis.com/youtube/v3/videos"
CHANNEL_URL = "https://www.googleapis.com/youtube/v3/channels"


def get_video_ids(channel_id, api_key, max_results=50):
    """Fetch all video IDs from a channel using Search endpoint"""
    video_ids = []
    page_token = None

    while True:
        params = {
            "part": "id",
            "channelId": channel_id,
            "maxResults": max_results,
            "order": "date",
            "type": "video",
            "key": api_key,
            "pageToken": page_token
        }
        response = requests.get(SEARCH_URL, params=params).json()
        for item in response.get("items", []):
            video_ids.append(item["id"]["videoId"])
        page_token = response.get("nextPageToken")
        if not page_token:
            break

    return video_ids


def get_video_details(video_ids, api_key, channel_data):
    """Fetch video details from Videos endpoint"""
    all_videos = []
    for i in range(0, len(video_ids), 50):  # batch of 50 (API limit)
        batch = video_ids[i:i+50]
        params = {
            "part": "snippet,contentDetails,statistics,status",
            "id": ",".join(batch),
            "key": api_key
        }
        response = requests.get(VIDEOS_URL, params=params).json()

        for item in response.get("items", []):
            snippet = item["snippet"]
            stats = item.get("statistics", {})
            content = item.get("contentDetails", {})
            status = item.get("status", {})

            video_data = {
                "id": item["id"],
                "title": snippet.get("title"),
                "description": snippet.get("description"),
                "publishedAt": snippet.get("publishedAt"),
                "tags": "|".join(snippet.get("tags", [])),
                "categoryId": snippet.get("categoryId"),
                "defaultLanguage": snippet.get("defaultLanguage"),
                "defaultAudioLanguage": snippet.get("defaultAudioLanguage"),
                "thumbnail_default": snippet.get("thumbnails", {}).get("default", {}).get("url"),
                "thumbnail_high": snippet.get("thumbnails", {}).get("high", {}).get("url"),
                "duration": content.get("duration"),
                "viewCount": stats.get("viewCount"),
                "likeCount": stats.get("likeCount"),
                "commentCount": stats.get("commentCount"),
                "privacyStatus": status.get("privacyStatus"),
                "channel_id": channel_data["id"],
                "channel_title": channel_data["title"],
                "channel_description": channel_data["description"],
                "channel_country": channel_data.get("country"),
                "channel_thumbnail": channel_data["thumbnail"],
                "channel_subscriberCount": channel_data.get("subscriberCount"),
                "channel_videoCount": channel_data.get("videoCount")
            }
            all_videos.append(video_data)

    return all_videos


def get_channel_details(channel_id, api_key):
    """Fetch channel details from Channel endpoint"""
    params = {
        "part": "snippet,statistics",
        "id": channel_id,
        "key": api_key
    }
    response = requests.get(CHANNEL_URL, params=params).json()
    item = response["items"][0]

    channel_data = {
        "id": item["id"],
        "title": item["snippet"]["title"],
        "description": item["snippet"]["description"],
        "country": item["snippet"].get("country"),
        "thumbnail": item["snippet"]["thumbnails"]["high"]["url"],
        "subscriberCount": item["statistics"].get("subscriberCount"),
        "videoCount": item["statistics"].get("videoCount")
    }
    return channel_data


if __name__ == "__main__":
    # 1. Get channel details
    channel = get_channel_details(CHANNEL_ID, API_KEY)

    # 2. Get video IDs
    video_ids = get_video_ids(CHANNEL_ID, API_KEY)
    print(f"Found {len(video_ids)} videos")

    # 3. Get video details with channel info
    videos = get_video_details(video_ids, API_KEY, channel)
    df_videos = pd.DataFrame(videos)

    # Save to CSV
    df_videos.to_csv("youtube_channel_videos_T1.csv", index=False, encoding="utf-8-sig")

    print("CSV saved: youtube_channel_videos.csv")




# import requests
# import pandas as pd

# # ---------- CONFIG ----------
# API_KEY = ${Api_key}
# CHANNEL_ID = "UCteRPiisgIoHtMgqHegpWAQ"
# MAX_RESULTS = 50   # per page (YouTube API limit)
# # ----------------------------

# # Base URLs
# SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
# VIDEOS_URL = "https://www.googleapis.com/youtube/v3/videos"
# CHANNEL_URL = "https://www.googleapis.com/youtube/v3/channels"

# def get_video_ids(channel_id, api_key, max_results=50):
#     """Fetch all video IDs from a channel using Search endpoint"""
#     video_ids = []
#     page_token = None

#     while True:
#         params = {
#             "part": "id",
#             "channelId": channel_id,
#             "maxResults": max_results,
#             "order": "date",
#             "type": "video",
#             "key": api_key,
#             "pageToken": page_token
#         }
#         response = requests.get(SEARCH_URL, params=params).json()
#         for item in response.get("items", []):
#             video_ids.append(item["id"]["videoId"])
#         page_token = response.get("nextPageToken")
#         if not page_token:
#             break

#     return video_ids


# def get_video_details(video_ids, api_key):
#     """Fetch video details from Videos endpoint"""
#     all_videos = []
#     for i in range(0, len(video_ids), 50):  # batch of 50 (API limit)
#         batch = video_ids[i:i+50]
#         params = {
#             "part": "snippet,contentDetails,statistics,status",
#             "id": ",".join(batch),
#             "key": api_key
#         }
#         response = requests.get(VIDEOS_URL, params=params).json()

#         for item in response.get("items", []):
#             snippet = item["snippet"]
#             stats = item.get("statistics", {})
#             content = item.get("contentDetails", {})
#             status = item.get("status", {})

#             video_data = {
#                 "id": item["id"],
#                 "title": snippet.get("title"),
#                 "description": snippet.get("description"),
#                 "publishedAt": snippet.get("publishedAt"),
#                 "tags": snippet.get("tags", []),
#                 "categoryId": snippet.get("categoryId"),
#                 "defaultLanguage": snippet.get("defaultLanguage"),
#                 "defaultAudioLanguage": snippet.get("defaultAudioLanguage"),
#                 "thumbnails": snippet.get("thumbnails", {}),
#                 "duration": content.get("duration"),
#                 "viewCount": stats.get("viewCount"),
#                 "likeCount": stats.get("likeCount"),
#                 "commentCount": stats.get("commentCount"),
#                 "privacyStatus": status.get("privacyStatus")
#             }
#             all_videos.append(video_data)

#     return all_videos


# def get_channel_details(channel_id, api_key):
#     """Fetch channel details from Channel endpoint"""
#     params = {
#         "part": "snippet,statistics",
#         "id": channel_id,
#         "key": api_key
#     }
#     response = requests.get(CHANNEL_URL, params=params).json()
#     item = response["items"][0]

#     channel_data = {
#         "id": item["id"],
#         "title": item["snippet"]["title"],
#         "description": item["snippet"]["description"],
#         "country": item["snippet"].get("country"),
#         "thumbnail": item["snippet"]["thumbnails"]["default"]["url"],
#         "subscriberCount": item["statistics"].get("subscriberCount"),
#         "videoCount": item["statistics"].get("videoCount")
#     }
#     return channel_data


# if __name__ == "__main__":
#     # 1. Get video IDs
#     video_ids = get_video_ids(CHANNEL_ID, API_KEY)
#     print(f"Found {len(video_ids)} videos")

#     # 2. Get video details
#     videos = get_video_details(video_ids, API_KEY)
#     df_videos = pd.DataFrame(videos)

#     # 3. Get channel details
#     channel = get_channel_details(CHANNEL_ID, API_KEY)

#     # Save to CSV
#     df_videos.to_csv("yt_sundas_khalid_metrics.csv", index=False, encoding="utf-8-sig")

#     print("Channel Info:", channel)
#     print("Videos saved to youtube_videos.csv")

