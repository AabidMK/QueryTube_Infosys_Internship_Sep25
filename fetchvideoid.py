import os
import pandas as pd
from googleapiclient.discovery import build

# === CONFIG ===
API_KEY = " "   # <-- replace with your key
CHANNEL_ID = "UC-lHJZR3Gqxm24_Vd_AJ5Yw"
INPUT_FILE = "pewdiepie.csv"
OUTPUT_FILE = "pewdiepie_with_ids.csv"
# ==============

# Load transcripts
df = pd.read_csv(INPUT_FILE)

# Build YouTube API service
youtube = build("youtube", "v3", developerKey=API_KEY)

# Get Uploads playlist ID
channel_response = youtube.channels().list(
    part="contentDetails",
    id=CHANNEL_ID
).execute()
uploads_playlist = channel_response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

# Fetch all video IDs from the uploads playlist
video_ids = []
next_page = None

while True:
    pl_request = youtube.playlistItems().list(
        part="contentDetails",
        playlistId=uploads_playlist,
        maxResults=50,
        pageToken=next_page
    )
    pl_response = pl_request.execute()
    for item in pl_response["items"]:
        video_ids.append(item["contentDetails"]["videoId"])
    next_page = pl_response.get("nextPageToken")
    if not next_page:
        break

print(f"Fetched {len(video_ids)} video IDs from PewDiePie’s channel.")

# Align video IDs with transcripts
# (Assuming row order == upload order)
df["video_id"] = video_ids[:len(df)]

# Add channel_id for completeness
df["channel_id"] = CHANNEL_ID

# Save
df.to_csv(OUTPUT_FILE, index=False)
print(f"Saved updated file to {OUTPUT_FILE}")
