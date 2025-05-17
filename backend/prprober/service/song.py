import os
import shutil

from typing import List

from sqlalchemy.orm import Session
from fastapi import HTTPException
from fastapi_cache.decorator import cache

from backend import config
from ..model import schemas, entities
from ..crud import song as crud
from .. import util


def song_to_levels(song: entities.Song) -> List[util.SongLevelInfo]:
    """
    Convert a DAO layer song entity to doc-formatted song level objects.
    :param song: DAO layer song entity to be converted
    :return: A list of formatted song levels.
    """
    song_levels = []
    for level in song.song_levels:
        song_level = util.SongLevelInfo(level)
        song_level.difficulty = level.difficulty.name
        song_levels.append(song_level)

    return song_levels


@cache(expire=60)
async def get_all_song_levels(db: Session):
    songs: List[entities.Song] = crud.get_all_songs(db)
    song_levels: List[util.SongLevelInfo] = []

    for song in songs:
        song_levels.extend(song_to_levels(song))

    return song_levels


@cache(expire=60)
async def get_single_by_id(db: Session, song_id: str, src: str):
    if src == 'prp':
        song = crud.get_single_song_by_id(db, int(song_id))
    elif src == 'wiki':
        song = crud.get_single_song_by_wiki_id(db, song_id)
    else:
        song = None
    if song is None:
        raise HTTPException(status_code=404, detail="Song doesn't exist")
    wrapped_song = util.SongInfo(song)
    # 展开 level.difficulty.name，不然 schema 没法序列化
    wrapped_song.song_levels = [
        schemas.LevelInfo.model_validate({
            key: getattr(level, key) if key != 'difficulty' else getattr(level, key).name
            for key in schemas.LevelInfo.model_fields.keys()
        }) for level in song.song_levels
    ]
    return wrapped_song


def create_song(db: Session, song: schemas.SongCreate):
    return song_to_levels(crud.create_song(db, song))


def update_song(db: Session, song: schemas.SongUpdate):
    return song_to_levels(crud.update_song(db, song))


def get_cover(filename: str):
    if filename is not None and os.path.isfile(config.UPLOAD_COVER_PATH + filename):
        shutil.copyfile(config.UPLOAD_COVER_PATH + filename, config.RESOURCE_COVER_PATH + filename)
        shutil.copyfile(config.UPLOAD_COVER_PATH + filename, config.RESOURCE_COVER_STATIC_PATH + filename)
