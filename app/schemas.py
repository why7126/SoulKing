from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field, model_validator


class ScanRequest(BaseModel):
    directory: Optional[str] = Field(default=None, description="Directory to scan, defaults to import_root")


class SongFileRenameIn(BaseModel):
    """仅更新展示用原始文件名，不修改对象存储路径。"""

    original_filename: str = Field(..., min_length=1, max_length=512)


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


class SongFileVariantOut(BaseModel):
    """同一首歌下各文件格式，用于列表选择播放/下载"""

    file_id: int
    format: str


class LyricLineOut(BaseModel):
    time_ms: int
    text: str


class SongLyricsOut(BaseModel):
    filename: str
    content: str
    lines: list[LyricLineOut] = []


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
    file_variants: list[SongFileVariantOut] = []
    tags: list[str] = []
    file_id: Optional[int] = None
    file_format: Optional[str] = None
    file_size: Optional[int] = None
    bitrate: Optional[int] = None
    sample_rate: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    language: Optional[str] = None
    genre: Optional[str] = None
    release_date: Optional[str] = None
    film_tv: Optional[str] = None
    has_lyrics: bool = False


class SongListPageOut(BaseModel):
    items: list[SongOut]
    total: int
    library_total: int


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
    language_ids: list[int] = []
    genre: Optional[str] = None
    lead_artist_ids: list[int] = []
    chorus_artist_ids: list[int] = []
    lyricist_ids: list[int] = []
    composer_ids: list[int] = []
    genre_id: Optional[int] = None
    genre_ids: list[int] = []
    release_date: Optional[str] = None
    film_tv: Optional[str] = None
    has_lyrics: bool = False


class SongMetadataUpdate(BaseModel):
    title: Optional[str] = None
    album: Optional[str] = None
    duration_ms: Optional[int] = None
    tag_ids: Optional[list[int]] = None
    language_id: Optional[int] = None
    language_ids: Optional[list[int]] = None
    genre_id: Optional[int] = None
    genre_ids: Optional[list[int]] = None
    lead_artist_ids: Optional[list[int]] = None
    chorus_artist_ids: Optional[list[int]] = None
    lyricist_ids: Optional[list[int]] = None
    composer_ids: Optional[list[int]] = None
    release_date: Optional[str] = None
    film_tv: Optional[str] = None


class BulkSongMetadataUpdate(BaseModel):
    song_ids: list[int]
    artist: Optional[str] = None
    album: Optional[str] = None
    tag_ids: Optional[list[int]] = None


class SongMergeSelected(BaseModel):
    """将多首歌曲合并为一首：全部并入 master_song_id 对应歌曲，其余歌曲记录删除。"""

    song_ids: list[int]
    master_song_id: int = Field(..., description="合并目标歌曲 ID，须在所选 song_ids 中")

    @model_validator(mode="after")
    def _master_must_be_in_selection(self) -> "SongMergeSelected":
        ids = {int(x) for x in self.song_ids if x is not None}
        if len(ids) < 2:
            raise ValueError("请至少选择 2 首歌曲")
        mid = int(self.master_song_id)
        if mid not in ids:
            raise ValueError("合并目标歌曲必须在已选歌曲列表中")
        return self


class BatchSongDownloadIn(BaseModel):
    """批量下载：对每首歌曲拉取所选格式（若存在）；总计多个文件时返回 ZIP。"""

    song_ids: list[int] = Field(..., min_length=1)
    formats: list[str] = Field(..., min_length=1)


class TagCreate(BaseModel):
    name: str


class TagUpdate(BaseModel):
    name: str


class TagOut(BaseModel):
    id: int
    name: str
    created_at: Optional[str] = None


class LanguageCreate(BaseModel):
    name: str


class LanguageUpdate(BaseModel):
    name: str


class LanguageOut(BaseModel):
    id: int
    name: str
    created_at: Optional[str] = None


class GenreCreate(BaseModel):
    name: str


class GenreUpdate(BaseModel):
    name: str


class GenreOut(BaseModel):
    id: int
    name: str
    created_at: Optional[str] = None


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
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


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
    genres: list[GenreOut] = []


class SkippedFileDetail(BaseModel):
    path: str
    reason: str


class ScanResult(BaseModel):
    scan_job_id: int
    status: str
    scanned_count: int
    added_count: int
    skipped_count: int
    total_count: int = 0
    start_time: Optional[float] = None
    skipped_details: list[SkippedFileDetail] = Field(default_factory=list)


class ScanProgress(BaseModel):
    is_scanning: bool = False
    total_count: int = 0
    scanned_count: int = 0
    added_count: int = 0
    skipped_count: int = 0
    start_time: Optional[float] = None
    skipped_details: list[SkippedFileDetail] = Field(default_factory=list)


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
