import secrets
from typing import Type, List
from datetime import datetime

from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import AmbiguousForeignKeysError

from ..model import entities, schemas
from ..model.entities import User, PlayRecord
from ..util import security, rating


def get_user(db: Session, username: str) -> User | None:
    db_user = db.query(User).filter(entities.User.username == username).first()
    return db_user


def create_user(db: Session, user: schemas.UserCreate) -> User | None:
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        return None

    db_user = entities.User(
        username=user.username,
        encoded_password=security.encode_password(user.password),
        email=user.email,
        qq_number=user.qq_number,
        account=user.account,
        account_number=user.account_number,
        uuid=user.uuid,
        anonymous_probe=user.anonymous_probe,
        upload_token=secrets.token_hex(256),
        is_active=True,
        is_admin=False
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


def create_record(db: Session, record: schemas.PlayRecordCreate) -> entities.PlayRecord:
    """
    Create a play record.
    :param db: SQLAlchemy.orm Session
    :param record: record details
    :return: record entity
    """
    db_song_level: entities.SongLevel | None \
        = (db.query(entities.SongLevel).filter(entities.SongLevel.song_level_id == record.song_level_id).first())
    if db_song_level is None:
        raise HTTPException(status_code=400, detail="Song level doesn't exist")

    db_record = entities.PlayRecord(
        song_level_id=record.song_level_id,
        record_time=datetime.now(),
        username=record.username,
        score=record.score,
        rating=rating.single_rating(db_song_level.level, record.score),
    )
    try:
        db.add(db_record)
        db.commit()
        db.refresh(db_record)
        return db_record
    except AmbiguousForeignKeysError:
        raise HTTPException(status_code=400, detail="User doesn't exist")


def get_all_records(db: Session, username: str) -> List[Type[PlayRecord]]:
    records: List[Type[PlayRecord]] \
        = db.query(PlayRecord).filter(PlayRecord.username == username).all()
    return records


def get_best_records(db: Session, username: str) -> List[Type[PlayRecord]]:
    records: List[Type[PlayRecord]] \
        = (db.query(PlayRecord)
           .filter(PlayRecord.username == username)
           .order_by(PlayRecord.rating.desc()).distinct(PlayRecord.song_level_id).all())
    return records


def get_best50_records(db: Session, username: str, underflow: int = 0) \
        -> tuple[list[Type[PlayRecord]], list[Type[PlayRecord]]]:
    """
    Get best play records of a user. Returns a tuple. The first element is the list of records of old version (b35),
    and the second element is the list of records of new version (b15).
    :param db: SQLAlchemy.orm Session
    :param username: the username of the user
    :param underflow: underflow records threshold
    :return: (list, list) like tuple
    """
    b35: List[Type[PlayRecord]] \
        = (db.query(PlayRecord)
           .filter(PlayRecord.username == username and PlayRecord.song_level.song.b15 is False)
           .order_by(PlayRecord.rating.desc()).distinct(PlayRecord.song_level_id).limit(35 + underflow).all())
    b15: List[Type[PlayRecord]] \
        = (db.query(PlayRecord)
           .filter(PlayRecord.username == username and PlayRecord.song_level.song.b15 is True)
           .order_by(PlayRecord.rating.desc()).distinct(PlayRecord.song_level_id).limit(15 + underflow).all())


    return b35, b15
