from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class Admin(Base):
    __tablename__ = "admins"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Playlist(Base):
    __tablename__ = "playlists"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    class_date = Column(DateTime(timezone=True), nullable=False)
    is_published = Column(Boolean, default=False)
    created_by = Column(Integer, ForeignKey("admins.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    creator = relationship("Admin", back_populates="playlists")
    tracks = relationship("Track", back_populates="playlist", cascade="all, delete-orphan")

class Track(Base):
    __tablename__ = "tracks"
    
    id = Column(Integer, primary_key=True, index=True)
    playlist_id = Column(Integer, ForeignKey("playlists.id"), nullable=False)
    position = Column(Integer, nullable=False)
    title = Column(String, nullable=False)
    artist = Column(String, nullable=False)
    album = Column(String)
    duration = Column(Float)  # Duration in seconds
    bpm = Column(Integer)
    genre = Column(String)
    notes = Column(Text)
    
    # External links
    apple_music_url = Column(String)
    youtube_url = Column(String)
    spotify_url = Column(String)
    
    # Metadata
    artwork_url = Column(String)
    release_year = Column(Integer)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    playlist = relationship("Playlist", back_populates="tracks")

# Add back reference to Admin
Admin.playlists = relationship("Playlist", back_populates="creator")
