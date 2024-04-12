from typing import List

from sqlalchemy.orm import Session
from fastapi import HTTPException

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


def get_all_song_levels(db: Session):
    songs: List[entities.Song] = crud.get_all_songs(db)
    song_levels: List[util.SongLevelInfo] = []

    for song in songs:
        song_levels.extend(song_to_levels(song))

    return song_levels


def get_single_song_by_id(db: Session, song_id: int):
    song = crud.get_single_song_by_id(db, song_id)
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
