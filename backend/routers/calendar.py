from typing import List
from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import Playlist, Admin
from schemas import CalendarEvent
from auth import get_current_admin

router = APIRouter()

@router.get("/events", response_model=List[CalendarEvent])
async def get_calendar_events(
    start_date: date = None,
    end_date: date = None,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    query = db.query(Playlist).filter(
        Playlist.created_by == current_admin.id
    )
    
    if start_date:
        query = query.filter(Playlist.class_date >= start_date)
    if end_date:
        query = query.filter(Playlist.class_date <= end_date)
    
    playlists = query.all()
    
    events = []
    for playlist in playlists:
        events.append(CalendarEvent(
            id=playlist.id,
            title=playlist.title,
            start=playlist.class_date,
            end=playlist.class_date,  # Single day events
            is_published=playlist.is_published,
            tracks_count=len(playlist.tracks)
        ))
    
    return events

@router.get("/month/{year}/{month}", response_model=List[CalendarEvent])
async def get_month_events(
    year: int,
    month: int,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    # Get first and last day of the month
    start_date = date(year, month, 1)
    if month == 12:
        end_date = date(year + 1, 1, 1)
    else:
        end_date = date(year, month + 1, 1)
    
    return await get_calendar_events(
        start_date=start_date,
        end_date=end_date,
        db=db,
        current_admin=current_admin
    )

@router.get("/day/{year}/{month}/{day}", response_model=List[CalendarEvent])
async def get_day_events(
    year: int,
    month: int,
    day: int,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    target_date = date(year, month, day)
    return await get_calendar_events(
        start_date=target_date,
        end_date=target_date,
        db=db,
        current_admin=current_admin
    )
