from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from database import get_db
from models import Playlist, Track, Admin
from schemas import PlaylistCreate, PlaylistUpdate, PlaylistResponse, PlaylistWithTracks, XMLImportResult
from auth import get_current_admin
from xml_parser import parse_playlist_xml
from metadata_enrichment import enrich_track_metadata

router = APIRouter()

@router.get("/", response_model=List[PlaylistResponse])
async def get_playlists(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    playlists = db.query(Playlist).filter(
        Playlist.created_by == current_admin.id
    ).offset(skip).limit(limit).all()
    return playlists

@router.get("/{playlist_id}", response_model=PlaylistWithTracks)
async def get_playlist(
    playlist_id: int,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    playlist = db.query(Playlist).filter(
        Playlist.id == playlist_id,
        Playlist.created_by == current_admin.id
    ).first()
    
    if not playlist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Playlist not found"
        )
    
    return playlist

@router.post("/", response_model=PlaylistResponse)
async def create_playlist(
    playlist_data: PlaylistCreate,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    db_playlist = Playlist(
        **playlist_data.dict(),
        created_by=current_admin.id
    )
    db.add(db_playlist)
    db.commit()
    db.refresh(db_playlist)
    return db_playlist

@router.put("/{playlist_id}", response_model=PlaylistResponse)
async def update_playlist(
    playlist_id: int,
    playlist_data: PlaylistUpdate,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    playlist = db.query(Playlist).filter(
        Playlist.id == playlist_id,
        Playlist.created_by == current_admin.id
    ).first()
    
    if not playlist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Playlist not found"
        )
    
    update_data = playlist_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(playlist, field, value)
    
    db.commit()
    db.refresh(playlist)
    return playlist

@router.delete("/{playlist_id}")
async def delete_playlist(
    playlist_id: int,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    playlist = db.query(Playlist).filter(
        Playlist.id == playlist_id,
        Playlist.created_by == current_admin.id
    ).first()
    
    if not playlist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Playlist not found"
        )
    
    db.delete(playlist)
    db.commit()
    return {"message": "Playlist deleted successfully"}

@router.post("/import-xml", response_model=XMLImportResult)
async def import_xml_playlist(
    file: UploadFile = File(...),
    class_date: str = None,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    if not file.filename.endswith('.xml'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an XML file"
        )
    
    try:
        content = await file.read()
        parsed_data = parse_playlist_xml(content)
        
        # Create playlist
        playlist = Playlist(
            title=parsed_data.get('title', f'Imported Playlist - {file.filename}'),
            description=parsed_data.get('description', ''),
            class_date=parsed_data.get('class_date'),
            created_by=current_admin.id
        )
        db.add(playlist)
        db.commit()
        db.refresh(playlist)
        
        # Add tracks
        tracks_imported = 0
        errors = []
        
        for track_data in parsed_data.get('tracks', []):
            try:
                # Enrich metadata
                enriched_data = await enrich_track_metadata(track_data)
                
                track = Track(
                    playlist_id=playlist.id,
                    **enriched_data
                )
                db.add(track)
                tracks_imported += 1
            except Exception as e:
                errors.append(f"Error importing track {track_data.get('title', 'Unknown')}: {str(e)}")
        
        db.commit()
        
        return XMLImportResult(
            success=True,
            message=f"Successfully imported {tracks_imported} tracks",
            playlist_id=playlist.id,
            tracks_imported=tracks_imported,
            errors=errors
        )
        
    except Exception as e:
        return XMLImportResult(
            success=False,
            message=f"Import failed: {str(e)}",
            errors=[str(e)]
        )

# Public endpoint for published playlists
@router.get("/public/{playlist_id}", response_model=PlaylistWithTracks)
async def get_public_playlist(playlist_id: int, db: Session = Depends(get_db)):
    playlist = db.query(Playlist).filter(
        Playlist.id == playlist_id,
        Playlist.is_published == True
    ).first()
    
    if not playlist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Playlist not found or not published"
        )
    
    return playlist
