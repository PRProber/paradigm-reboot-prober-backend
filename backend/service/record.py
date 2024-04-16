from typing import List, Tuple, Type

from fastapi import HTTPException
from sqlalchemy import Row
from sqlalchemy.exc import AmbiguousForeignKeysError
from sqlalchemy.orm import Session

from ..crud import record as crud
from backend import util
from backend.model.entities import PlayRecord, BestPlayRecord, Best50Trends
from backend.model.schemas import PlayRecordCreate


def create_record(db: Session, username: str, records: list[PlayRecordCreate], is_replaced: bool = False) \
        -> List[PlayRecord]:
    response_records = []
    try:
        for record in records:
            response_records.append(crud.create_record(db, record, username, is_replaced))
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=e)
    except AmbiguousForeignKeysError:
        raise HTTPException(status_code=400, detail="User doesn't exist or song doesn't exist")
    except Exception as e:
        raise HTTPException(status_code=400, detail=e)
    return response_records


def get_all_records(db: Session, username: str, page_size: int, page_index: int, sort_by: str, order: str):
    unwrapped_records = crud.get_all_records(db, username, page_size, page_index, sort_by, order == "desc")
    records: List[util.PlayRecordInfo] = []
    for record in unwrapped_records:
        records.append(util.PlayRecordInfo(record[0]))
    return records


def wrap_record(record: Row[Tuple[BestPlayRecord, PlayRecord]]) -> util.PlayRecordInfo:
    best_record = util.PlayRecordInfo(record[1])
    return best_record


def get_best50_records(db: Session, username: str, underflow: int = 0):
    b35_records, b15_records = crud.get_best50_records(db, username, underflow)
    records: List[util.PlayRecordInfo] = []
    for record in b35_records:
        records.append(wrap_record(record))
    for record in b15_records:
        records.append(wrap_record(record))
    return records


def get_best_records(db: Session, username: str, page_size: int, page_index: int, sort_by: str, order: str):
    unwrapped_records = crud.get_best_records(db, username, page_size, page_index, sort_by, order == "desc")
    records: List[util.PlayRecordInfo] = []
    for record in unwrapped_records:
        records.append(wrap_record(record))
    return records


def remove_b50_record(db: Session, record: Best50Trends):
    # TODO: remove a b50 record
    pass


def update_b50_record(db: Session, username: str) -> Best50Trends:
    trends = crud.update_b50_record(db, username)
    return trends


def get_b50_trends(db: Session, username: str, scope: str | None) -> List[Type[Best50Trends]]:
    trends: List[Type[Best50Trends]] = crud.get_b50_trends(db, username, scope)
    return trends
