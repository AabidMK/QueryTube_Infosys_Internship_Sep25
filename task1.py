import requests, csv

API_KEY = "AIzaSyCNod8nYfM12A2uNIaTZ33mP7xAG-EStKc"  
CHANNEL_ID = "UCJW3oUy5NZHSOexmp-aVwUg"

# --- Get Channel Info ---
c_url = "https://www.googleapis.com/youtube/v3/channels"
c_params = {"part":"snippet,contentDetails,statistics","id":CHANNEL_ID,"key":API_KEY}
c_data = requests.get(c_url, params=c_params).json()["items"][0]

ch_info = {
    "id": c_data["id"],
    "title": c_data["snippet"]["title"],
    "description": c_data["snippet"].get("description"),
    "country": c_data["snippet"].get("country"),
    "thumbnail": c_data["snippet"]["thumbnails"]["default"]["url"],
    "subscriberCount": c_data["statistics"].get("subscriberCount"),
    "videoCount": c_data["statistics"].get("videoCount"),
    "uploads": c_data["contentDetails"]["relatedPlaylists"]["uploads"]
}

# Get Video IDs 
video_ids, url, params = [], "https://www.googleapis.com/youtube/v3/playlistItems", {
    "part":"snippet,contentDetails","playlistId":ch_info["uploads"],"maxResults":50,"key":API_KEY
}
while True:
    r = requests.get(url, params=params).json()
    video_ids += [i["snippet"]["resourceId"]["videoId"] for i in r["items"]]
    if "nextPageToken" in r: params["pageToken"] = r["nextPageToken"]
    else: break

videos, v_url = [], "https://www.googleapis.com/youtube/v3/videos"
for i in range(0, len(video_ids), 50):
    v_params = {"part":"snippet,contentDetails,statistics,status","id":",".join(video_ids[i:i+50]),"key":API_KEY}
    videos += requests.get(v_url, params=v_params).json()["items"]


headers = ["channel_id","channel_title","channel_description","channel_country","channel_thumbnail",
           "channel_subscriberCount","channel_videoCount","video_id","video_title","video_description",
           "publishedAt","tags","categoryId","defaultLanguage","defaultAudioLanguage","video_thumbnail",
           "duration","viewCount","likeCount","commentCount","privacyStatus"]

with open("youtube_data.csv","w",newline="",encoding="utf-8") as f:
    writer = csv.writer(f); writer.writerow(headers)
    for v in videos:
        sn, cd, st, s = v.get("snippet",{}), v.get("contentDetails",{}), v.get("statistics",{}), v.get("status",{})
        writer.writerow([
            ch_info["id"], ch_info["title"], ch_info["description"], ch_info["country"], ch_info["thumbnail"],
            ch_info["subscriberCount"], ch_info["videoCount"], v["id"], sn.get("title"), sn.get("description"),
            sn.get("publishedAt"), "|".join(sn.get("tags",[])) if sn.get("tags") else None, sn.get("categoryId"),
            sn.get("defaultLanguage"), sn.get("defaultAudioLanguage"), sn.get("thumbnails",{}).get("default",{}).get("url"),
            cd.get("duration"), st.get("viewCount"), st.get("likeCount"), st.get("commentCount"), s.get("privacyStatus")
        ])

print("✅ Data saved to youtube_data.csv")
