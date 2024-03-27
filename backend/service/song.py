from typing import List

from sqlalchemy.orm import Session

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
        song_level = util.SongLevelInfo(song)
        # TODO: More elegant method
        setattr(song_level, "song_level_id", level.song_level_id)
        song_level.difficulty_id = level.difficulty_id
        song_level.difficulty = level.difficulty.name
        song_level.level = level.level
        song_level.fitting_level = level.fitting_level
        song_level.level_design = level.level_design

        song_levels.append(song_level)

    return song_levels


def get_all_song_levels(db: Session):
    songs: List[entities.Song] = crud.get_all_songs(db)
    song_levels: List[util.SongLevelInfo] = []

    for song in songs:
        song_levels.extend(song_to_levels(song))

    return song_levels


def create_song(db: Session, song: schemas.SongCreate):
    return song_to_levels(crud.create_song(db, song))


def update_song(db: Session, song: schemas.SongUpdate):
    return song_to_levels(crud.update_song(db, song))
