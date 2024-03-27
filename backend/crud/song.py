from sqlalchemy.orm import Session
from ..model import entities, schemas


REPLACEABLE_ATTRIBUTES = [
    'title', 'artist', 'cover', 'illustrator', 'bpm', 'b15', 'album'
]


def get_all_songs(db: Session):
    return db.query(entities.Song)


def create_song(db: Session, song: schemas.SongCreate):
    db_song = entities.Song(
        title=song.title,
        artist=song.artist,
        cover=song.cover,
        illustrator=song.illustrator,
        version=song.version,
        b15=song.b15,
        album=song.album,
        bpm=song.bpm
    )
    db.add(db_song)
    db.commit()
    # 获得新的 song_id
    db.refresh(db_song)

    db_levels = [
        entities.SongLevel(
            song_id=db_song.song_id,
            difficulty_id=level.difficulty_id,
            level=level.level,
            level_design=level.level_design,
        )
        for level in song.song_levels
    ]
    db.add_all(db_levels)
    db.commit()
    db.refresh(db_song)

    return db_song


def update_song(db: Session, song: schemas.SongUpdate):
    db_song: entities.Song | None \
        = db.query(entities.Song).filter(entities.Song.song_id == song.song_id).first()
    if db_song is not None:
        # 更新可以直接替换的歌曲属性
        for attr in REPLACEABLE_ATTRIBUTES:
            if hasattr(song, attr) and getattr(song, attr) is not None:
                setattr(db_song, attr, getattr(song, attr))
        # 更新定数，用难度进行匹配，没有的就当作新的难度添加
        if song.song_levels is not None:
            song_levels = {song_level.difficulty_id: song_level for song_level in song.song_levels}
            db_song_levels = {song_level.difficulty_id: song_level for song_level in db_song.song_levels}
            for diff_id in song_levels.keys():
                if diff_id in db_song_levels.keys():
                    db_song_levels[diff_id].level = song_levels[diff_id].level
                else:
                    new_level = entities.SongLevel(
                        song_id=db_song.song_id,
                        difficulty_id=diff_id,
                        level=song_levels[diff_id].level,
                        level_design=song_levels[diff_id].level_design
                    )
                    db.add(new_level)

    db.commit()
    db.refresh(db_song)

    return db_song
