from backend.model import entities, schemas


class SongLevelInfo:
    """
    A simple wrapper class to convert a composed song with levels to independent song levels (chart).
    """
    def __init__(self, level: entities.SongLevel):
        for key in schemas.SongLevelInfo.model_fields.keys():
            if hasattr(level.song, key):
                setattr(self, key, getattr(level.song, key))
            elif hasattr(level, key):
                setattr(self, key, getattr(level, key))
            else:
                setattr(self, key, None)


class PlayRecordInfo:
    """
    A simple wrapper class to convert a composed song with levels to independent song levels (chart).
    """
    def __init__(self, record: entities.PlayRecord):
        for key in schemas.PlayRecordInfo.model_fields.keys():
            if hasattr(record, key):
                setattr(self, key, getattr(record, key))
            else:
                setattr(self, key, None)
        setattr(self, 'song_level', SongLevelInfo(record.song_level))


class SongInfo:
    """
    A simple wrapper class to convert an ORM song to a Song schema (flatten entities.Difficulty).
    """
    def __init__(self, song: entities.Song):
        for key in schemas.SongLevelInfo.model_fields.keys():
            if hasattr(song, key):
                setattr(self, key, getattr(song, key))
            else:
                setattr(self, key, None)
