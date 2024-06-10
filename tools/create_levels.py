import json
from backend.model.schemas import SongCreate, LevelInfo
from backend.util.database import get_db
from backend.crud.song import create_song


if __name__ == '__main__':
    with open("meta.json", "r") as f:
        meta = json.load(f)

    songs, songs_schema = meta['items'], []
    for song in songs:
        if song['isNewlyUpdated']:
            songs_schema.append(SongCreate(
                title=song['title'],
                artist=song['musician'],
                genre=song['genre'],
                cover=f"{song['title']}.png",
                illustrator=song['illustrator'],
                version=meta['ver'],
                b15=True,
                ablum='Future MagnetiX',
                bpm=song['bpm'],
                length='?:??',
                song_levels=[LevelInfo(
                    difficulty_id=chart['difficulty']+1,
                    level=chart['level'],
                    level_design=chart['noter']
                ) for chart in song['charts']]
            ))

    db = get_db()
    for song in songs_schema:
        create_song(db, song)
