import json

from sqlalchemy.orm import Session
from sqlalchemy.exc import AmbiguousForeignKeysError

from ..model import database, entities
from ..model.schemas import SongCreate
from ..model.database import SessionLocal
from ..crud.song import create_song


def init_db():
    database.Base.metadata.create_all(bind=database.engine)
    #
    # with Session(database.engine) as db:
    #     init_difficulties(db)
    #     init_songs(db)


def init_difficulties(db: Session):
    diffs = ["Detected", "Invaded", "Massive"]
    db_diffs = [entities.Difficulty(name=diff) for diff in diffs]
    db.add_all(db_diffs)
    db.commit()


def init_songs(db: Session):
    songs: list
    try:
        with open('resources/formatted.json', 'r', encoding='utf-8') as f:
            songs = json.load(f)
    except FileNotFoundError | json.JSONDecodeError as e:
        print("Error occurs when initializing song information\n", e)

    for song in songs:
        song_create = SongCreate.model_validate(song)
        try:
            create_song(db, song_create)
        except AmbiguousForeignKeysError as e:
            print("Ambiguous foreign key error occurs when initializing song information\n", e)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
