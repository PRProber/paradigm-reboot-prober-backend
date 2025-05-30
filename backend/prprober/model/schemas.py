from pydantic import BaseModel, Field, EmailStr
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
    wiki_id: str | None = None


class UserBase(BaseModel):
    username: str
    email: str
    nickname: str | None = None
    qq_number: int | None = None
    account: str | None = None
    account_number: int | None = None
    uuid: str | None = None
    anonymous_probe: bool | None = False
    upload_token: str | None = None
    is_active: bool | None = True
    is_admin: bool | None = False


class PlayRecordBase(BaseModel):
    song_level_id: int
    score: int


class PlayRecord(PlayRecordBase):
    username: str
    play_record_id: int
    record_time: datetime
    rating: float

    class Config:
        from_attributes = True


class User(UserBase):
    class Config:
        from_attributes = True


class UserInDB(UserBase):
    encoded_password: str

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
    song_levels: list[LevelInfo] | None = None


class UserCreate(UserBase):
    username: str = Field(pattern=r'^[A-Za-z][A-Za-z0-9_]{5,15}$')
    email: EmailStr
    # TODO: 适配 Pydantic 的 Rust-style regex 校验
    password: str


class UserUpdate(BaseModel):
    nickname: str | None = None
    qq_number: int | None = None
    account: str | None = None
    account_number: int | None = None
    uuid: str | None = None
    anonymous_probe: bool | None = False


class PlayRecordCreate(PlayRecordBase):
    pass


class BatchPlayRecordCreate(BaseModel):
    upload_token: str | None = None
    csv_filename: str | None = None
    is_replace: bool | None = False
    play_records: list[PlayRecordCreate] | None = None


class SongLevelInfoSimple(BaseModel):
    wiki_id: str | None = None
    title: str | None = None
    version: str | None = None
    b15: bool | None = False
    song_id: int
    song_level_id: int
    difficulty_id: int
    difficulty: str
    level: float
    cover: str | None = None
    fitting_level: float | None = None


class PlayRecordInfo(BaseModel):
    play_record_id: int
    record_time: datetime
    score: int
    rating: float
    song_level: SongLevelInfoSimple


class PlayRecordResponse(BaseModel):
    username: str
    total: int | None = None
    records: list[PlayRecordInfo]


class Token(BaseModel):
    access_token: str
    token_type: str


class UploadToken(BaseModel):
    upload_token: str


class SongLevelCsv(BaseModel):
    song_level_id: int
    title: str
    version: str
    difficulty: str
    level: float
    score: int | None = None


class UploadFileResponse(BaseModel):
    filename: str