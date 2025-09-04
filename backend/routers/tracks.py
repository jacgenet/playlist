from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import Track, Playlist, Admin
from schemas import TrackCreate, TrackUpdate, TrackResponse
from auth import get_current_admin

router = APIRouter()

@router.get("/playlist/{playlist_id}", response_model=List[TrackResponse])
async def get_playlist_tracks(
    playlist_id: int,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    # Verify playlist ownership
    playlist = db.query(Playlist).filter(
        Playlist.id == playlist_id,
        Playlist.created_by == current_admin.id
    ).first()
    
    if not playlist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Playlist not found"
        )
    
    tracks = db.query(Track).filter(
        Track.playlist_id == playlist_id
    ).order_by(Track.position).all()
    
    return tracks

@router.post("/playlist/{playlist_id}", response_model=TrackResponse)
async def create_track(
    playlist_id: int,
    track_data: TrackCreate,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    # Verify playlist ownership
    playlist = db.query(Playlist).filter(
        Playlist.id == playlist_id,
        Playlist.created_by == current_admin.id
    ).first()
    
    if not playlist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Playlist not found"
        )
    
    track = Track(
        playlist_id=playlist_id,
        **track_data.dict()
    )
    db.add(track)
    db.commit()
    db.refresh(track)
    return track

@router.put("/{track_id}", response_model=TrackResponse)
async def update_track(
    track_id: int,
    track_data: TrackUpdate,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    # Get track and verify playlist ownership
    track = db.query(Track).join(Playlist).filter(
        Track.id == track_id,
        Playlist.created_by == current_admin.id
    ).first()
    
    if not track:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Track not found"
        )
    
    update_data = track_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(track, field, value)
    
    db.commit()
    db.refresh(track)
    return track

@router.delete("/{track_id}")
async def delete_track(
    track_id: int,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    # Get track and verify playlist ownership
    track = db.query(Track).join(Playlist).filter(
        Track.id == track_id,
        Playlist.created_by == current_admin.id
    ).first()
    
    if not track:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Track not found"
        )
    
    db.delete(track)
    db.commit()
    return {"message": "Track deleted successfully"}

@router.post("/{track_id}/reorder")
async def reorder_tracks(
    track_id: int,
    new_position: int,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    # Get track and verify playlist ownership
    track = db.query(Track).join(Playlist).filter(
        Track.id == track_id,
        Playlist.created_by == current_admin.id
    ).first()
    
    if not track:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Track not found"
        )
    
    # Update positions of other tracks
    if new_position < track.position:
        # Moving up - shift tracks down
        db.query(Track).filter(
            Track.playlist_id == track.playlist_id,
            Track.position >= new_position,
            Track.position < track.position
        ).update({Track.position: Track.position + 1})
    else:
        # Moving down - shift tracks up
        db.query(Track).filter(
            Track.playlist_id == track.playlist_id,
            Track.position > track.position,
            Track.position <= new_position
        ).update({Track.position: Track.position - 1})
    
    # Update the track's position
    track.position = new_position
    db.commit()
    
    return {"message": "Track reordered successfully"}
