from backend.prprober.util.database import get_db_sync
from backend.prprober.crud.song import get_single_song_by_id
from backend.prprober.model.entities import Song

import json


if __name__ == "__main__":
    db = get_db_sync()
    with open("prp_to_wiki.json") as f:
        mapping = json.load(f)
    for song_id, wiki_id in mapping.items():
        song: Song = get_single_song_by_id(db, int(song_id))
        song.wiki_id = wiki_id
    db.commit()