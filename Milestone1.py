import requests
import csv

API_KEY = 'AIzaSyAxIGGpA441tMB5z0az3UTr4YG5YHBvWLg'
CHANNEL_ID = 'UC8butISFwT-Wl7EV0hUK0BQ'
MAX_ENTRIES = 50

def get_all_channel_videos(channel_id, limit):
    video_ids = []
    url = f'https://www.googleapis.com/youtube/v3/search?key={API_KEY}&channelId={channel_id}&part=id&order=date&maxResults=50&type=video'
    while url and len(video_ids) < limit:
        response = requests.get(url)
        data = response.json()
        for item in data.get('items', []):
            vid = item['id'].get('videoId')
            if vid and vid not in video_ids:
                video_ids.append(vid)
                if len(video_ids) >= limit:
                    break
        if 'nextPageToken' in data and len(video_ids) < limit:
            url = f'https://www.googleapis.com/youtube/v3/search?key={API_KEY}&channelId={channel_id}&part=id&order=date&maxResults=50&type=video&pageToken={data["nextPageToken"]}'
        else:
            url = None
    return video_ids

def get_playlists(channel_id):
    playlists = []
    url = f'https://www.googleapis.com/youtube/v3/playlists?part=id&channelId={channel_id}&maxResults=50&key={API_KEY}'
    response = requests.get(url)
    data = response.json()
    for item in data.get('items', []):
        playlists.append(item['id'])
    return playlists

def get_videos_from_playlist(playlist_id, already_fetched, limit):
    videos = []
    url = f'https://www.googleapis.com/youtube/v3/playlistItems?part=contentDetails&playlistId={playlist_id}&maxResults=50&key={API_KEY}'
    while url and len(videos) + len(already_fetched) < limit:
        response = requests.get(url)
        data = response.json()
        for item in data.get('items', []):
            video_id = item['contentDetails']['videoId']
            if video_id not in already_fetched and video_id not in videos:
                videos.append(video_id)
                if len(videos) + len(already_fetched) >= limit:
                    break
        if 'nextPageToken' in data and len(videos) + len(already_fetched) < limit:
            url = f'https://www.googleapis.com/youtube/v3/playlistItems?part=contentDetails&playlistId={playlist_id}&maxResults=50&key={API_KEY}&pageToken={data["nextPageToken"]}'
        else:
            url = None
    return videos

# ...existing code...
def fetch_and_write_video(video_id, writer):
    video_url = f'https://www.googleapis.com/youtube/v3/videos?part=snippet,statistics,contentDetails,status&id={video_id}&key={API_KEY}'
    video_response = requests.get(video_url)
    video_data = video_response.json()
    if not video_data.get('items'):
        return False
    video_info = video_data['items'][0]

    snippet = video_info['snippet']
    statistics = video_info.get('statistics', {})
    content_details = video_info.get('contentDetails', {})
    status = video_info.get('status', {})

    channel_id = snippet.get('channelId', CHANNEL_ID)
    channel_url = f'https://www.googleapis.com/youtube/v3/channels?part=snippet,statistics&id={channel_id}&key={API_KEY}'
    channel_response = requests.get(channel_url)
    channel_data = channel_response.json()
    channel_info = channel_data['items'][0]

    channel_snippet = channel_info['snippet']
    channel_statistics = channel_info['statistics']

    writer.writerow({
        'video_id': video_info['id'],
        'video_title': snippet.get('title', 'N/A'),
        'video_description': snippet.get('description', 'N/A'),
        'video_published_at': snippet.get('publishedAt', 'N/A'),
        'video_tags': ','.join(snippet.get('tags', [])) if snippet.get('tags') else 'N/A',
        'video_category_id': snippet.get('categoryId', 'N/A'),
        'video_default_language': snippet.get('defaultLanguage', 'N/A'),
        'video_default_audio_language': snippet.get('defaultAudioLanguage', 'N/A'),
        'video_thumbnail_default': snippet.get('thumbnails', {}).get('default', {}).get('url', 'N/A'),
        'video_thumbnail_high': snippet.get('thumbnails', {}).get('high', {}).get('url', 'N/A'),
        'video_duration': content_details.get('duration', 'N/A'),
        'video_view_count': statistics.get('viewCount', 'N/A'),
        'video_like_count': statistics.get('likeCount', 'N/A'),
        'video_comment_count': statistics.get('commentCount', 'N/A'),
        'video_privacy_status': status.get('privacyStatus', 'N/A'),
        'channel_id': channel_info['id'],
        'channel_title': channel_snippet.get('title', 'N/A'),
        'channel_description': channel_snippet.get('description', 'N/A'),
        'channel_country': channel_snippet.get('country', 'N/A'),
        'channel_thumbnail': channel_snippet.get('thumbnails', 'N/A'),
        'channel_subscriber_count': channel_statistics.get('subscriberCount', 'N/A'),
        'channel_video_count': channel_statistics.get('videoCount', 'N/A')
    })
    return True

if __name__ == "__main__":
    with open('youtube_playlist_videos.csv', mode='w', newline='', encoding='utf-8') as csvfile:
        fieldnames = [
            'video_id', 'video_title', 'video_description', 'video_published_at', 'video_tags',
            'video_category_id', 'video_default_language', 'video_default_audio_language',
            'video_thumbnail_default', 'video_thumbnail_high',
            'video_duration', 'video_view_count', 'video_like_count', 'video_comment_count', 'video_privacy_status',
            'channel_id', 'channel_title', 'channel_description', 'channel_country', 'channel_thumbnail',
            'channel_subscriber_count', 'channel_video_count'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
# ...existing code...

        # 1. Fetch up to MAX_ENTRIES channel videos (not in any playlist)
        all_channel_videos = get_all_channel_videos(CHANNEL_ID, MAX_ENTRIES)

        # 2. Fetch up to MAX_ENTRIES videos from playlists, skipping already fetched
        playlists = get_playlists(CHANNEL_ID)
        playlist_videos = []
        for playlist_id in playlists:
            if len(all_channel_videos) + len(playlist_videos) >= MAX_ENTRIES:
                break
            new_videos = get_videos_from_playlist(playlist_id, set(all_channel_videos + playlist_videos), MAX_ENTRIES)
            playlist_videos.extend(new_videos)
            if len(all_channel_videos) + len(playlist_videos) >= MAX_ENTRIES:
                break

        # 3. Write up to MAX_ENTRIES videos (no duplicates)
        written = 0
        for video_id in all_channel_videos:
            if written >= MAX_ENTRIES:
                break
            if fetch_and_write_video(video_id, writer):
                written += 1

        for video_id in playlist_videos:
            if written >= MAX_ENTRIES:
                break
            if fetch_and_write_video(video_id, writer):
                written += 1

def get_all_video_ids(channel_id, max_entries):
    all_channel_videos = get_all_channel_videos(channel_id, max_entries)
    playlists = get_playlists(channel_id)
    playlist_videos = []
    for playlist_id in playlists:
        if len(all_channel_videos) + len(playlist_videos) >= max_entries:
            break
        new_videos = get_videos_from_playlist(playlist_id, set(all_channel_videos + playlist_videos), max_entries)
        playlist_videos.extend(new_videos)
        if len(all_channel_videos) + len(playlist_videos) >= max_entries:
            break
    return list(dict.fromkeys(all_channel_videos + playlist_videos))[:max_entries]