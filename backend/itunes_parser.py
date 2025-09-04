import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Dict, List, Any, Optional
import re

def parse_itunes_library_xml(xml_content: bytes) -> Dict[str, Any]:
    """
    Parse iTunes Library XML file (plist format) and extract playlist and track information.
    This handles the specific structure used by iTunes library exports.
    """
    try:
        root = ET.fromstring(xml_content)
    except ET.ParseError as e:
        raise ValueError(f"Invalid XML format: {str(e)}")
    
    # Verify this is an iTunes library file
    if root.tag != 'plist':
        raise ValueError("Not a valid iTunes library file (missing plist root)")
    
    result = {
        'title': 'iTunes Library Import',
        'description': 'Imported from iTunes Library',
        'class_date': None,
        'tracks': []
    }
    
    # Find the main dict element
    main_dict = root.find('dict')
    if main_dict is None:
        raise ValueError("Invalid iTunes library structure")
    
    # Extract library metadata
    library_info = parse_dict_element(main_dict)
    
    # Extract the date if available
    if 'Date' in library_info:
        result['class_date'] = parse_itunes_date(library_info['Date'])
    
    # Find tracks section
    tracks_dict = None
    for i, child in enumerate(main_dict):
        if child.tag == 'key' and child.text == 'Tracks':
            # Next element should be the tracks dict
            if i + 1 < len(main_dict):
                tracks_dict = main_dict[i + 1]
            break
    
    if tracks_dict is None or tracks_dict.tag != 'dict':
        raise ValueError("No tracks found in iTunes library")
    
    # Parse all tracks
    tracks = []
    track_elements = []
    
    # Collect all track elements (they're key-value pairs)
    for i, child in enumerate(tracks_dict):
        if child.tag == 'key':
            # This is a track ID, next element should be the track dict
            if i + 1 < len(tracks_dict):
                track_dict = tracks_dict[i + 1]
                if track_dict.tag == 'dict':
                    track_elements.append(track_dict)
    
    for track_dict in track_elements:
        track_data = parse_track_dict(track_dict)
        if track_data:
            tracks.append(track_data)
    
    result['tracks'] = tracks
    return result

def parse_dict_element(dict_elem) -> Dict[str, Any]:
    """Parse a dict element from plist format into a Python dictionary."""
    result = {}
    children = list(dict_elem)
    
    for i in range(0, len(children), 2):
        if i + 1 >= len(children):
            break
            
        key_elem = children[i]
        value_elem = children[i + 1]
        
        if key_elem.tag == 'key':
            key = key_elem.text
            value = parse_plist_value(value_elem)
            result[key] = value
    
    return result

def parse_plist_value(value_elem) -> Any:
    """Parse a plist value element into Python value."""
    if value_elem.tag == 'string':
        return value_elem.text
    elif value_elem.tag == 'integer':
        return int(value_elem.text)
    elif value_elem.tag == 'real':
        return float(value_elem.text)
    elif value_elem.tag == 'true':
        return True
    elif value_elem.tag == 'false':
        return False
    elif value_elem.tag == 'date':
        return value_elem.text
    elif value_elem.tag == 'dict':
        return parse_dict_element(value_elem)
    else:
        return value_elem.text

def parse_track_dict(track_dict) -> Optional[Dict[str, Any]]:
    """Parse a track dictionary from iTunes format."""
    track_info = parse_dict_element(track_dict)
    
    # Skip if no name or artist
    if not track_info.get('Name') or not track_info.get('Artist'):
        return None
    
    # Convert Total Time from milliseconds to seconds
    total_time = track_info.get('Total Time', 0)
    if total_time:
        duration_seconds = total_time / 1000
        duration_minutes = int(duration_seconds // 60)
        duration_remaining_seconds = int(duration_seconds % 60)
        duration_formatted = f"{duration_minutes}:{duration_remaining_seconds:02d}"
    else:
        duration_formatted = None
    
    # Clean up artist name (remove HTML entities)
    artist = track_info.get('Artist', '')
    if artist:
        artist = artist.replace('&#38;', '&')
    
    track_data = {
        'position': 0,  # Will be set when adding to playlist
        'title': track_info.get('Name', ''),
        'artist': artist,
        'album': track_info.get('Album', ''),
        'duration': duration_seconds,  # Store as seconds for database
        'bpm': track_info.get('BPM'),
        'genre': track_info.get('Genre', ''),
        'release_year': track_info.get('Year'),
        'notes': f"iTunes Track ID: {track_info.get('Track ID', 'Unknown')}"
    }
    
    # Add additional metadata to notes if available
    additional_info = []
    if track_info.get('Kind'):
        additional_info.append(f"File Type: {track_info.get('Kind')}")
    if track_info.get('Bit Rate'):
        additional_info.append(f"Bit Rate: {track_info.get('Bit Rate')} kbps")
    if track_info.get('Sample Rate'):
        additional_info.append(f"Sample Rate: {track_info.get('Sample Rate')} Hz")
    if track_info.get('Play Count', 0) > 0:
        additional_info.append(f"Play Count: {track_info.get('Play Count')}")
    
    if additional_info:
        track_data['notes'] += f" | {' | '.join(additional_info)}"
    
    return track_data

def parse_itunes_date(date_str: str) -> Optional[str]:
    """Parse iTunes date format to ISO date string."""
    try:
        # iTunes dates are in ISO format: 2024-10-03T18:16:12Z
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d')
    except (ValueError, AttributeError):
        return None

def detect_itunes_library(xml_content: bytes) -> bool:
    """Check if the XML content is an iTunes library file."""
    try:
        root = ET.fromstring(xml_content)
        if root.tag != 'plist':
            return False
        
        # Check for iTunes-specific elements
        main_dict = root.find('dict')
        if main_dict is None:
            return False
        
        library_info = parse_dict_element(main_dict)
        
        # Check for iTunes-specific keys
        itunes_keys = ['Application Version', 'Library Persistent ID', 'Tracks']
        return any(key in library_info for key in itunes_keys)
        
    except Exception:
        return False
