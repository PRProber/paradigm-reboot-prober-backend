from sqlalchemy.orm import Session

from backend.model import database, entities
from backend.model.database import SessionLocal


def init_db():
    database.Base.metadata.create_all(bind=database.engine)

    with Session(database.engine) as db:
        init_difficulties(db)


def init_difficulties(db: Session):
    diffs = ["Detected", "Invaded", "Massive"]
    db_diffs = [entities.Difficulty(name=diff) for diff in diffs]
    db.add_all(db_diffs)
    db.commit()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
