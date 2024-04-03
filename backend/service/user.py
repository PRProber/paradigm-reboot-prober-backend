import secrets
from typing import Union, List, Tuple

from sqlalchemy.orm import Session
from fastapi import HTTPException, Depends

from ..crud import user as crud
from ..model.entities import User, PlayRecord
from ..model.schemas import UserCreate, PlayRecordCreate
from ..util import security, database
from .. import config


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


async def get_current_user(db: Session = Depends(database.get_db),
                           token: str = Depends(security.oauth2_scheme)) -> User:
    """
    For view functions to get current authorized user.
    :param db: SQLAlchemy.Session
    :param token: FastAPI Depends
    :return:
    """
    username = security.extract_username(token)
    return get_active_user(db, username)


def get_active_user(db: Session, username: str) -> Union[User, None]:
    user: User = crud.get_user(db, username)
    if user:
        if not user.is_active:
            raise HTTPException(status_code=400, detail="Inactivated user")
    else:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    return user


def get_user(db: Session, username: str) -> Union[User, None]:
    user: User = crud.get_user(db, username)
    return user


def create_user(db: Session, user: UserCreate) -> User:
    user: User | None = crud.create_user(db, user)
    if user is None:
        raise HTTPException(status_code=400, detail="Username has already exists")
    return user


def refresh_upload_token(db: Session, user: User) -> User:
    if user is None:
        raise HTTPException(status_code=400, detail="User doesn't exist")
    user.upload_token = secrets.token_hex(256)
    db.commit()
    db.refresh(user)

    return user


def create_record(db: Session, record: PlayRecordCreate, user: User) -> PlayRecord:
    # TODO: Implement this function
    pass


def get_all_records(db: Session, username: str) -> List[PlayRecord]:
    # TODO: Implement this function
    pass


def get_best_records(db: Session, username: str, underflow: int = 0) \
        -> Tuple[List[PlayRecord], List[PlayRecord]]:
    # TODO: Implement this function
    pass
