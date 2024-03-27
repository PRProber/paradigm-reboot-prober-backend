from typing import Union

from sqlalchemy.orm import Session
from fastapi import HTTPException, Depends

from ..crud import user as crud
from ..model.entities import User
from ..model.schemas import UserCreate
from ..util import security, database
from .. import config


def login(db: Session, username: str, plain_password: str) -> Union[str, None]:
    user: User = crud.get_user(db, username)
    if user:
        if not user.is_active:
            raise HTTPException(status_code=400, detail="Inactivated user")
        if security.verify_password(plain_password, user.encoded_password):
            return security.generate_access_jwt(username, config.TOKEN_EXPIRE_MINUTES)
    return None


async def get_current_user(db: Session = Depends(database.get_db),
                           token: str = Depends(security.oauth2_scheme)) -> User:
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
