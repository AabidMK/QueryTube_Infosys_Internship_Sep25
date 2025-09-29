import csv
from googleapiclient.discovery import build

def get_channel_videos(api_key, channel_id):
    youtube = build('youtube', 'v3', developerKey=api_key)

    # Get channel details
    channel_request = youtube.channels().list(
        part="snippet,contentDetails,statistics",
        id=channel_id
    )
    channel_response = channel_request.execute()
    
    if not channel_response.get('items'):
        print("Channel not found.")
        return []
        
    channel_item = channel_response['items'][0]

    channel_title = channel_item['snippet']['title']
    channel_description = channel_item['snippet']['description']
    channel_country = channel_item['snippet'].get('country')
    channel_thumbnail = channel_item['snippet']['thumbnails']['default']['url']
    channel_subscriber_count = channel_item['statistics']['subscriberCount']
    channel_video_count = channel_item['statistics']['videoCount']

    # Get video IDs from the channel's uploads playlist
    uploads_playlist_id = channel_item['contentDetails']['relatedPlaylists']['uploads']

    video_ids = []
    next_page_token = None
    while True:
        playlist_request = youtube.playlistItems().list(
            part='contentDetails',
            playlistId=uploads_playlist_id,
            maxResults=50,
            pageToken=next_page_token
        )
        playlist_response = playlist_request.execute()

        for item in playlist_response['items']:
            video_ids.append(item['contentDetails']['videoId'])

        next_page_token = playlist_response.get('nextPageToken')
        if not next_page_token:
            break

    # Get video details for all video IDs
    videos = []
    for i in range(0, len(video_ids), 50):
        video_request = youtube.videos().list(
            part='snippet,contentDetails,statistics,status',
            id=','.join(video_ids[i:i+50])
        )
        video_response = video_request.execute()
        videos.extend(video_response['items'])

    # Prepare data for CSV
    video_data = []
    for video in videos:
        snippet = video.get('snippet', {})
        statistics = video.get('statistics', {})
        status = video.get('status', {})
        content_details = video.get('contentDetails', {})
        thumbnails = snippet.get('thumbnails', {})
        default_thumbnail = thumbnails.get('default', {})
        high_thumbnail = thumbnails.get('high', {})

        video_info = {
            'id': video['id'],
            'title': snippet.get('title'),
            'description': snippet.get('description'),
            'publishedAt': snippet.get('publishedAt'),
            'tags': '|'.join(snippet.get('tags', [])),
            'categoryId': snippet.get('categoryId'),
            'defaultLanguage': snippet.get('defaultLanguage'),
            'defaultAudioLanguage': snippet.get('defaultAudioLanguage'),
            'thumbnail_default': default_thumbnail.get('url'),
            'thumbnail_high': high_thumbnail.get('url'),
            'duration': content_details.get('duration'),
            'viewCount': statistics.get('viewCount', 0),
            'likeCount': statistics.get('likeCount', 0),
            'commentCount': statistics.get('commentCount', 0),
            'privacyStatus': status.get('privacyStatus', 'N/A'), # Corrected line
            'channel_id': channel_id,
            'channel_title': channel_title,
            'channel_description': channel_description,
            'channel_country': channel_country,
            'channel_thumbnail': channel_thumbnail,
            'channel_subscriberCount': channel_subscriber_count,
            'channel_videoCount': channel_video_count
        }
        video_data.append(video_info)

    return video_data

def write_to_csv(video_data, filename):
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = [
            'id', 'title', 'description', 'publishedAt', 'tags', 'categoryId',
            'defaultLanguage', 'defaultAudioLanguage', 'thumbnail_default',
            'thumbnail_high', 'duration', 'viewCount', 'likeCount',
            'commentCount', 'privacyStatus', 'channel_id', 'channel_title',
            'channel_description', 'channel_country', 'channel_thumbnail',
            'channel_subscriberCount', 'channel_videoCount'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(video_data)

if __name__ == '__main__':
    API_KEY = 'YOUTUBE-API-KEY'  # Replace with your API key
    CHANNEL_ID = 'CHANNEL-ID'  # Replace with the channel ID you want to fetch
    CSV_FILENAME = 'tech with tim.csv'

    video_details = get_channel_videos(API_KEY, CHANNEL_ID)
    if video_details:
        write_to_csv(video_details, CSV_FILENAME)
        print(f"Data for channel {CHANNEL_ID} has been saved to {CSV_FILENAME}")