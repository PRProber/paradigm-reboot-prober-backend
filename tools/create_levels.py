import json
from backend.model.schemas import SongCreate, LevelInfo
from backend.util.database import get_db_sync
from backend.crud.song import create_song


def get_diff_str(diff_id: int):
    if diff_id == 1:
        return 'detected'
    elif diff_id == 2:
        return 'invaded'
    elif diff_id == 3:
        return 'massive'


if __name__ == '__main__':
    with open("meta.json", "r") as f:
        meta = json.load(f)

    songs, songs_schema = meta['items'], []
    title_id_map, id_song_level_map = {}, {}
    for song in songs:
        if song['isNewlyUpdated']:
            title_id_map[song['title']] = song['address']
            songs_schema.append(SongCreate(
                title=song['title'],
                artist=song['musician'],
                genre=song['genre'],
                cover=f"{song['title']}.png",
                illustrator=song['illustrator'],
                version=meta['ver'],
                b15=True,
                album='Future MagnetiX',
                bpm=song['bpm'],
                length='?:??',
                song_levels=[LevelInfo(
                    difficulty_id=chart['difficulty']+1,
                    level=chart['level'],
                    level_design=chart['noter'],
                    notes=0
                ) for chart in song['charts']]
            ))

    db = get_db_sync()
    for song in songs_schema:
        song = create_song(db, song)
        for level in song.song_levels:
            id_song_level_map[title_id_map[song.title] + f'/{get_diff_str(level.difficulty_id)}'] =\
                level.song_level_id

    with open('new_chart2level.json', 'w', encoding='utf-8') as f:
        json.dump(id_song_level_map, f)

