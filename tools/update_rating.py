from backend.prprober.util.rating import single_rating
from backend.prprober.util.database import get_db_sync
from backend.prprober.model.entities import PlayRecord

if __name__ == '__main__':
    db = get_db_sync()
    records = db.query(PlayRecord).all()
    for record in records:
        record.rating = single_rating(record.song_level.level, record.score)
    db.commit()