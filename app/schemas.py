from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ScanRequest(BaseModel):
    directory: Optional[str] = Field(default=None, description="Directory to scan, defaults to import_root")


class SongFileOut(BaseModel):
    id: int
    format: str
    bitrate: Optional[int] = None
    sample_rate: Optional[int] = None
    bit_depth: Optional[int] = None
    channels: Optional[int] = None
    file_size: int
    is_lossless: bool
    is_playable_web: bool
    original_filename: str
    created_at: datetime

    model_config = {"from_attributes": True}


class SongOut(BaseModel):
    id: int
    title: str
    artist: Optional[str] = None
    lead_artist: Optional[str] = None
    chorus_artist: Optional[str] = None
    lead_artists: list[str] = []
    chorus_artists: list[str] = []
    lyricists: list[str] = []
    composers: list[str] = []
    album: Optional[str] = None
    duration_ms: Optional[int] = None
    formats: list[str]
    tags: list[str] = []
    file_format: Optional[str] = None
    file_size: Optional[int] = None
    bitrate: Optional[int] = None
    sample_rate: Optional[int] = None
    created_at: Optional[datetime] = None
    language: Optional[str] = None
    release_date: Optional[str] = None


class SongDetailOut(BaseModel):
    id: int
    title: str
    artist: Optional[str] = None
    lead_artist: Optional[str] = None
    chorus_artist: Optional[str] = None
    lead_artists: list[str] = []
    chorus_artists: list[str] = []
    lyricists: list[str] = []
    composers: list[str] = []
    album: Optional[str] = None
    duration_ms: Optional[int] = None
    files: list[SongFileOut]
    tags: list[str] = []
    language: Optional[str] = None
    lead_artist_ids: list[int] = []
    chorus_artist_ids: list[int] = []
    lyricist_ids: list[int] = []
    composer_ids: list[int] = []
    release_date: Optional[str] = None


class SongMetadataUpdate(BaseModel):
    title: Optional[str] = None
    album: Optional[str] = None
    duration_ms: Optional[int] = None
    tag_ids: Optional[list[int]] = None
    language_id: Optional[int] = None
    lead_artist_ids: Optional[list[int]] = None
    chorus_artist_ids: Optional[list[int]] = None
    lyricist_ids: Optional[list[int]] = None
    composer_ids: Optional[list[int]] = None
    release_date: Optional[str] = None


class BulkSongMetadataUpdate(BaseModel):
    song_ids: list[int]
    artist: Optional[str] = None
    album: Optional[str] = None
    tag_ids: Optional[list[int]] = None


class TagCreate(BaseModel):
    name: str


class TagUpdate(BaseModel):
    name: str


class TagOut(BaseModel):
    id: int
    name: str


class LanguageCreate(BaseModel):
    name: str


class LanguageUpdate(BaseModel):
    name: str


class LanguageOut(BaseModel):
    id: int
    name: str


class PersonCreate(BaseModel):
    name: str
    types: list[str] = []


class PersonUpdate(BaseModel):
    name: str
    types: list[str] = []


class PersonOut(BaseModel):
    id: int
    name: str
    types: list[str] = []


class FilterOptionsOut(BaseModel):
    artists: list[str]
    albums: list[str]
    lead_artists: list[str] = []
    chorus_artists: list[str] = []
    lyricists: list[str] = []
    composers: list[str] = []
    formats: list[str]
    bitrates: list[int]
    sample_rates: list[int]
    tags: list[TagOut]
    languages: list[LanguageOut]


class ScanResult(BaseModel):
    scan_job_id: int
    status: str
    scanned_count: int
    added_count: int
    skipped_count: int


class PlayResponse(BaseModel):
    song_id: int
    selected_song_file_id: int
    selected_format: str
    stream_url: str
    download_url: str


class PlaylistCreate(BaseModel):
    name: str


class PlaylistSongCreate(BaseModel):
    song_id: int


class PlaylistUpdate(BaseModel):
    name: str


class PlaylistReorder(BaseModel):
    playlist_ids: list[int]


class PlaylistOut(BaseModel):
    id: int
    name: str
    song_count: int


class PlaylistDetailOut(BaseModel):
    id: int
    name: str
    songs: list[SongOut]
