import secrets

from sqlalchemy.orm import Session

from ..model import schemas
from ..model.entities import User
from ..model.schemas import UserUpdate
from ..util import security


def get_user(db: Session, username: str) -> User | None:
    db_user = db.query(User).filter(User.username == username).first()
    return db_user


def create_user(db: Session, user: schemas.UserCreate) -> User | None:
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        return None

    db_user = User(
        username=user.username,
        nickname=user.username if user.nickname is None else user.nickname,
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


def update_user(db: Session, username: str, update_info: UserUpdate):
    db_user: User | None = db.query(User).filter(User.username == username).one_or_none()
    for attr in UserUpdate.model_fields.keys():
        if getattr(update_info, attr) is not None:
            setattr(db_user, attr, getattr(update_info, attr))
    db.commit()
    db.refresh(db_user)
    return db_user
