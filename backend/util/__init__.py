from sqlalchemy.orm import Session

from backend.model import entities, schemas, database


class SongLevelInfo:
    def __init__(self, song: entities.Song):
        for key in schemas.SongLevelInfo.model_fields.keys():
            if hasattr(song, key):
                setattr(self, key, getattr(song, key))
            else:
                setattr(self, key, None)


def init_db():
    database.Base.metadata.create_all(bind=database.engine)

    with database.Session(database.engine) as db:
        init_difficulties(db)


def init_difficulties(db: Session):
    diffs = ["Detected", "Invaded", "Massive"]
    db_diffs = [entities.Difficulty(name=diff) for diff in diffs]
    db.add_all(db_diffs)
    db.commit()
