from pydantic import BaseModel
from datetime import datetime


class SongBase(BaseModel):
    title: str | None = None
    artist: str | None = None
    cover: str | None = None
    illustrator: str | None = None
    version: str | None = None
    b15: bool | None = False
    album: str | None = None
    bpm: float | None = None


class SongLevelBase(BaseModel):
    difficulty_id: int | None = None
    difficulty: str | None = None
    level: float | None = None
    level_design: str | None = None


class UserBase(BaseModel):
    username: str
    email: str | None = None
    qq_number: int | None = None
    account: str | None = None
    account_number: int | None = None
    uuid: str | None = None
    anonymous_probe: bool | None = False
    is_active: bool | None = True
    is_admin: bool | None = False


class PlayRecordBase(BaseModel):
    username: str
    song_level_id: int
    acc: float


class PlayRecord(PlayRecordBase):
    play_record_id: int
    record_time: datetime


class User(UserBase):
    class Config:
        from_attributes = True


class SongLevelInfo(SongBase):
    difficulty_id: int
    difficulty: str | None = None
    level: float
    fitting_level: float | None = None
    level_design: str | None = None

    class Config:
        from_attributes = True


class SongCreate(SongBase):
    song_levels: list[SongLevelInfo]


class SongUpdate(SongBase):
    song_id: int
    song_levels: list[SongLevelInfo]


class UserCreate(UserBase):
    password: str


class PlayRecordCreate(PlayRecordBase):
    pass
