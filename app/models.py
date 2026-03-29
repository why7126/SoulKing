from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.datetime_util import now_cn_naive


class Artist(Base):
    __tablename__ = "artists"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    types: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now_cn_naive)


class Album(Base):
    __tablename__ = "albums"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    artist_id: Mapped[Optional[int]] = mapped_column(ForeignKey("artists.id"), nullable=True)
    year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now_cn_naive)

    __table_args__ = (UniqueConstraint("name", "artist_id", name="uq_album_name_artist"),)


class Song(Base):
    __tablename__ = "songs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), index=True)
    artist_id: Mapped[Optional[int]] = mapped_column(ForeignKey("artists.id"), nullable=True, index=True)
    chorus_artist_id: Mapped[Optional[int]] = mapped_column(ForeignKey("artists.id"), nullable=True, index=True)
    album_id: Mapped[Optional[int]] = mapped_column(ForeignKey("albums.id"), nullable=True, index=True)
    language_id: Mapped[Optional[int]] = mapped_column(ForeignKey("languages.id"), nullable=True, index=True)
    genre_id: Mapped[Optional[int]] = mapped_column(ForeignKey("genres.id"), nullable=True, index=True)
    release_date: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    film_tv: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    duration_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now_cn_naive)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=now_cn_naive, onupdate=now_cn_naive)

    # 不含 delete-orphan；passive_deletes=True：删除 Song 时不要让 ORM 去改子表 FK（合并后文件已改挂主曲，误触会置 NULL 违反 NOT NULL）
    files: Mapped[list["SongFile"]] = relationship(
        "SongFile",
        back_populates="song",
        cascade="save-update, merge",
        passive_deletes=True,
    )


class SongFile(Base):
    __tablename__ = "song_files"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    song_id: Mapped[int] = mapped_column(ForeignKey("songs.id"), index=True)
    object_key: Mapped[str] = mapped_column(String(1024), unique=True, index=True)
    original_filename: Mapped[str] = mapped_column(String(512))
    format: Mapped[str] = mapped_column(String(32), index=True)
    mime_type: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    bitrate: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    sample_rate: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    bit_depth: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    channels: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    file_size: Mapped[int] = mapped_column(Integer)
    sha256: Mapped[str] = mapped_column(String(64), index=True)
    is_lossless: Mapped[bool] = mapped_column(Boolean, default=False)
    is_playable_web: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now_cn_naive)

    song: Mapped[Song] = relationship("Song", back_populates="files")

    # 仅 object_key 全局唯一；同一歌曲下可保留多条相同 sha256+file_size（合并后多路径指向相同字节时仍保留各行）。


class ScanJob(Base):
    __tablename__ = "scan_jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    root_path: Mapped[str] = mapped_column(String(1024))
    status: Mapped[str] = mapped_column(String(32), default="running")
    scanned_count: Mapped[int] = mapped_column(Integer, default=0)
    added_count: Mapped[int] = mapped_column(Integer, default=0)
    skipped_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now_cn_naive)
    finished_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)


class Playlist(Base):
    __tablename__ = "playlists"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now_cn_naive)

    items: Mapped[list["PlaylistItem"]] = relationship(
        "PlaylistItem", back_populates="playlist", cascade="all, delete-orphan"
    )


class PlaylistItem(Base):
    __tablename__ = "playlist_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    playlist_id: Mapped[int] = mapped_column(ForeignKey("playlists.id"), index=True)
    song_id: Mapped[int] = mapped_column(ForeignKey("songs.id"), index=True)
    position: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now_cn_naive)

    playlist: Mapped[Playlist] = relationship("Playlist", back_populates="items")

    __table_args__ = (UniqueConstraint("playlist_id", "song_id", name="uq_playlist_song"),)


class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now_cn_naive)


class SongTag(Base):
    __tablename__ = "song_tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    song_id: Mapped[int] = mapped_column(ForeignKey("songs.id"), index=True)
    tag_id: Mapped[int] = mapped_column(ForeignKey("tags.id"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now_cn_naive)

    __table_args__ = (UniqueConstraint("song_id", "tag_id", name="uq_song_tag"),)


class Language(Base):
    __tablename__ = "languages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now_cn_naive)


class SongLanguage(Base):
    __tablename__ = "song_languages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    song_id: Mapped[int] = mapped_column(ForeignKey("songs.id"), index=True)
    language_id: Mapped[int] = mapped_column(ForeignKey("languages.id"), index=True)

    __table_args__ = (UniqueConstraint("song_id", "language_id", name="uq_song_language"),)


class Genre(Base):
    __tablename__ = "genres"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now_cn_naive)


class SongGenre(Base):
    __tablename__ = "song_genres"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    song_id: Mapped[int] = mapped_column(ForeignKey("songs.id"), index=True)
    genre_id: Mapped[int] = mapped_column(ForeignKey("genres.id"), index=True)

    __table_args__ = (UniqueConstraint("song_id", "genre_id", name="uq_song_genre"),)


class SongLeadArtist(Base):
    __tablename__ = "song_lead_artists"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    song_id: Mapped[int] = mapped_column(ForeignKey("songs.id"), index=True)
    artist_id: Mapped[int] = mapped_column(ForeignKey("artists.id"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now_cn_naive)


class SongChorusArtist(Base):
    __tablename__ = "song_chorus_artists"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    song_id: Mapped[int] = mapped_column(ForeignKey("songs.id"), index=True)
    artist_id: Mapped[int] = mapped_column(ForeignKey("artists.id"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now_cn_naive)


class SongLyricistArtist(Base):
    __tablename__ = "song_lyricist_artists"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    song_id: Mapped[int] = mapped_column(ForeignKey("songs.id"), index=True)
    artist_id: Mapped[int] = mapped_column(ForeignKey("artists.id"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now_cn_naive)


class SongComposerArtist(Base):
    __tablename__ = "song_composer_artists"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    song_id: Mapped[int] = mapped_column(ForeignKey("songs.id"), index=True)
    artist_id: Mapped[int] = mapped_column(ForeignKey("artists.id"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now_cn_naive)
