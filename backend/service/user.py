import secrets
from typing import Union, Type

from fastapi import HTTPException, Depends
from fastapi_cache.decorator import cache
from sqlalchemy.orm import Session

from .. import config
from ..crud import user as crud
from ..model.entities import User
from ..model.schemas import UserInDB, UserCreate, UserUpdate
from ..util import security, database
from ..util.cache import UserInDBCoder


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


@cache(expire=5, coder=UserInDBCoder)
async def get_active_user(db: Session, username: str) -> Union[UserInDB, None]:
    user: User = crud.get_user(db, username)
    if user:
        if not user.is_active:
            raise HTTPException(status_code=400, detail="Inactivated user")
    else:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    return UserInDB.model_validate(user) if user else None


@cache(expire=5, coder=UserInDBCoder)
async def get_user(db: Session, username: str) -> Union[UserInDB, None]:
    user: User = crud.get_user(db, username)
    return UserInDB.model_validate(user) if user else None


def create_user(db: Session, user: UserCreate) -> User:
    user: User | None = crud.create_user(db, user)
    if user is None:
        raise HTTPException(status_code=400, detail="Username has already existed")
    return user


def refresh_upload_token(db: Session, username: str) -> str:
    user: Type[User] = db.query(User).filter(User.username == username).one()
    user.upload_token = secrets.token_hex(32)
    db.commit()
    db.refresh(user)

    return user.upload_token


async def check_probe_authority(db: Session, username: str, current_user: UserInDB | None):
    user = await get_user(db, username)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    # 不允许匿名查询，且未认证或者认证信息不匹配
    elif user.anonymous_probe is False and (current_user is None or username != current_user.username):
        raise HTTPException(status_code=401, detail="Anonymous probes are not allowed")


def update_user(db: Session, user: UserInDB, update_info: UserUpdate):
    return crud.update_user(db, user.username, update_info)
