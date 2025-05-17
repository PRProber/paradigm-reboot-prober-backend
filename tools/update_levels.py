import json
from backend.prprober.util.database import get_db_sync
from backend.prprober.crud.song import get_all_songs

if __name__ == '__main__':

    db = get_db_sync()
    songs = get_all_songs(db)
    EPS = 0.0002

    diff_to_id = {
        'detected': 1,
        'invaded': 2,
        'massive': 3
    }
    id_to_diff = {
        1: "detected",
        2: "invaded",
        3: "massive"
    }
    title_to_id = {}

    with open('meta_modified.json') as f:
        songs_meta = json.load(f)['songs']

    for song_id, info in songs_meta.items():
        title_to_id[info['title']] = song_id

    for song in songs:
        for level in song.song_levels:
            meta_level = songs_meta[title_to_id[song.title]]['charts'][id_to_diff[level.difficulty_id]]['acclevel']
            if abs(level.level - meta_level) > EPS and meta_level != 0:
                print(f"update level {song.title}[{id_to_diff[level.difficulty_id]}] {level.level}"
                      f"->{meta_level}")
                level.level = meta_level

    db.commit()



