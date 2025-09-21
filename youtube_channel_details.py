import requests
import csv

API_KEY = "AIzaSyB0jmEyC6SpjLJcItmyXWZezMkv3zDDwGg"
BASE_URL = "https://www.googleapis.com/youtube/v3"


CHANNEL_ID = "UCX6OQ3DkcsbYNE6H8uQQuVA"


def get_channel_info(channel_id):
    url = f"{BASE_URL}/channels"
    params = {
        "part": "snippet,statistics",
        "id": channel_id,
        "key": API_KEY
    }
    response = requests.get(url, params=params).json()
    channel = response["items"][0]
    snippet = channel["snippet"]
    stats = channel["statistics"]

    return {
        "channel_id": channel["id"],
        "channel_title": snippet["title"],
        "channel_description": snippet.get("description", ""),
        "channel_country": snippet.get("country", "Not Available"),
        "channel_thumbnail": snippet["thumbnails"]["default"]["url"],
        "subscriberCount": stats.get("subscriberCount", "0"),
        "videoCount": stats.get("videoCount", "0")
    }


def get_uploads_playlist(channel_id):
    url = f"{BASE_URL}/channels"
    params = {
        "part": "contentDetails",
        "id": channel_id,
        "key": API_KEY
    }
    response = requests.get(url, params=params).json()
    return response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]


def get_video_ids(playlist_id, max_results=50):
    url = f"{BASE_URL}/playlistItems"
    params = {
        "part": "contentDetails",
        "playlistId": playlist_id,
        "maxResults": max_results,
        "key": API_KEY
    }
    response = requests.get(url, params=params).json()
    return [item["contentDetails"]["videoId"] for item in response["items"]]


def get_video_details(video_ids):
    url = f"{BASE_URL}/videos"
    params = {
        "part": "snippet,contentDetails,statistics,status",
        "id": ",".join(video_ids),
        "key": API_KEY
    }
    response = requests.get(url, params=params).json()
    return response.get("items", [])


def save_to_csv(channel_info, videos, filename="youtube channel details.csv"):
    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        
        writer.writerow([
            "videoId", "title", "description", "publishedAt", "tags", "categoryId",
            "defaultLanguage", "defaultAudioLanguage", "thumbnails", "duration",
            "viewCount", "likeCount", "commentCount", "privacyStatus",
            "channel_id", "channel_title", "channel_description",
            "channel_country", "channel_thumbnail", "subscriberCount", "videoCount"
        ])

        # Rows
        for item in videos:
            snippet = item["snippet"]
            stats = item.get("statistics", {})
            details = item["contentDetails"]
            status = item["status"]

            writer.writerow([
                item["id"],
                snippet["title"],
                snippet.get("description", "").replace("\n", " "),
                snippet["publishedAt"],
                "|".join(snippet.get("tags", [])),
                snippet.get("categoryId", ""),
                snippet.get("defaultLanguage", ""),
                snippet.get("defaultAudioLanguage", ""),
                snippet["thumbnails"]["default"]["url"],
                details["duration"],
                stats.get("viewCount", "0"),
                stats.get("likeCount", "0"),
                stats.get("commentCount", "0"),
                status["privacyStatus"],
                channel_info["channel_id"],
                channel_info["channel_title"],
                channel_info["channel_description"].replace("\n", " "),
                channel_info["channel_country"],
                channel_info["channel_thumbnail"],
                channel_info["subscriberCount"],
                channel_info["videoCount"]
            ])

    print(f" Data saved to {filename}")


if __name__ == "__main__":
    channel_info = get_channel_info(CHANNEL_ID)
    uploads_playlist = get_uploads_playlist(CHANNEL_ID)
    video_ids = get_video_ids(uploads_playlist, max_results=50)  
    videos = get_video_details(video_ids)
    save_to_csv(channel_info, videos)
