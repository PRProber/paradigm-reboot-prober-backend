from sqlalchemy.orm import Session
from backend.model import entities, schemas


def get_user(db: Session, username: str):
    db_user = db.query(entities.User).filter(entities.User.username == username).first()

