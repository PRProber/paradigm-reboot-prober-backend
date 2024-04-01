import secrets
from typing import Type, Tuple, List
from datetime import datetime

from sqlalchemy.orm import Session

from ..model import schemas
from ..model.entities import User, PlayRecord, BestPlayRecord, SongLevel
from ..util import security, rating


def get_user(db: Session, username: str) -> User | None:
    db_user = db.query(User).filter(User.username == username).first()
    return db_user


def create_user(db: Session, user: schemas.UserCreate) -> User | None:
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        return None

    db_user = User(
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


def create_record(db: Session, record: schemas.PlayRecordCreate, user: User):
    """Record
    Create a play record.
    :param db: SQLAlchemy.orm Session
    :param record: record details
    :param user: validated user
    :return: record entity
    """

    db_song_level: SongLevel | None \
        = (db.query(SongLevel).filter(SongLevel.song_level_id == record.song_level_id).first())
    if db_song_level is None:
        raise RuntimeError("Song level does not exist")

    db_record = PlayRecord(
        song_level_id=record.song_level_id,
        record_time=datetime.now(),
        username=record.username,
        score=record.score,
        rating=rating.single_rating(db_song_level.level, record.score),
    )

    db.add(db_record)
    db.commit()
    db.refresh(db_record)

    db_best_record: BestPlayRecord | None \
        = (db.query(BestPlayRecord).filter(BestPlayRecord.play_record.song.song_id == record.song_level_id).one_or_none())
    if db_best_record is not None:
        best_record: PlayRecord = db_best_record.play_record
        if db_record.score > best_record.score:
            setattr(db_best_record, "play_record", db_record)
            db.commit()
            db.refresh(db_best_record)
    else:
        best_play_record: BestPlayRecord = BestPlayRecord(
            play_record_id=db_record.play_record_id,
        )
        db.add(best_play_record)
        db.commit()
        db.refresh(best_play_record)

    return db_record


def get_all_records(db: Session, username: str) -> List[Type[PlayRecord]]:
    records: List[Type[PlayRecord]] \
        = db.query(PlayRecord).filter(PlayRecord.username == username).all()
    return records


def get_best_records(db: Session, username: str, underflow: int = 0) \
        -> Tuple[List[Type[PlayRecord]], List[Type[PlayRecord]]]:
    """
    Get best play records of a user. Returns a tuple. The first element is the list of records of old version (b35),
    and the second element is the list of records of new version (b15).
    :param db: SQLAlchemy.orm Session
    :param username: the username of the user
    :param underflow: underflow records threshold
    :return: (list, list) like tuple
    """
    b35: List[Type[PlayRecord]] \
        = (db.query(BestPlayRecord)
           .filter(BestPlayRecord.play_record.username == username, BestPlayRecord.play_record.song.b15 is False)
           .order_by(BestPlayRecord.play_record.rating.desc()).limit(35 + underflow).all())
    b15: List[Type[PlayRecord]] \
        = (db.query(BestPlayRecord)
           .filter(BestPlayRecord.play_record.username == username, BestPlayRecord.play_record.song.b15 is True)
           .order_by(BestPlayRecord.play_record.rating.desc()).limit(15 + underflow).all())

    return b35, b15
