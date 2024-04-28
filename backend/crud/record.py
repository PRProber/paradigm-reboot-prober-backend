from datetime import datetime
from typing import List, Type

from dateutil.relativedelta import relativedelta
from sqlalchemy import select, func, and_, or_, not_
from sqlalchemy.orm import Session

from ..model.schemas import PlayRecordCreate
from ..model.entities import PlayRecord, SongLevel, BestPlayRecord, Song, Best50Trends
from ..util import rating


def create_record(db: Session, record: PlayRecordCreate, username: str, is_replaced: bool = False) -> PlayRecord:
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
        = (db.query(BestPlayRecord).
           join(PlayRecord).
           filter(PlayRecord.song_level_id == record.song_level_id).
           filter(PlayRecord.username == username).one_or_none())
    if db_best_record:
        best_record: PlayRecord = db_best_record.play_record
        if is_replaced or db_record.score >= best_record.score:
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


def get_best50_records(db: Session, username: str, underflow: int = 0):
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

    b35_statement = statement.filter(not_(Song.b15)).order_by(PlayRecord.rating.desc()).limit(35 + underflow)
    b35 = db.execute(b35_statement).all()
    b15_statement = statement.filter(Song.b15).order_by(PlayRecord.rating.desc()).limit(15 + underflow)
    b15 = db.execute(b15_statement).all()

    return b35, b15


def get_statement(statement_base, page_size: int, page_index: int, sort_by: (str, int), order: bool):
    (key, belong) = sort_by
    if belong == 1:
        statement = \
            (statement_base.
             order_by(getattr(PlayRecord, key).desc() if order else getattr(PlayRecord, key).asc()).
             offset(page_size * (page_index - 1)).
             limit(page_size))
    elif belong == 2:
        statement = \
            (statement_base.
             join(PlayRecord.song_level).
             order_by(getattr(SongLevel, key).desc() if order else getattr(SongLevel, key).asc()).
             offset(page_size * (page_index - 1)).
             limit(page_size))
    elif belong == 3:
        statement = \
            (statement_base.
             join(PlayRecord.song_level).
             join(SongLevel.song).
             order_by(getattr(Song, key).desc() if order else getattr(Song, key).asc()).
             offset(page_size * (page_index - 1)).
             limit(page_size))
    else:
        raise Exception('Unexpected belong')
    return statement


def get_all_records(db: Session, username: str, page_size: int, page_index: int, sort_by: (str, int), order: bool):
    statement_base = \
        (select(PlayRecord).
         filter(PlayRecord.username == username))
    statement = get_statement(statement_base, page_size, page_index, sort_by, order)
    records = db.execute(statement).all()
    return records


def get_best_records(db: Session, username: str, page_size: int, page_index: int, sort_by: (str, int), order: bool):
    statement_base = \
        (select(BestPlayRecord, PlayRecord).
         join(BestPlayRecord.play_record).
         filter(PlayRecord.username == username))
    statement = get_statement(statement_base, page_size, page_index, sort_by, order)
    records = db.execute(statement).all()
    return records


def remove_b50_record(db: Session, record: Best50Trends):
    pass


def update_b50_record(db: Session, username: str) -> Best50Trends:
    b35, b15 = get_best50_records(db, username)

    b50rating: float = 0
    for record in b35:
        b50rating += record[1].rating
    for record in b15:
        b50rating += record[1].rating
    b50rating /= 5000

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
                Best50Trends.is_valid,
                Best50Trends.record_time >= limit_time).
         order_by(Best50Trends.record_time).all())
    return trends


def count_best_records(db: Session, username: str) -> int:
    count = int(db.query(func.count(BestPlayRecord.best_record_id))
                .join(PlayRecord).filter(PlayRecord.username == username).one()[0])
    return count


def count_all_records(db: Session, username: str) -> int:
    count = int(db.query(func.count(PlayRecord.play_record_id)).filter(PlayRecord.username == username).one()[0])
    return count


def get_all_levels_with_best_scores(db: Session, username: str):
    statement = \
        (select(SongLevel, PlayRecord.score, BestPlayRecord.best_record_id).
         outerjoin(PlayRecord,
                   and_(PlayRecord.song_level_id == SongLevel.song_level_id, PlayRecord.username == username)).
         outerjoin(BestPlayRecord, BestPlayRecord.play_record_id == PlayRecord.play_record_id).
         order_by(SongLevel.level.desc()))
    records = db.execute(statement).all()
    return records
