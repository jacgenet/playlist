from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import List, Optional

# Auth schemas
class AdminCreate(BaseModel):
    email: EmailStr
    password: str

class AdminLogin(BaseModel):
    email: EmailStr
    password: str

class AdminResponse(BaseModel):
    id: int
    email: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

# Track schemas
class TrackBase(BaseModel):
    title: str
    artist: str
    album: Optional[str] = None
    duration: Optional[float] = None
    bpm: Optional[int] = None
    genre: Optional[str] = None
    notes: Optional[str] = None
    apple_music_url: Optional[str] = None
    youtube_url: Optional[str] = None
    spotify_url: Optional[str] = None
    artwork_url: Optional[str] = None
    release_year: Optional[int] = None

class TrackCreate(TrackBase):
    position: int

class TrackUpdate(TrackBase):
    position: Optional[int] = None

class TrackResponse(TrackBase):
    id: int
    position: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Playlist schemas
class PlaylistBase(BaseModel):
    title: str
    description: Optional[str] = None
    class_date: datetime

class PlaylistCreate(PlaylistBase):
    pass

class PlaylistUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    class_date: Optional[datetime] = None
    is_published: Optional[bool] = None

class PlaylistResponse(PlaylistBase):
    id: int
    is_published: bool
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    tracks: List[TrackResponse] = []
    
    class Config:
        from_attributes = True

class PlaylistWithTracks(PlaylistResponse):
    tracks: List[TrackResponse] = []

# Calendar schemas
class CalendarEvent(BaseModel):
    id: int
    title: str
    start: datetime
    end: Optional[datetime] = None
    is_published: bool
    tracks_count: int
    
    class Config:
        from_attributes = True

# XML Import schemas
class XMLImportResult(BaseModel):
    success: bool
    message: str
    playlist_id: Optional[int] = None
    tracks_imported: int = 0
    errors: List[str] = []
