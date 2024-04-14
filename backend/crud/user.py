import secrets
from typing import Type, Tuple, List
from datetime import datetime

from dateutil.relativedelta import relativedelta
from sqlalchemy import Row, select
from sqlalchemy.orm import Session

from ..model import schemas
from ..model.entities import User, PlayRecord, BestPlayRecord, SongLevel, Song, Best50Trends
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
        upload_token=secrets.token_hex(32),
        is_active=True,
        is_admin=False
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


def create_record(db: Session, record: schemas.PlayRecordCreate, username: str,  is_replaced: bool = False) -> PlayRecord:
    """Record
    Create a play record.
    :param username:
    :param db: SQLAlchemy.orm Session
    :param record: record details
    :param is_replaced: whether to replace the best record or not
    :return: record entity
    """

    db_song_level: SongLevel | None \
        = (db.query(SongLevel).filter(SongLevel.song_level_id == record.song_level_id).first())
    if db_song_level is None:
        raise RuntimeError("Song level does not exist")

    db_record = PlayRecord(
        song_level_id=record.song_level_id,
        record_time=datetime.now(),
        username=username,
        score=record.score,
        rating=rating.single_rating(db_song_level.level, record.score),
    )

    db.add(db_record)
    db.commit()
    db.refresh(db_record)

    db_best_record: BestPlayRecord | None \
        = (db.query(BestPlayRecord)
           .join(PlayRecord).filter(PlayRecord.song_level_id == record.song_level_id).one_or_none())
    if db_best_record:
        best_record: PlayRecord = db_best_record.play_record
        if is_replaced or db_record.score > best_record.score:
            setattr(db_best_record, "play_record", db_record)
            setattr(db_best_record, "play_record_id", db_record.play_record_id)
            db.commit()
            db.refresh(db_best_record)
    else:
        best_play_record: BestPlayRecord = BestPlayRecord(
            play_record_id=db_record.play_record_id,
            play_record=db_record,
        )
        db.add(best_play_record)
        db.commit()
        db.refresh(best_play_record)

    return db_record


def get_all_records(db: Session, username: str) -> List[Type[PlayRecord]]:
    records: List[Type[PlayRecord]] \
        = db.query(PlayRecord).filter(PlayRecord.username == username).all()
    return records


def get_best_records(db: Session, username: str, underflow: int = 0):
    """
    Get best play records of a user. Returns a tuple. The first element is the list of records of old version (b35),
    and the second element is the list of records of new version (b15).
    :param db: SQLAlchemy.orm Session
    :param username: the username of the user
    :param underflow: underflow records threshold
    :return: (list, list) like tuple
    """

    statement = \
        (select(BestPlayRecord, PlayRecord).
         join(BestPlayRecord.play_record).
         join(PlayRecord.song_level).
         join(SongLevel.song).
         filter(PlayRecord.username == username))

    b35_statement = statement.filter(Song.b15 == 0).order_by(PlayRecord.rating.desc()).limit(35 + underflow)
    b35 = db.execute(b35_statement).all()
    b15_statement = statement.filter(Song.b15 == 1).order_by(PlayRecord.rating.desc()).limit(15 + underflow)
    b15 = db.execute(b15_statement).all()

    return b35, b15


def remove_b50_record(db: Session, record: Best50Trends):
    pass


def update_b50_record(db: Session, username: str) -> Best50Trends:
    b35, b15 = get_best_records(db, username)

    b50rating: float = 0
    for record in b35:
        b50rating += record[1].rating
    for record in b15:
        b50rating += record[1].rating

    db_b50_record: Best50Trends = Best50Trends(
        username=username,
        b50rating=b50rating,
        record_time=datetime.now(),
        is_valid=True,
    )

    db.add(db_b50_record)
    db.commit()
    db.refresh(db_b50_record)

    return db_b50_record


def get_b50_trends(db: Session, username: str, scope: str | None = "month") -> List[Type[Best50Trends]]:
    current_time: datetime = datetime.now()
    limit_time: datetime = current_time
    if scope == "month":
        limit_time = current_time - relativedelta(months=1)
    elif scope == "season":
        limit_time = current_time - relativedelta(months=3)
    elif scope == "year":
        limit_time = current_time - relativedelta(years=1)

    trends: List[Type[Best50Trends]] = \
        (db.query(Best50Trends).
         filter(Best50Trends.username == username,
                Best50Trends.is_valid == 1,
                Best50Trends.record_time <= current_time,
                Best50Trends.record_time >= limit_time).
         order_by(Best50Trends.record_time).all())
    return trends
