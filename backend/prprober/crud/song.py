from sqlalchemy.orm import Session
from ..model import schemas
from ..model.entities import Song, SongLevel


REPLACEABLE_ATTRIBUTES = [
    'title', 'artist', 'cover', 'illustrator', 'bpm', 'b15', 'album', 'wiki_id'
]


def get_all_songs(db: Session):
    return db.query(Song).all()


def get_single_song_by_id(db: Session, song_id: int):
    return db.query(Song).filter(Song.song_id == song_id).one_or_none()


def get_single_song_by_wiki_id(db: Session, song_id: str):
    return db.query(Song).filter(Song.wiki_id == song_id).one_or_none()


def create_song(db: Session, song: schemas.SongCreate):
    db_song = Song(
        title=song.title,
        artist=song.artist,
        genre=song.genre,
        cover=song.cover,
        illustrator=song.illustrator,
        version=song.version,
        b15=song.b15,
        album=song.album,
        bpm=song.bpm,
        length=song.length,
        wiki_id=song.wiki_id
    )
    db.add(db_song)
    db.commit()
    # 获得新的 song_id
    db.refresh(db_song)

    db_levels = [
        SongLevel(
            song_id=db_song.song_id,
            difficulty_id=level.difficulty_id,
            level=level.level,
            level_design=level.level_design,
            notes=level.notes,
        )
        for level in song.song_levels
    ]
    db.add_all(db_levels)
    db.commit()
    db.refresh(db_song)

    return db_song


def update_song(db: Session, song: schemas.SongUpdate):
    db_song: Song | None \
        = db.query(Song).filter(Song.song_id == song.song_id).first()
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
                    new_level = SongLevel(
                        song_id=db_song.song_id,
                        difficulty_id=diff_id,
                        level=song_levels[diff_id].level,
                        level_design=song_levels[diff_id].level_design
                    )
                    db.add(new_level)

    db.commit()
    db.refresh(db_song)

    return db_song
