import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Dict, List, Any
import re
from itunes_parser import parse_itunes_library_xml, detect_itunes_library

def parse_playlist_xml(xml_content: bytes) -> Dict[str, Any]:
    """
    Parse XML playlist file and extract playlist and track information.
    Supports common XML formats used by DJ software and playlist managers.
    Also supports iTunes Library XML files.
    """
    # Check if this is an iTunes library file
    if detect_itunes_library(xml_content):
        return parse_itunes_library_xml(xml_content)
    
    try:
        root = ET.fromstring(xml_content)
    except ET.ParseError as e:
        raise ValueError(f"Invalid XML format: {str(e)}")
    
    result = {
        'title': '',
        'description': '',
        'class_date': None,
        'tracks': []
    }
    
    # Try to extract playlist metadata
    playlist_elem = root.find('.//playlist') or root.find('.//Playlist') or root
    if playlist_elem is not None:
        result['title'] = get_text_content(playlist_elem, ['title', 'name', 'Title', 'Name'])
        result['description'] = get_text_content(playlist_elem, ['description', 'comment', 'Description', 'Comment'])
        
        # Try to extract date from various possible fields
        date_str = get_text_content(playlist_elem, ['date', 'created', 'Date', 'Created'])
        if date_str:
            result['class_date'] = parse_date(date_str)
    
    # Extract tracks
    tracks = []
    track_elements = root.findall('.//track') or root.findall('.//Track') or root.findall('.//song') or root.findall('.//Song')
    
    for i, track_elem in enumerate(track_elements):
        track_data = parse_track_element(track_elem, i + 1)
        if track_data:
            tracks.append(track_data)
    
    result['tracks'] = tracks
    return result

def parse_track_element(track_elem, position: int) -> Dict[str, Any]:
    """Parse individual track element from XML."""
    track_data = {
        'position': position,
        'title': '',
        'artist': '',
        'album': '',
        'duration': None,
        'bpm': None,
        'genre': '',
        'notes': ''
    }
    
    # Extract track information from various possible field names
    track_data['title'] = get_text_content(track_elem, ['title', 'name', 'Title', 'Name', 'track'])
    track_data['artist'] = get_text_content(track_elem, ['artist', 'Artist', 'creator', 'Creator'])
    track_data['album'] = get_text_content(track_elem, ['album', 'Album', 'collection', 'Collection'])
    track_data['genre'] = get_text_content(track_elem, ['genre', 'Genre', 'style', 'Style'])
    track_data['notes'] = get_text_content(track_elem, ['comment', 'Comment', 'notes', 'Notes'])
    
    # Parse duration
    duration_str = get_text_content(track_elem, ['duration', 'Duration', 'length', 'Length', 'time', 'Time'])
    if duration_str:
        track_data['duration'] = parse_duration(duration_str)
    
    # Parse BPM
    bpm_str = get_text_content(track_elem, ['bpm', 'BPM', 'tempo', 'Tempo'])
    if bpm_str:
        try:
            track_data['bpm'] = int(float(bpm_str))
        except (ValueError, TypeError):
            pass
    
    # Only return track if it has at least title and artist
    if track_data['title'] and track_data['artist']:
        return track_data
    return None

def get_text_content(element, field_names: List[str]) -> str:
    """Get text content from element using multiple possible field names."""
    for field_name in field_names:
        field_elem = element.find(field_name)
        if field_elem is not None and field_elem.text:
            return field_elem.text.strip()
    return ''

def parse_duration(duration_str: str) -> float:
    """Parse duration string to seconds."""
    if not duration_str:
        return None
    
    # Handle MM:SS format
    if ':' in duration_str:
        parts = duration_str.split(':')
        if len(parts) == 2:
            try:
                minutes, seconds = map(float, parts)
                return minutes * 60 + seconds
            except ValueError:
                pass
        elif len(parts) == 3:
            try:
                hours, minutes, seconds = map(float, parts)
                return hours * 3600 + minutes * 60 + seconds
            except ValueError:
                pass
    
    # Handle plain number (assume seconds)
    try:
        return float(duration_str)
    except ValueError:
        return None

def parse_date(date_str: str) -> datetime:
    """Parse date string to datetime object."""
    if not date_str:
        return None
    
    # Common date formats
    date_formats = [
        '%Y-%m-%d',
        '%Y-%m-%d %H:%M:%S',
        '%m/%d/%Y',
        '%d/%m/%Y',
        '%Y-%m-%dT%H:%M:%S',
        '%Y-%m-%dT%H:%M:%SZ'
    ]
    
    for fmt in date_formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    
    return None
