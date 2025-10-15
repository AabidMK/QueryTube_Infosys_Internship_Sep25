"""
YouTube Data Collector for QueryTube AI Project
VS Code Implementation with .env support - LIMITED TO 50 VIDEOS
Author: QueryTube AI Team
"""

import requests
import pandas as pd
import json
import time
import logging
import os
from datetime import datetime
from typing import List, Dict, Optional, Any
from tqdm import tqdm
from dotenv import load_dotenv  # Added for .env support
import warnings
warnings.filterwarnings('ignore')

# Load environment variables from .env file
load_dotenv()

# Configure logging with UTF-8 encoding
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('youtube_collector.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class YouTubeDataCollector:
    """Professional YouTube Data Collector with .env support"""
    
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("❌ API key is required. Check your .env file.")
        
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'QueryTubeAI/1.0',
            'Accept': 'application/json'
        })
        
        # API URLs
        self.search_url = "https://www.googleapis.com/youtube/v3/search"
        self.videos_url = "https://www.googleapis.com/youtube/v3/videos"
        self.channels_url = "https://www.googleapis.com/youtube/v3/channels"
        
        # Configuration
        self.request_delay = 0.1
        self.max_retries = 3
        self.timeout = 30
        self.min_video_duration = 120  # Minimum duration in seconds to exclude Shorts
        
    def _make_request(self, url: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Make API request with comprehensive error handling"""
        for attempt in range(self.max_retries):
            try:
                print(f"Making request to {url} (attempt {attempt + 1})")
                response = self.session.get(url, params=params, timeout=self.timeout)
                
                # Handle different HTTP status codes
                if response.status_code == 403:
                    error_data = response.json()
                    if 'quotaExceeded' in str(error_data):
                        raise Exception("❌ YouTube API quota exceeded for today")
                    elif 'keyInvalid' in str(error_data):
                        raise Exception("❌ Invalid API key - check your .env file")
                    else:
                        raise Exception(f"❌ API access forbidden: {error_data}")
                elif response.status_code == 400:
                    raise Exception("❌ Bad request - check parameters")
                elif response.status_code != 200:
                    raise Exception(f"❌ HTTP {response.status_code}: {response.text}")
                
                response.raise_for_status()
                time.sleep(self.request_delay)
                return response.json()
                
            except requests.exceptions.Timeout:
                print(f"Warning: Request timeout on attempt {attempt + 1}")
            except requests.exceptions.ConnectionError:
                print(f"Warning: Connection error on attempt {attempt + 1}")
            except Exception as e:
                if "quota" in str(e).lower() or "keyInvalid" in str(e):
                    print(f"Warning: Request failed on attempt {attempt + 1}: {str(e).replace('❌', 'ERROR:')}")
            
            if attempt < self.max_retries - 1:
                wait_time = 2 ** attempt
                print(f"Waiting {wait_time} seconds before retry...")
                time.sleep(wait_time)
        
        raise Exception(f"❌ Failed to make request after {self.max_retries} attempts")
    
    def get_uploads_playlist_id(self, channel_id: str) -> str:
        """Get the uploads playlist ID for a channel"""
        params = {
            'key': self.api_key,
            'part': 'contentDetails',
            'id': channel_id
        }
        
        try:
            data = self._make_request(self.channels_url, params)
            if data.get('items'):
                uploads_playlist_id = data['items'][0]['contentDetails']['relatedPlaylists']['uploads']
                return uploads_playlist_id
        except Exception as e:
            print(f"Error getting uploads playlist: {e}")
        
        return None

    def get_video_ids(self, channel_id: str, max_videos: int = 70) -> List[str]:
        """Step 1: Collect video IDs using uploads playlist (will filter for long-form videos later)"""
        print(f"\n🔍 Step 1: Collecting video IDs from channel (targeting 50-70 long-form videos)...")
        print(f"Collecting video IDs from channel: {channel_id} (target: 50-70 long videos)")
        
        # First, get the uploads playlist ID
        print("📡 Getting channel uploads playlist...")
        uploads_playlist_id = self.get_uploads_playlist_id(channel_id)
        
        if not uploads_playlist_id:
            print("⚠️ Could not get uploads playlist, falling back to search API...")
            return self._get_video_ids_search_fallback(channel_id, max_videos)
        
        print(f"✅ Found uploads playlist: {uploads_playlist_id}")
        
        video_ids = []
        next_page_token = None
        page_count = 0
        max_pages = 15  # Allow more pages since we'll filter out Shorts later
        target_ids = max_videos * 3  # Collect 3x more to account for filtering
        
        playlist_url = "https://www.googleapis.com/youtube/v3/playlistItems"
        
        while len(video_ids) < target_ids and page_count < max_pages:
            page_count += 1
            
            params = {
                'key': self.api_key,
                'playlistId': uploads_playlist_id,
                'part': 'contentDetails',
                'maxResults': min(50, target_ids - len(video_ids))
            }
            
            if next_page_token:
                params['pageToken'] = next_page_token
            
            try:
                print(f"📡 Making API request for playlist items (page {page_count})...")
                data = self._make_request(playlist_url, params)
                
                # Extract video IDs from current page
                current_page_videos = []
                for item in data.get('items', []):
                    video_id = item.get('contentDetails', {}).get('videoId')
                    if video_id:
                        current_page_videos.append(video_id)
                
                video_ids.extend(current_page_videos)
                print(f"   📄 Page {page_count}: Found {len(current_page_videos)} videos (Total: {len(video_ids)})")
                
                # Check if there's a next page
                next_page_token = data.get('nextPageToken')
                if not next_page_token:
                    print(f"   ℹ️ No more pages available")
                    break
                    
                # If we have no videos on this page, break to avoid infinite loop
                if len(current_page_videos) == 0:
                    print(f"   ⚠️ No videos found on page {page_count}, stopping")
                    break
                
            except Exception as e:
                print(f"Error in playlist request (page {page_count}): {e}")
                raise
        
        # Return more video IDs than needed since we'll filter by duration later
        final_video_ids = video_ids[:target_ids]
        print(f"✅ Collected {len(final_video_ids)} video IDs across {page_count} pages (will filter for long-form videos)")
        
        return final_video_ids
    
    def _get_video_ids_search_fallback(self, channel_id: str, max_videos: int) -> List[str]:
        """Fallback method using search API"""
        print("🔄 Using search API fallback...")
        
        video_ids = []
        next_page_token = None
        page_count = 0
        max_pages = 5
        
        while len(video_ids) < max_videos * 3 and page_count < max_pages:
            page_count += 1
            
            params = {
                'key': self.api_key,
                'channelId': channel_id,
                'part': 'id',
                'order': 'date',
                'type': 'video',
                'maxResults': min(50, max_videos * 3 - len(video_ids)),  # Collect more for filtering
                'regionCode': 'US'
            }
            
            if next_page_token:
                params['pageToken'] = next_page_token
            
            try:
                print(f"📡 Making search API request (page {page_count})...")
                data = self._make_request(self.search_url, params)
                
                current_page_videos = []
                for item in data.get('items', []):
                    if 'videoId' in item.get('id', {}):
                        current_page_videos.append(item['id']['videoId'])
                
                video_ids.extend(current_page_videos)
                print(f"   📄 Page {page_count}: Found {len(current_page_videos)} videos (Total: {len(video_ids)})")
                
                next_page_token = data.get('nextPageToken')
                if not next_page_token or len(current_page_videos) == 0:
                    break
                
            except Exception as e:
                print(f"Error in search fallback (page {page_count}): {e}")
                break
        
        return video_ids[:max_videos * 3]  # Return more for filtering
    
    def get_video_details(self, video_ids: List[str]) -> List[Dict[str, Any]]:
        """Step 2: Get detailed video information (excluding short videos < 2 minutes)"""
        print(f"\n📹 Step 2: Getting detailed information for {len(video_ids)} videos...")
        
        all_videos = []
        short_videos_filtered = 0
        
        # Split video IDs into batches of 50 (YouTube API limit)
        batch_size = 50
        video_batches = [video_ids[i:i + batch_size] for i in range(0, len(video_ids), batch_size)]
        
        for batch_num, batch_ids in enumerate(video_batches, 1):
            print(f"📡 Processing batch {batch_num}/{len(video_batches)} ({len(batch_ids)} videos)...")
            
            params = {
                'key': self.api_key,
                'part': 'id,snippet,contentDetails,statistics,status',
                'id': ','.join(batch_ids)
            }
            
            try:
                data = self._make_request(self.videos_url, params)
                
                for item in data.get('items', []):
                    video_info = self._extract_video_details(item)
                    if video_info:
                        # Filter out short videos (videos under 2 minutes)
                        duration_seconds = video_info.get('duration_seconds', 0)
                        if duration_seconds >= 120:
                            all_videos.append(video_info)
                        else:
                            short_videos_filtered += 1
                            print(f"   Filtered: {video_info.get('title', 'Unknown')[:50]}... ({duration_seconds}s)")
                
            except Exception as e:
                print(f"Error processing batch {batch_num}: {e}")
                continue
        
        print(f"✅ Successfully collected details for {len(all_videos)} long-form videos")
        if short_videos_filtered > 0:
            print(f"🚫 Filtered out {short_videos_filtered} short videos (< 2 minutes)")
        
        return all_videos
    
    def get_channel_info(self, channel_id: str) -> Dict[str, Any]:
        """Step 3: Get channel information"""
        print(f"\n📺 Step 3: Getting channel information...")
        
        params = {
            'key': self.api_key,
            'part': 'id,snippet,statistics,brandingSettings',
            'id': channel_id
        }
        
        try:
            data = self._make_request(self.channels_url, params)
            
            if data.get('items'):
                item = data['items'][0]
                channel_info = self._extract_channel_details(item)
                print(f"✅ Channel info collected: {channel_info.get('channel_title', 'Unknown')}")
                return channel_info
                
        except Exception as e:
            print(f"Error getting channel info: {e}")
        
        print("⚠️ Could not get channel information")
        return {}
    
    def _extract_video_details(self, item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract comprehensive video details"""
        try:
            snippet = item.get('snippet', {})
            content_details = item.get('contentDetails', {})
            statistics = item.get('statistics', {})
            status = item.get('status', {})
            
            # Process thumbnails
            thumbnails = snippet.get('thumbnails', {})
            thumbnail_data = {}
            for quality, thumb_info in thumbnails.items():
                thumbnail_data[f'thumbnail_{quality}'] = thumb_info.get('url', '')
            
            # Process tags
            tags = snippet.get('tags', [])
            tags_str = '|'.join(tags) if tags else ''
            
            return {
                # Basic video info
                'video_id': item.get('id', ''),
                'title': snippet.get('title', ''),
                'description': snippet.get('description', '')[:1000],
                'channel_id': snippet.get('channelId', ''),
                'channel_title': snippet.get('channelTitle', ''),
                
                # Dates and timing
                'published_at': snippet.get('publishedAt', ''),
                'published_date': self._format_date(snippet.get('publishedAt', '')),
                'duration_iso': content_details.get('duration', ''),
                'duration_seconds': self._duration_to_seconds(content_details.get('duration', '')),
                'duration_formatted': self._format_duration(content_details.get('duration', '')),
                
                # Statistics
                'view_count': int(statistics.get('viewCount', 0)) if statistics.get('viewCount') else 0,
                'like_count': int(statistics.get('likeCount', 0)) if statistics.get('likeCount') else 0,
                'comment_count': int(statistics.get('commentCount', 0)) if statistics.get('commentCount') else 0,
                
                # Metadata
                'category_id': snippet.get('categoryId', ''),
                'default_language': snippet.get('defaultLanguage', ''),
                'default_audio_language': snippet.get('defaultAudioLanguage', ''),
                'privacy_status': status.get('privacy_status', ''),
                'tags': tags_str,
                'tags_count': len(tags),
                
                # Thumbnails
                'thumbnail_default': thumbnail_data.get('thumbnail_default', ''),
                'thumbnail_medium': thumbnail_data.get('thumbnail_medium', ''),
                'thumbnail_high': thumbnail_data.get('thumbnail_high', ''),
                
                # URLs
                'video_url': f"https://www.youtube.com/watch?v={item.get('id', '')}",
                'embed_url': f"https://www.youtube.com/embed/{item.get('id', '')}",
            }
            
        except Exception as e:
            print(f"Warning: Error extracting video details: {e}")
            return None
    
    def _extract_channel_details(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Extract channel details"""
        snippet = item.get('snippet', {})
        statistics = item.get('statistics', {})
        
        thumbnails = snippet.get('thumbnails', {})
        thumbnail_url = ''
        for quality in ['high', 'medium', 'default']:
            if quality in thumbnails:
                thumbnail_url = thumbnails[quality].get('url', '')
                break
        
        return {
            'channel_id': item.get('id', ''),
            'channel_title': snippet.get('title', ''),
            'channel_description': snippet.get('description', '')[:500],
            'channel_country': snippet.get('country', ''),
            'channel_thumbnail': thumbnail_url,
            'channel_published_at': snippet.get('publishedAt', ''),
            'channel_custom_url': snippet.get('customUrl', ''),
            'subscriber_count': int(statistics.get('subscriberCount', 0)) if statistics.get('subscriberCount') else 0,
            'total_video_count': int(statistics.get('videoCount', 0)) if statistics.get('videoCount') else 0,
            'channel_view_count': int(statistics.get('viewCount', 0)) if statistics.get('viewCount') else 0,
        }
    
    def _format_date(self, date_string: str) -> str:
        """Format ISO date to readable format"""
        try:
            if date_string:
                dt = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
                return dt.strftime('%Y-%m-%d %H:%M:%S')
        except:
            pass
        return date_string
    
    def _duration_to_seconds(self, duration: str) -> int:
        """Convert PT4M13S to seconds"""
        try:
            if not duration or not duration.startswith('PT'):
                return 0
            
            duration = duration[2:]
            seconds = 0
            
            if 'H' in duration:
                hours, duration = duration.split('H', 1)
                seconds += int(hours) * 3600
            
            if 'M' in duration:
                minutes, duration = duration.split('M', 1)
                seconds += int(minutes) * 60
            
            if 'S' in duration:
                secs = duration.replace('S', '')
                if secs:
                    seconds += int(secs)
            
            return seconds
        except:
            return 0
    
    def _format_duration(self, duration: str) -> str:
        """Format duration as MM:SS or HH:MM:SS"""
        seconds = self._duration_to_seconds(duration)
        if seconds == 0:
            return "00:00"
        
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes:02d}:{secs:02d}"
    
    def create_combined_dataset(self, videos_data: List[Dict[str, Any]], channel_info: Dict[str, Any]) -> pd.DataFrame:
        """Combine video data with channel info"""
        print(f"\n🔄 Step 4: Creating combined dataset...")
        
        df = pd.DataFrame(videos_data)
        
        for key, value in channel_info.items():
            if key not in df.columns:
                df[key] = value
        
        df = self._optimize_dataframe(df)
        
        print(f"✅ Combined dataset created with {len(df)} videos and {len(df.columns)} columns")
        return df
    
    def _optimize_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Optimize DataFrame"""
        if 'published_at' in df.columns:
            df['published_at'] = pd.to_datetime(df['published_at'], errors='coerce')
        
        numeric_cols = [
            'view_count', 'like_count', 'comment_count', 'duration_seconds',
            'tags_count', 'subscriber_count', 'total_video_count', 'channel_view_count'
        ]
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype('int64')
        
        return df
    
    def save_to_csv(self, df: pd.DataFrame, filename: Optional[str] = None) -> str:
        """Save DataFrame to CSV"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f'YT_DataCollection_{timestamp}.csv'
        
        if not filename.endswith('.csv'):
            filename += '.csv'
        
        print(f"\n💾 Step 5: Saving {len(df)} videos to {filename}...")
        
        try:
            df.to_csv(filename, index=False, encoding='utf-8')
            file_size = os.path.getsize(filename) / 1024
            print(f"✅ Data saved successfully!")
            print(f"   📁 File: {filename}")
            print(f"   📊 Size: {file_size:.1f} KB")
            print(f"   📈 Rows: {len(df)}")
            print(f"   📋 Columns: {len(df.columns)}")
            
            return filename
            
        except Exception as e:
            logger.error(f"Error saving CSV: {e}")
            raise
    
    def print_summary(self, df: pd.DataFrame, channel_info: Dict[str, Any]):
        """Print collection summary"""
        print(f"\n" + "="*60)
        print(f"📊 QUERYTUBE AI - COLLECTION SUMMARY")
        print(f"="*60)
        
        print(f"\n📺 CHANNEL INFORMATION:")
        print(f"   • Name: {channel_info.get('channel_title', 'Unknown')}")
        print(f"   • Subscribers: {channel_info.get('subscriber_count', 0):,}")
        print(f"   • Total Videos: {channel_info.get('total_video_count', 0):,}")
        
        print(f"\n📹 VIDEO STATISTICS (LONG-FORM ONLY):")
        print(f"   • Videos Collected: {len(df)} (excludes videos < 2 minutes)")
        print(f"   • Average Views: {df['view_count'].mean():,.0f}")
        print(f"   • Average Duration: {df['duration_seconds'].mean()/60:.1f} minutes")
        print(f"   • Shortest Video: {df['duration_seconds'].min()} seconds")
        print(f"   • Total Views: {df['view_count'].sum():,}")
        
        if len(df) >= 3:
            print(f"\n🏆 TOP 3 VIDEOS BY VIEWS:")
            top_videos = df.nlargest(3, 'view_count')[['title', 'view_count']]
            for i, (_, video) in enumerate(top_videos.iterrows(), 1):
                print(f"   {i}. {video['title'][:60]}...")
                print(f"      Views: {video['view_count']:,}")
        
        print(f"\n" + "="*60)

def check_env_file() -> bool:
    """Check if .env file exists"""
    if not os.path.exists('.env'):
        print("❌ .env file not found!")
        print("\n🔧 Please create a .env file with:")
        print("YOUTUBE_API_KEY=your_actual_api_key_here")
        return False
    return True

def test_api_key(api_key: str) -> bool:
    """Test if the API key is working"""
    try:
        url = "https://www.googleapis.com/youtube/v3/search"
        params = {
            'key': api_key,
            'part': 'snippet',
            'q': 'test',
            'maxResults': 1,
            'type': 'video'
        }
        response = requests.get(url, params=params, timeout=10)
        return response.status_code == 200
    except:
        return False

def main():
    """Main execution function with .env support - Long-form videos only"""
    
    print("🚀 QUERYTUBE AI - YOUTUBE DATA COLLECTOR (LONG-FORM VIDEOS)")
    print("="*60)
    
    # Check if .env file exists
    if not check_env_file():
        return None, None
    
    # Load API key from .env file
    API_KEY = os.getenv('YOUTUBE_API_KEY')
    
    if not API_KEY:
        print("❌ YOUTUBE_API_KEY not found in .env file!")
        print("\n🔧 Please add to your .env file:")
        print("YOUTUBE_API_KEY=your_actual_api_key_here")
        return None, None
    
    # Configuration
    CHANNEL_ID = "UCAuUUnT6oDeKwE6v1NGQxug"
    MIN_VIDEOS = 50
    MAX_VIDEOS = 70
    
    print(f"📺 Channel ID: {CHANNEL_ID}")
    print(f"🎯 Target Long Videos: {MIN_VIDEOS}-{MAX_VIDEOS} (excludes videos < 2 minutes)")
    print(f"🔑 API Key Source: .env file")
    print(f"💻 Environment: VS Code")
    
    # Test API key
    print(f"\n🔍 Testing API connection...")
    if not test_api_key(API_KEY):
        print("❌ API key test failed!")
        print("🔧 Check your API key in the .env file")
        return None, None
    
    print("✅ API key from .env file is working!")
    
    try:
        # Initialize collector
        collector = YouTubeDataCollector(API_KEY)
        
        # Collect data - gather more videos to ensure we get 50-70 after filtering
        video_ids = collector.get_video_ids(CHANNEL_ID, MAX_VIDEOS * 2)  # Collect 2x more for filtering
        if not video_ids:
            return None, None
        
        videos_data = collector.get_video_details(video_ids)
        if not videos_data:
            print("❌ No long-form videos found after filtering out short videos")
            return None, None
        
        # Check if we have enough videos
        if len(videos_data) < MIN_VIDEOS:
            print(f"⚠️ Warning: Only found {len(videos_data)} long videos, minimum required is {MIN_VIDEOS}")
            print(f"📊 Proceeding with {len(videos_data)} videos...")
        elif len(videos_data) > MAX_VIDEOS:
            print(f"📊 Found {len(videos_data)} long videos, limiting to {MAX_VIDEOS}")
            videos_data = videos_data[:MAX_VIDEOS]
        else:
            print(f"✅ Perfect! Found {len(videos_data)} long videos (within {MIN_VIDEOS}-{MAX_VIDEOS} range)")
        
        channel_info = collector.get_channel_info(CHANNEL_ID)
        
        df = collector.create_combined_dataset(videos_data, channel_info)
        
        filename = collector.save_to_csv(df)
        
        collector.print_summary(df, channel_info)
        
        print(f"\n🎉 SUCCESS! Data collected using .env API key")
        print(f"📁 Output file: {filename}")
        
        # Sample data
        print(f"\n📋 SAMPLE DATA:")
        sample_cols = ['video_id', 'title', 'view_count', 'duration_formatted']
        print(df[sample_cols].head().to_string(index=False))
        
        return df, filename
        
    except Exception as e:
        print(f"ERROR: Data collection failed: {str(e).replace('❌', 'ERROR:')}")
        print(f"\n❌ Error: {e}")
        return None, None

if __name__ == "__main__":
    df, filename = main()
    
    if df is not None:
        print(f"\n✅ Collection completed successfully!")
        print(f"📊 {len(df)} videos with {len(df.columns)} data fields")
        print(f"🔑 API key loaded from .env file")
    else:
        print(f"\n❌ Collection failed. Check your .env file and API key.")
