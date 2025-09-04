import httpx
import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

# API Keys
ITUNES_API_BASE = "https://itunes.apple.com/search"
YOUTUBE_API_BASE = "https://www.googleapis.com/youtube/v3/search"
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

async def enrich_track_metadata(track_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Enrich track metadata by searching iTunes/Apple Music and YouTube APIs.
    """
    enriched_data = track_data.copy()
    
    # Search iTunes/Apple Music first
    itunes_data = await search_itunes(track_data['title'], track_data['artist'])
    if itunes_data:
        enriched_data.update(itunes_data)
    
    # Search YouTube if we don't have a link yet
    if not enriched_data.get('youtube_url') and YOUTUBE_API_KEY:
        youtube_data = await search_youtube(track_data['title'], track_data['artist'])
        if youtube_data:
            enriched_data.update(youtube_data)
    
    return enriched_data

async def search_itunes(title: str, artist: str) -> Optional[Dict[str, Any]]:
    """Search iTunes/Apple Music API for track metadata."""
    try:
        async with httpx.AsyncClient() as client:
            # Construct search query
            search_term = f"{artist} {title}"
            params = {
                'term': search_term,
                'media': 'music',
                'entity': 'song',
                'limit': 1
            }
            
            response = await client.get(ITUNES_API_BASE, params=params)
            response.raise_for_status()
            
            data = response.json()
            if data.get('results'):
                result = data['results'][0]
                
                return {
                    'apple_music_url': result.get('trackViewUrl'),
                    'artwork_url': result.get('artworkUrl100'),
                    'release_year': result.get('releaseDate', '').split('-')[0] if result.get('releaseDate') else None,
                    'genre': result.get('primaryGenreName', ''),
                    'album': result.get('collectionName', ''),
                    'duration': result.get('trackTimeMillis', 0) / 1000 if result.get('trackTimeMillis') else None
                }
    except Exception as e:
        print(f"iTunes search error: {e}")
    
    return None

async def search_youtube(title: str, artist: str) -> Optional[Dict[str, Any]]:
    """Search YouTube API for track video."""
    if not YOUTUBE_API_KEY:
        return None
    
    try:
        async with httpx.AsyncClient() as client:
            # Construct search query
            search_term = f"{artist} {title} official"
            params = {
                'part': 'snippet',
                'q': search_term,
                'type': 'video',
                'maxResults': 1,
                'key': YOUTUBE_API_KEY
            }
            
            response = await client.get(YOUTUBE_API_BASE, params=params)
            response.raise_for_status()
            
            data = response.json()
            if data.get('items'):
                item = data['items'][0]
                video_id = item['id']['videoId']
                
                return {
                    'youtube_url': f"https://www.youtube.com/watch?v={video_id}"
                }
    except Exception as e:
        print(f"YouTube search error: {e}")
    
    return None

def format_duration(seconds: float) -> str:
    """Format duration in seconds to MM:SS format."""
    if not seconds:
        return ""
    
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    return f"{minutes:02d}:{seconds:02d}"
