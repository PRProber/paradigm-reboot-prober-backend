from backend.util.rating import single_rating
from backend.util.database import get_db_sync
from backend.model.entities import BestPlayRecord, PlayRecord

if __name__ == '__main__':
    db = get_db_sync()
    records = db.query(PlayRecord).all()
    for record in records:
        record.rating = single_rating(record.song_level.level, record.score)
    db.commit()