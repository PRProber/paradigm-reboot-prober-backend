import secrets
from typing import Tuple, List

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
        upload_token=secrets.token_hex(256),
        is_active=True,
        is_admin=False
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


def create_record(db: Session, record: schemas.PlayRecordCreate, user: User):
    """
    Create a play record.
    :param db: SQLAlchemy.orm Session
    :param record: record details
    :param user: validated user
    :return: record entity
    """
    # TODO: Implement this function
    pass


def get_all_records(db: Session, username: str) -> List[entities.PlayRecord]:
    # TODO: Implement this function
    pass


def get_best_records(db: Session, username: str, underflow: int = 0) \
        -> Tuple[List[entities.PlayRecord], List[entities.PlayRecord]]:
    """
    Get best play records of a user. Returns a tuple. The first element is the list of records of old version (b35),
    and the second element is the list of records of ne version (b15).
    :param db: SQLAlchemy.orm Session
    :param username: the username of the user
    :param underflow: underflow records threshold
    :return: (list, list) like tuple
    """
    # TODO: Implement this function
    # Remark: it's possible to return a little more records i.e. underflow
    pass
