import secrets
from typing import Union, List, Tuple, Type

from fastapi import HTTPException, Depends
from fastapi_cache.decorator import cache
from sqlalchemy import Row
from sqlalchemy.exc import AmbiguousForeignKeysError
from sqlalchemy.orm import Session

from .. import config
from .. import util
from ..crud import user as crud
from ..model.entities import User, PlayRecord, Best50Trends, BestPlayRecord
from ..model.schemas import UserInDB, UserCreate, PlayRecordCreate
from ..util import security, database
from ..util.encoder import UserInDBCoder


def login(db: Session, username: str, plain_password: str) -> Union[str, None]:
    """
    Generate access token.
    :param db: SQLAlchemy.Session
    :param username
    :param plain_password:
    :return:
    """
    user: User = crud.get_user(db, username)
    if user:
        if not user.is_active:
            raise HTTPException(status_code=400, detail="Inactivated user")
        if security.verify_password(plain_password, user.encoded_password):
            return security.generate_access_jwt(username, config.TOKEN_EXPIRE_MINUTES)
    return None


async def get_current_user_or_none(db: Session = Depends(database.get_db),
                                   token: str = Depends(security.optional_oauth2_scheme)) -> UserInDB | None:
    username = security.extract_username(token)
    if username is None:
        return None
    user = await get_user(db, username)
    return user if user and user.is_active else None


async def get_current_user(db: Session = Depends(database.get_db),
                           token: str = Depends(security.oauth2_scheme)) -> UserInDB:
    """
    For view functions to get current authorized user.
    :param db: SQLAlchemy.Session
    :param token: FastAPI Depends
    :return:
    """
    username = security.extract_username(token)
    return await get_active_user(db, username)


@cache(expire=10, coder=UserInDBCoder)
async def get_active_user(db: Session, username: str) -> Union[UserInDB, None]:
    user: User = crud.get_user(db, username)
    if user:
        if not user.is_active:
            raise HTTPException(status_code=400, detail="Inactivated user")
    else:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    return user


@cache(expire=10, coder=UserInDBCoder)
async def get_user(db: Session, username: str) -> Union[UserInDB, None]:
    user: User = crud.get_user(db, username)
    return UserInDB.model_validate(user)


def create_user(db: Session, user: UserCreate) -> User:
    user: User | None = crud.create_user(db, user)
    if user is None:
        raise HTTPException(status_code=400, detail="Username has already existed")
    return user


def refresh_upload_token(db: Session, user: User) -> User:
    if user is None:
        raise HTTPException(status_code=400, detail="User doesn't exist")
    user.upload_token = secrets.token_hex(32)
    db.commit()
    db.refresh(user)

    return user


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


async def check_probe_authority(db: Session, username: str, current_user: User | None):
    user = await get_user(db, username)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    # 不允许匿名查询，且未认证或者认证信息不匹配
    elif user.anonymous_probe is False and (current_user is None or username != current_user.username):
        raise HTTPException(status_code=401, detail="Anonymous probes are not allowed")
