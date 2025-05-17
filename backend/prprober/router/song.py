from fastapi import APIRouter, Depends, HTTPException
from fastapi_cache.decorator import cache
from sqlalchemy.orm import Session

from ..model import schemas, entities
from ..util.database import get_db
from ..service import song as song_service
from ..service import user as user_service

router = APIRouter()


@router.get('/songs', response_model=list[schemas.SongLevelInfo])
@cache(expire=600)
async def get_all_song_levels(db: Session = Depends(get_db)):
    song_levels = await song_service.get_all_song_levels(db)
    return sorted(song_levels, key=lambda x: x.song_level_id, reverse=True)


@router.get('/songs/{song_id}', response_model=schemas.Song)
@cache(expire=600)
async def get_single_song_info(song_id: str,
                               src: str = 'prp',
                               db: Session = Depends(get_db)):
    if src not in ('prp', 'wiki'):
        raise HTTPException(status_code=404, detail="Source doesn't exist")
    song = await song_service.get_single_by_id(db, song_id, src)
    return song


@router.post('/songs', response_model=list[schemas.SongLevelInfo])
async def create_song(song: schemas.SongCreate, db: Session = Depends(get_db),
                      user: entities.User = Depends(user_service.get_current_user)):
    if user.is_admin:
        song_service.get_cover(song.cover)
        song_levels = song_service.create_song(db, song)
        return song_levels
    else:
        raise HTTPException(status_code=403, detail="You are not admin")


@router.patch('/songs', response_model=list[schemas.SongLevelInfo])
async def update_song(song: schemas.SongUpdate, db: Session = Depends(get_db),
                      user: entities.User = Depends(user_service.get_current_user)):
    if user.is_admin:
        song_service.get_cover(song.cover)
        song_levels = song_service.update_song(db, song)
        return song_levels
    else:
        raise HTTPException(status_code=403, detail="You are not admin")
