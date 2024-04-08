from pydantic import BaseModel
from datetime import datetime


class SongBase(BaseModel):
    title: str | None = None
    artist: str | None = None
    genre: str | None = None
    cover: str | None = None
    illustrator: str | None = None
    version: str | None = None
    b15: bool | None = False
    album: str | None = None
    bpm: str | None = None
    length: str | None = None


class UserBase(BaseModel):
    username: str
    email: str
    qq_number: int | None = None
    account: str | None = None
    account_number: int | None = None
    uuid: str | None = None
    anonymous_probe: bool | None = False
    upload_token: str | None = None
    is_active: bool | None = True
    is_admin: bool | None = False


class PlayRecordBase(BaseModel):
    username: str
    song_level_id: int
    score: int


class PlayRecord(PlayRecordBase):
    play_record_id: int
    record_time: datetime
    rating: float

    class Config:
        from_attributes = True


class User(UserBase):
    class Config:
        from_attributes = True


class SongLevelInfo(SongBase):
    song_id: int
    song_level_id: int
    difficulty_id: int
    difficulty: str | None = None
    level: float
    fitting_level: float | None = None
    level_design: str | None = None
    notes: int | None = None

    class Config:
        from_attributes = True


class LevelInfo(BaseModel):
    difficulty_id: int
    difficulty: str | None = None
    level: float
    level_design: str | None = None
    notes: int | None = None

    class Config:
        from_attributes = True


class Song(SongBase):
    song_id: int
    song_levels: list[LevelInfo]

    class Config:
        from_attributes = True


class SongCreate(SongBase):
    song_levels: list[LevelInfo]


class SongUpdate(SongBase):
    song_id: int
    song_levels: list[LevelInfo]


class UserCreate(UserBase):
    password: str


class PlayRecordCreate(PlayRecordBase):
    pass


class Token(BaseModel):
    access_token: str
    token_type: str

