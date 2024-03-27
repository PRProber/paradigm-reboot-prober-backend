from typing import Type

from fastapi import HTTPException
from sqlalchemy.orm import Session

from ..model import entities, schemas
from ..model.entities import User
from ..util import security


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
        is_active=True,
        is_admin=False
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user
