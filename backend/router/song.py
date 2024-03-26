from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.model import schemas
from backend.model.database import get_db
from backend.service import song as song_service

router = APIRouter()


@router.get('/v1/api/songs', response_model=list[schemas.SongLevelInfo])
async def get_all_song_levels(db: Session = Depends(get_db)):
    song_levels = song_service.get_all_song_levels(db)

    return song_levels


@router.post('/v1/api/songs', response_model=list[schemas.SongLevelInfo])
async def create_song(song: schemas.SongCreate, db: Session = Depends(get_db)):
    # TODO: Check authority
    song_levels = song_service.create_song(db, song)

    return song_levels


@router.patch('/v1/api/songs', response_model=list[schemas.SongLevelInfo])
async def update_song(song: schemas.SongUpdate, db: Session = Depends(get_db)):
    # TODO: Check authority
    song_levels = song_service.update_song(db, song)

    return song_levels
