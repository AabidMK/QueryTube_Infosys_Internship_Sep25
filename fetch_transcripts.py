import pandas as pd
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound

# ==== Load the CSV of fetched videos ====
try:
    df_videos = pd.read_csv("tedx_videos.csv")
except FileNotFoundError:
    print("❌ CSV file 'tedx_videos.csv' not found. Please run fetch_youtube_channel.py first.")
    exit()

video_ids = df_videos["videoId"].tolist()

# ==== Prepare list to store transcripts ====
transcript_data = []
failed_videos = []

for vid in video_ids:
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(vid)
        full_transcript = " ".join([entry["text"] for entry in transcript_list])
        transcript_data.append({"videoId": vid, "transcript": full_transcript})
        print(f"✅ Transcript fetched for video {vid}")
    except TranscriptsDisabled:
        print(f"⚠️ Transcripts are disabled for video {vid}")
        transcript_data.append({"videoId": vid, "transcript": ""})
        failed_videos.append(vid)
    except NoTranscriptFound:
        print(f"⚠️ No transcript found for video {vid}")
        transcript_data.append({"videoId": vid, "transcript": ""})
        failed_videos.append(vid)
    except Exception as e:
        print(f"⚠️ Error for video {vid}: {e}")
        transcript_data.append({"videoId": vid, "transcript": ""})
        failed_videos.append(vid)

# ==== Save transcripts to CSV ====
df_transcripts = pd.DataFrame(transcript_data)
df_transcripts.to_csv("tedx_transcripts.csv", index=False)
print("✅ Transcripts saved to tedx_transcripts.csv")

# ==== Save failed videos for reference ====
if failed_videos:
    pd.DataFrame({"videoId": failed_videos}).to_csv("failed_videos.csv", index=False)
    print(f"⚠️ {len(failed_videos)} videos failed. Saved to failed_videos.csv")
