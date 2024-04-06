from typing import List, Optional
from datetime import datetime

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column, relationship

from .database import Base


# 歌曲数据部分
class Song(Base):
    __tablename__ = 'songs'

    song_id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column()
    artist: Mapped[str] = mapped_column()
    genre: Mapped[str] = mapped_column()
    cover: Mapped[str] = mapped_column()  # 实际上为封面的*文件名*
    illustrator: Mapped[str] = mapped_column()
    version: Mapped[str] = mapped_column()
    b15: Mapped[bool] = mapped_column()  # 是否为 b15 歌曲
    album: Mapped[str] = mapped_column()
    bpm: Mapped[str] = mapped_column()
    length: Mapped[str] = mapped_column()

    song_levels: Mapped[List["SongLevel"]] = relationship(back_populates='song')


class Difficulty(Base):
    __tablename__ = 'difficulties'

    difficulty_id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()

    song_levels: Mapped[List["SongLevel"]] = relationship(back_populates='difficulty')


class SongLevel(Base):
    __tablename__ = 'song_levels'

    song_level_id: Mapped[int] = mapped_column(primary_key=True)
    song_id: Mapped[int] = mapped_column(ForeignKey('songs.song_id'))
    difficulty_id: Mapped[int] = mapped_column(ForeignKey('difficulties.difficulty_id'))
    level: Mapped[float] = mapped_column()
    fitting_level: Mapped[Optional[float]] = mapped_column(nullable=True)
    level_design: Mapped[str] = mapped_column(nullable=True)  # 考虑到合作作谱，设计上不把谱师独立建表
    notes: Mapped[int] = mapped_column()

    song: Mapped["Song"] = relationship(back_populates='song_levels')
    difficulty: Mapped["Difficulty"] = relationship(back_populates='song_levels')


# 用户数据部分
class User(Base):
    __tablename__ = 'prober_users'

    user_id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    encoded_password: Mapped[str] = mapped_column()
    email: Mapped[str] = mapped_column()
    qq_number: Mapped[Optional[int]] = mapped_column()
    account: Mapped[Optional[str]] = mapped_column()
    account_number: Mapped[Optional[int]] = mapped_column()
    uuid: Mapped[Optional[str]] = mapped_column()
    anonymous_probe: Mapped[bool] = mapped_column()  # 允许匿名查询成绩
    upload_token: Mapped[str] = mapped_column()  # 匿名上传成绩 token
    is_active: Mapped[bool] = mapped_column()
    is_admin: Mapped[bool] = mapped_column()  # 权限管理

    play_records: Mapped[List["PlayRecord"]] = relationship(back_populates='user')


class PlayRecord(Base):
    __tablename__ = 'play_records'

    play_record_id: Mapped[int] = mapped_column(primary_key=True)
    song_level_id: Mapped[int] = mapped_column(ForeignKey('song_levels.song_level_id'))
    record_time: Mapped[datetime] = mapped_column()
    username: Mapped[str] = mapped_column(ForeignKey('prober_users.username'))
    score: Mapped[int] = mapped_column()
    rating: Mapped[float] = mapped_column()  # 便于查询 b50

    user: Mapped["User"] = relationship(back_populates='play_records')
    song_level: Mapped["SongLevel"] = relationship()


class BestPlayRecord(Base):
    __tablename__ = 'best_play_records'

    best_record_id: Mapped[int] = mapped_column(primary_key=True)
    play_record_id: Mapped[int] = mapped_column(ForeignKey('play_records.play_record_id'))

    play_record: Mapped["PlayRecord"] = relationship(uselist=False)
