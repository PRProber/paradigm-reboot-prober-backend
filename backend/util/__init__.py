from backend.model import entities, schemas


class SongLevelInfo:
    """
    A simple wrapper class to convert a composed song with levels to independent song levels (chart).
    """
    def __init__(self, song: entities.Song):
        for key in schemas.SongLevelInfo.model_fields.keys():
            if hasattr(song, key):
                setattr(self, key, getattr(song, key))
            else:
                setattr(self, key, None)
