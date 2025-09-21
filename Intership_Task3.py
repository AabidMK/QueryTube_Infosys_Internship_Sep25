import pandas as pd
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter

df = pd.read_csv("YT_UR_DATA.csv")


transcripts = []
formatter = TextFormatter()


for video_id in df["id"]:
    try:
        ytt_api = YouTubeTranscriptApi()
        transcript_list = ytt_api.list(video_id)

        transcript = None
        try:
            transcript = transcript_list.find_manually_created_transcript(['en'])
        except:
            try:
                transcript = transcript_list.find_generated_transcript(['en'])
            except:
                pass

        if transcript:
            transcript_data = transcript.fetch()
            formatted_text = formatter.format_transcript(transcript_data.snippets)

            transcripts.append({"video_id": video_id, "transcript": formatted_text})
            print(f"✅ Transcript fetched for {video_id}")
        else:
            transcripts.append({"video_id": video_id, "transcript": "Transcript not available"})
            print(f"⚠️ No transcript for {video_id}")

    except Exception as e:
        transcripts.append({"video_id": video_id, "transcript": f"Error: {str(e)}"})
        print(f"❌ Could not fetch transcript for {video_id} - {e}")

transcript_df = pd.DataFrame(transcripts)
transcript_df.to_csv("ChannelTranscripts.csv", index=False, encoding="utf-8")

print(f"\n💾 Saved transcripts for {len(transcript_df)} videos into ChannelTranscripts.csv")