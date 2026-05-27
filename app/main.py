from pathlib import Path
import io
import json
import mimetypes
import shutil
import tempfile
import zipfile
from datetime import datetime
from typing import Optional
from zoneinfo import ZoneInfo

from botocore.exceptions import ClientError
from fastapi import Body, Depends, FastAPI, File, HTTPException, Query, Request, UploadFile
from fastapi.responses import FileResponse
from fastapi.responses import StreamingResponse
from urllib.parse import quote
from fastapi.staticfiles import StaticFiles
from sqlalchemy import func, inspect, or_, select, text
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import Base, engine, get_db
from app.models import Album, Artist, Genre, Language, Playlist, PlaylistItem, Song, SongChorusArtist, SongComposerArtist, SongFile, SongGenre, SongLanguage, SongLeadArtist, SongLyricistArtist, SongTag, Tag
from app.schemas import (
    BatchSongDownloadIn,
    BulkSongMetadataUpdate,
    FilterOptionsOut,
    GenreCreate,
    GenreOut,
    GenreUpdate,
    PersonCreate,
    PersonOut,
    PersonUpdate,
    PlayResponse,
    PlaylistCreate,
    PlaylistDetailOut,
    PlaylistReorder,
    PlaylistOut,
    PlaylistSongCreate,
    PlaylistUpdate,
    ScanRequest,
    ScanResult,
    ScanProgress,
    SongDetailOut,
    SongFileOut,
    SongFileRenameIn,
    SongFileVariantOut,
    SongMergeSelected,
    SongMetadataUpdate,
    SongListPageOut,
    SongLyricsOut,
    LyricLineOut,
    SongOut,
    LanguageCreate,
    LanguageOut,
    LanguageUpdate,
    TagCreate,
    TagOut,
    TagUpdate,
)
from app.services import (
    attach_audio_file_to_song,
    audio_song_files,
    choose_best_file,
    delete_song_lyric_files,
    effective_is_playable_web,
    get_or_create_album,
    get_or_create_artist,
    get_song_lyric_file,
    ingest_lyric_file,
    parse_lrc_content,
    read_lyric_file_text,
    relocate_song_files_storage,
    scan_directory,
    sync_song_file_names_to_title,
    song_has_lyrics,
)
from app.services import LYRIC_EXTENSIONS, LYRIC_MAX_BYTES, SUPPORTED_EXTENSIONS, ingest_file
from app.song_merge import merge_duplicate_songs, merge_slave_into_master
from app.storage import S3Storage

settings = get_settings()
app = FastAPI(title=settings.app_name)
storage = S3Storage()
static_dir = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=static_dir), name="static")

scan_progress = {
    "is_scanning": False,
    "total_count": 0,
    "scanned_count": 0,
    "added_count": 0,
    "skipped_count": 0,
    "start_time": None,
    "skipped_details": [],
}


def song_file_to_out(song_file: SongFile) -> SongFileOut:
    """
    手动组装，避免历史库里 format 等列为 NULL 时 model_validate 失败（否则会拖垮整个 SongDetailOut 序列化 → 500）。
    """
    fmt = (song_file.format or "").strip().lstrip(".").lower() or "unknown"
    return SongFileOut(
        id=song_file.id,
        format=fmt,
        bitrate=song_file.bitrate,
        sample_rate=song_file.sample_rate,
        bit_depth=song_file.bit_depth,
        channels=song_file.channels,
        file_size=song_file.file_size or 0,
        is_lossless=bool(song_file.is_lossless),
        is_playable_web=effective_is_playable_web(song_file),
        original_filename=(song_file.original_filename or "").strip() or "audio",
        created_at=song_file.created_at or datetime(1970, 1, 1),
    )


def stream_content_type_for_song_file(song_file: SongFile) -> str:
    """浏览器 <audio> 对 Content-Type 较敏感，需显式映射常见后缀，避免误报 resource not suitable。"""
    fmt = (song_file.format or "").strip().lower().lstrip(".")
    by_ext = {
        "mp3": "audio/mpeg",
        "flac": "audio/flac",
        "m4a": "audio/mp4",
        "aac": "audio/aac",
        "wav": "audio/wav",
        "ogg": "audio/ogg",
        "oga": "audio/ogg",
        "opus": "audio/ogg",
        "alac": "audio/mp4",
    }
    if fmt in by_ext:
        return by_ext[fmt]
    mime = song_file.mime_type
    if not mime or mime == "application/octet-stream":
        guessed, _ = mimetypes.guess_type(f"x.{fmt}" if fmt else "")
        mime = guessed
    if fmt == "flac" and (not mime or mime == "application/octet-stream"):
        mime = "audio/flac"
    return mime or "application/octet-stream"


def get_song_tag_names(db: Session, song_id: int) -> list[str]:
    rows = db.execute(
        select(Tag.name).join(SongTag, SongTag.tag_id == Tag.id).where(SongTag.song_id == song_id).order_by(Tag.name.asc())
    ).all()
    return [row[0] for row in rows]


def parse_artist_types(value: Optional[str]) -> list[str]:
    if not value:
        return []
    return [item for item in value.split(",") if item]


def encode_artist_types(types: list[str]) -> str:
    unique = []
    for item in types:
        text = item.strip()
        if text and text not in unique:
            unique.append(text)
    return ",".join(unique)


def get_song_language_ids(db: Session, song_id: int) -> list[int]:
    rows = db.execute(
        select(SongLanguage.language_id)
        .join(Language, SongLanguage.language_id == Language.id)
        .where(SongLanguage.song_id == song_id)
        .order_by(Language.name.asc())
    ).all()
    ids = [row[0] for row in rows]
    if ids:
        return ids
    song = db.scalar(select(Song).where(Song.id == song_id))
    if song and song.language_id:
        return [song.language_id]
    return []


def get_song_language_name(db: Session, song: Song) -> Optional[str]:
    lids = get_song_language_ids(db, song.id)
    if not lids:
        return None
    names = db.scalars(select(Language.name).where(Language.id.in_(lids)).order_by(Language.name.asc())).all()
    return ", ".join(names) if names else None


def set_song_languages(db: Session, song_id: int, language_ids: list[int]) -> None:
    db.query(SongLanguage).filter(SongLanguage.song_id == song_id).delete()
    seen: list[int] = []
    for lid in language_ids:
        if lid and lid not in seen:
            seen.append(lid)
    song = db.scalar(select(Song).where(Song.id == song_id))
    for lid in seen:
        if db.scalar(select(Language).where(Language.id == lid)):
            db.add(SongLanguage(song_id=song_id, language_id=lid))
    if song:
        song.language_id = seen[0] if seen else None


def get_song_genre_ids(db: Session, song_id: int) -> list[int]:
    rows = db.execute(
        select(SongGenre.genre_id).join(Genre, SongGenre.genre_id == Genre.id).where(SongGenre.song_id == song_id).order_by(Genre.name.asc())
    ).all()
    ids = [row[0] for row in rows]
    if ids:
        return ids
    song = db.scalar(select(Song).where(Song.id == song_id))
    if song and song.genre_id:
        return [song.genre_id]
    return []


def get_song_genre_name(db: Session, song: Song) -> Optional[str]:
    gids = get_song_genre_ids(db, song.id)
    if not gids:
        return None
    names = db.scalars(select(Genre.name).where(Genre.id.in_(gids)).order_by(Genre.name.asc())).all()
    return ", ".join(names) if names else None


def set_song_genres(db: Session, song_id: int, genre_ids: list[int]) -> None:
    db.query(SongGenre).filter(SongGenre.song_id == song_id).delete()
    seen: list[int] = []
    for gid in genre_ids:
        if gid and gid not in seen:
            seen.append(gid)
    song = db.scalar(select(Song).where(Song.id == song_id))
    for gid in seen:
        if db.scalar(select(Genre).where(Genre.id == gid)):
            db.add(SongGenre(song_id=song_id, genre_id=gid))
    if song:
        song.genre_id = seen[0] if seen else None


def get_song_lead_artist_names(db: Session, song: Song) -> list[str]:
    rows = db.execute(
        select(Artist.name).join(SongLeadArtist, SongLeadArtist.artist_id == Artist.id).where(SongLeadArtist.song_id == song.id).order_by(Artist.name.asc())
    ).all()
    return [row[0] for row in rows]


def get_song_chorus_artist_names(db: Session, song: Song) -> list[str]:
    rows = db.execute(
        select(Artist.name).join(SongChorusArtist, SongChorusArtist.artist_id == Artist.id).where(SongChorusArtist.song_id == song.id).order_by(Artist.name.asc())
    ).all()
    return [row[0] for row in rows]


def get_song_lead_artist_ids(db: Session, song: Song) -> list[int]:
    return [row[0] for row in db.execute(select(SongLeadArtist.artist_id).where(SongLeadArtist.song_id == song.id)).all()]


def get_song_chorus_artist_ids(db: Session, song: Song) -> list[int]:
    return [row[0] for row in db.execute(select(SongChorusArtist.artist_id).where(SongChorusArtist.song_id == song.id)).all()]


def get_song_role_artist_names(db: Session, song: Song, model) -> list[str]:
    rows = db.execute(
        select(Artist.name).join(model, model.artist_id == Artist.id).where(model.song_id == song.id).order_by(Artist.name.asc())
    ).all()
    return [row[0] for row in rows]


def get_song_role_artist_ids(db: Session, song: Song, model) -> list[int]:
    return [row[0] for row in db.execute(select(model.artist_id).where(model.song_id == song.id)).all()]


def get_song_artist_text(db: Session, song: Song) -> Optional[str]:
    lead_names = get_song_lead_artist_names(db, song)
    chorus_names = get_song_chorus_artist_names(db, song)
    lead = " / ".join(lead_names) if lead_names else None
    chorus = " / ".join(chorus_names) if chorus_names else None
    if lead and chorus:
        return f"{lead} / {chorus}"
    return lead or chorus


def get_song_lead_artist_name(db: Session, song: Song) -> Optional[str]:
    names = get_song_lead_artist_names(db, song)
    return " / ".join(names) if names else None


def get_song_chorus_artist_name(db: Session, song: Song) -> Optional[str]:
    names = get_song_chorus_artist_names(db, song)
    return " / ".join(names) if names else None


def normalize_audio_format(fmt: Optional[str]) -> str:
    if not fmt:
        return ""
    return str(fmt).strip().lower().lstrip(".")


_CN_SH = ZoneInfo("Asia/Shanghai")


def download_zip_timestamp_tag() -> str:
    """
    ZIP 文件名用时间戳（Asia/Shanghai）：yyyyMMddHHmmss + 五位亚秒（微秒 // 10，00000–99999），
    对应书写习惯 yyyymmddhhMMsssss。
    """
    now = datetime.now(_CN_SH)
    return now.strftime("%Y%m%d%H%M%S") + f"{now.microsecond // 10:05d}"


def safe_download_segment(text: Optional[str], fallback: str = "unknown") -> str:
    if not text or not str(text).strip():
        text = fallback
    bad = '\\/:*?"<>|\n\r\t'
    out = "".join("_" if c in bad else c for c in str(text))
    out = out.strip(" .")
    return out or fallback


def build_song_file_download_basename(db: Session, song: Song, song_file: SongFile) -> tuple[str, str]:
    title = safe_download_segment(song.title, "untitled")
    lead_raw = get_song_lead_artist_name(db, song) or get_song_artist_text(db, song)
    lead = safe_download_segment(lead_raw, "unknown")
    ext = normalize_audio_format(song_file.format) or "bin"
    stem = f"{title}-{lead}"
    return stem, ext


def build_song_file_download_filename(db: Session, song: Song, song_file: SongFile) -> str:
    stem, ext = build_song_file_download_basename(db, song, song_file)
    return f"{stem}.{ext}"


def assign_unique_archive_names(db: Session, files: list[SongFile]) -> list[tuple[SongFile, str]]:
    if not files:
        return []
    song_ids = {f.song_id for f in files}
    songs = {s.id: s for s in db.scalars(select(Song).where(Song.id.in_(song_ids))).all()}
    seen: set[str] = set()
    out: list[tuple[SongFile, str]] = []
    for sf in sorted(files, key=lambda x: (x.song_id, normalize_audio_format(x.format), x.id)):
        song = songs.get(sf.song_id)
        if not song:
            arc = f"missing_{sf.id}.bin"
            if arc in seen:
                arc = f"missing_{sf.id}_{sf.song_id}.bin"
            seen.add(arc)
            out.append((sf, arc))
            continue
        name = build_song_file_download_filename(db, song, sf)
        if name in seen:
            stem, ext = build_song_file_download_basename(db, song, sf)
            name = f"{stem}_{sf.id}.{ext}"
        seen.add(name)
        out.append((sf, name))
    return out


def streaming_download_song_file(db: Session, song_file: SongFile) -> StreamingResponse:
    song = db.scalar(select(Song).where(Song.id == song_file.song_id))
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
    try:
        s3_object = storage.get_object(song_file.object_key)
    except ClientError as exc:
        raise HTTPException(status_code=404, detail="Audio object not found") from exc
    download_name = build_song_file_download_filename(db, song, song_file)
    filename_star = quote(download_name)
    media = song_file.mime_type or "application/octet-stream"
    headers = {
        "Content-Type": media,
        "Content-Length": str(s3_object.get("ContentLength", song_file.file_size)),
        "Content-Disposition": f"attachment; filename*=UTF-8''{filename_star}",
    }
    return StreamingResponse(s3_object["Body"].iter_chunks(), media_type=media, headers=headers)


def zip_song_files_response(db: Session, files: list[SongFile], zip_download_name: str) -> StreamingResponse:
    pairs = assign_unique_archive_names(db, files)
    memory_file = io.BytesIO()
    with zipfile.ZipFile(memory_file, "w", zipfile.ZIP_DEFLATED) as zf:
        for sf, arcname in pairs:
            try:
                s3_object = storage.get_object(sf.object_key)
                content = b"".join(s3_object["Body"].iter_chunks())
                zf.writestr(arcname, content)
            except Exception as e:
                print(f"Error adding file {sf.id} to zip: {e}")
                continue
    memory_file.seek(0)
    zname = quote(zip_download_name)
    headers = {
        "Content-Type": "application/zip",
        "Content-Disposition": f"attachment; filename*=UTF-8''{zname}",
    }
    return StreamingResponse(memory_file, media_type="application/zip", headers=headers)


def resolve_song_files_for_download(db: Session, song_id: int, formats_param: list[str]) -> list[SongFile]:
    files_all = audio_song_files(list(db.scalars(select(SongFile).where(SongFile.song_id == song_id)).all()))
    if not files_all:
        return []
    if not formats_param:
        best = choose_best_file(files_all)
        return [best] if best else []
    want = {normalize_audio_format(f) for f in formats_param if normalize_audio_format(f)}
    if not want:
        best = choose_best_file(files_all)
        return [best] if best else []
    chosen: list[SongFile] = []
    for fmt in sorted(want):
        match = next((x for x in files_all if normalize_audio_format(x.format) == fmt), None)
        if match:
            chosen.append(match)
    seen_ids: set[int] = set()
    unique: list[SongFile] = []
    for f in chosen:
        if f.id not in seen_ids:
            seen_ids.add(f.id)
            unique.append(f)
    return unique


def collect_batch_song_files(db: Session, song_ids: list[int], formats: list[str]) -> list[SongFile]:
    want = {normalize_audio_format(f) for f in formats if normalize_audio_format(f)}
    if not want:
        return []
    result: list[SongFile] = []
    for sid in song_ids:
        files_all = audio_song_files(list(db.scalars(select(SongFile).where(SongFile.song_id == sid)).all()))
        for fmt in sorted(want):
            match = next((x for x in files_all if normalize_audio_format(x.format) == fmt), None)
            if match:
                result.append(match)
    return result


def set_song_artists(db: Session, song_id: int, lead_artist_ids: list[int], chorus_artist_ids: list[int]) -> None:
    db.query(SongLeadArtist).filter(SongLeadArtist.song_id == song_id).delete()
    db.query(SongChorusArtist).filter(SongChorusArtist.song_id == song_id).delete()
    for artist_id in lead_artist_ids:
        if db.scalar(select(Artist).where(Artist.id == artist_id)):
            db.add(SongLeadArtist(song_id=song_id, artist_id=artist_id))
    for artist_id in chorus_artist_ids:
        if db.scalar(select(Artist).where(Artist.id == artist_id)):
            db.add(SongChorusArtist(song_id=song_id, artist_id=artist_id))


def set_song_role_artists(db: Session, song_id: int, artist_ids: list[int], model) -> None:
    db.query(model).filter(model.song_id == song_id).delete()
    for artist_id in artist_ids:
        if db.scalar(select(Artist).where(Artist.id == artist_id)):
            db.add(model(song_id=song_id, artist_id=artist_id))


def get_default_language(db: Session) -> Language:
    language = db.scalar(select(Language).where(func.lower(Language.name) == "普通话"))
    if language:
        return language
    language = Language(name="普通话")
    db.add(language)
    db.commit()
    db.refresh(language)
    return language


def set_song_tags(db: Session, song_id: int, tag_ids: list[int]) -> None:
    db.query(SongTag).filter(SongTag.song_id == song_id).delete()
    valid_tags = db.scalars(select(Tag).where(Tag.id.in_(tag_ids))).all() if tag_ids else []
    for tag in valid_tags:
        db.add(SongTag(song_id=song_id, tag_id=tag.id))


def song_file_variants_out(files: list[SongFile]) -> list[SongFileVariantOut]:
    audio = audio_song_files(files)
    return [
        SongFileVariantOut(file_id=f.id, format=f.format or "")
        for f in sorted(audio, key=lambda x: (x.format or "").lower())
    ]


def build_song_lyrics_out(db: Session, song_id: int) -> SongLyricsOut:
    song_file = get_song_lyric_file(db, song_id)
    if not song_file:
        raise HTTPException(status_code=404, detail="该歌曲暂无歌词")
    try:
        content = read_lyric_file_text(storage, song_file)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"读取歌词失败：{exc}") from exc
    parsed = parse_lrc_content(content)
    return SongLyricsOut(
        filename=(song_file.original_filename or "").strip() or "lyrics.lrc",
        content=content,
        lines=[LyricLineOut(time_ms=line["time_ms"], text=line["text"]) for line in parsed],
    )


def build_song_out(db: Session, song: Song, artist_name: Optional[str], album_name: Optional[str], formats: list[str]) -> SongOut:
    files = list(db.scalars(select(SongFile).where(SongFile.song_id == song.id)).all())
    audio_files = audio_song_files(files)
    best_file = choose_best_file(audio_files) if audio_files else None
    return SongOut(
        id=song.id,
        title=song.title,
        artist=artist_name or get_song_artist_text(db, song),
        lead_artist=get_song_lead_artist_name(db, song),
        chorus_artist=get_song_chorus_artist_name(db, song),
        lead_artists=get_song_lead_artist_names(db, song),
        chorus_artists=get_song_chorus_artist_names(db, song),
        lyricists=get_song_role_artist_names(db, song, SongLyricistArtist),
        composers=get_song_role_artist_names(db, song, SongComposerArtist),
        album=album_name,
        duration_ms=song.duration_ms,
        formats=formats,
        file_variants=song_file_variants_out(files) if files else [],
        tags=get_song_tag_names(db, song.id),
        file_id=best_file.id if best_file else None,
        file_format=best_file.format if best_file else None,
        file_size=best_file.file_size if best_file else None,
        bitrate=best_file.bitrate if best_file else None,
        sample_rate=best_file.sample_rate if best_file else None,
        created_at=best_file.created_at if best_file else song.created_at,
        updated_at=song.updated_at,
        language=get_song_language_name(db, song),
        genre=get_song_genre_name(db, song),
        release_date=song.release_date,
        film_tv=song.film_tv,
        has_lyrics=song_has_lyrics(db, song.id),
    )


def build_song_out_for_file(
    db: Session,
    song: Song,
    file: SongFile,
    artist_name: Optional[str],
    album_name: Optional[str],
    song_formats: list[str],
    tag_names: list[str],
    all_files: Optional[list[SongFile]] = None,
) -> SongOut:
    variants_source = all_files if all_files is not None else [file]
    return SongOut(
        id=song.id,
        title=song.title,
        artist=artist_name or get_song_artist_text(db, song),
        lead_artist=get_song_lead_artist_name(db, song),
        chorus_artist=get_song_chorus_artist_name(db, song),
        lead_artists=get_song_lead_artist_names(db, song),
        chorus_artists=get_song_chorus_artist_names(db, song),
        lyricists=get_song_role_artist_names(db, song, SongLyricistArtist),
        composers=get_song_role_artist_names(db, song, SongComposerArtist),
        album=album_name,
        duration_ms=song.duration_ms,
        formats=song_formats,
        file_variants=song_file_variants_out(variants_source) if variants_source else [],
        tags=tag_names,
        file_id=file.id,
        file_format=file.format,
        file_size=file.file_size,
        bitrate=file.bitrate,
        sample_rate=file.sample_rate,
        created_at=file.created_at,
        updated_at=song.updated_at,
        language=get_song_language_name(db, song),
        genre=get_song_genre_name(db, song),
        release_date=song.release_date or "",
        film_tv=song.film_tv,
        has_lyrics=song_has_lyrics(db, song.id),
    )


_SONG_FILES_COLS_ORDER = [
    "id",
    "song_id",
    "object_key",
    "original_filename",
    "format",
    "mime_type",
    "bitrate",
    "sample_rate",
    "bit_depth",
    "channels",
    "file_size",
    "sha256",
    "is_lossless",
    "is_playable_web",
    "created_at",
]


def _sqlite_song_files_has_unique_on_hash_size(connection) -> bool:
    """是否存在 (sha256, file_size) 上的唯一索引（含 sqlite_autoindex_*，SQLite 禁止对其 DROP INDEX）。"""
    rows = connection.execute(text("PRAGMA index_list('song_files')")).fetchall()
    for row in rows:
        if len(row) < 3:
            continue
        unique = int(row[2] or 0)
        if not unique:
            continue
        idx_name = row[1]
        if not idx_name:
            continue
        info = connection.execute(text(f'PRAGMA index_info("{idx_name}")')).fetchall()
        col_names = sorted(str(c[2]) for c in info if c[2] is not None)
        if col_names == ["file_size", "sha256"]:
            return True
    return False


def _sqlite_rebuild_song_files_without_hash_unique(connection) -> None:
    """表重建：去掉 (sha256, file_size) 唯一约束，保留 PRIMARY KEY、UNIQUE(object_key) 及全部数据。"""
    insp = inspect(connection)
    if "song_files" not in insp.get_table_names():
        return
    present = {c["name"] for c in insp.get_columns("song_files")}
    missing = [n for n in _SONG_FILES_COLS_ORDER if n not in present]
    if missing:
        raise RuntimeError(
            f"song_files 缺少列 {missing}，无法自动迁移；请手动调整库结构或从备份恢复。"
        )
    qcols = ", ".join(f'"{n}"' for n in _SONG_FILES_COLS_ORDER)
    connection.execute(
        text(
            """
            CREATE TABLE song_files__m (
                id INTEGER NOT NULL,
                song_id INTEGER NOT NULL,
                object_key VARCHAR(1024) NOT NULL,
                original_filename VARCHAR(512) NOT NULL,
                format VARCHAR(32) NOT NULL,
                mime_type VARCHAR(64),
                bitrate INTEGER,
                sample_rate INTEGER,
                bit_depth INTEGER,
                channels INTEGER,
                file_size INTEGER NOT NULL,
                sha256 VARCHAR(64) NOT NULL,
                is_lossless BOOLEAN NOT NULL DEFAULT 0,
                is_playable_web BOOLEAN NOT NULL DEFAULT 1,
                created_at DATETIME,
                PRIMARY KEY (id),
                FOREIGN KEY (song_id) REFERENCES songs (id),
                UNIQUE (object_key)
            )
            """
        )
    )
    connection.execute(text(f"INSERT INTO song_files__m ({qcols}) SELECT {qcols} FROM song_files"))
    connection.execute(text("DROP TABLE song_files"))
    connection.execute(text("ALTER TABLE song_files__m RENAME TO song_files"))
    connection.execute(text("CREATE INDEX IF NOT EXISTS ix_song_files_song_id ON song_files (song_id)"))
    connection.execute(text("CREATE INDEX IF NOT EXISTS ix_song_files_format ON song_files (format)"))
    connection.execute(text("CREATE INDEX IF NOT EXISTS ix_song_files_sha256 ON song_files (sha256)"))


def _migrate_drop_song_file_hash_unique(connection) -> None:
    """移除 song_files 上 (sha256, file_size) 全局唯一约束，使合并后可保留多条相同内容记录（不同 object_key）。"""
    dialect = connection.dialect.name
    if dialect == "sqlite":
        # 命名唯一索引可直接删；表内 UNIQUE 会生成 sqlite_autoindex_*，SQLite 不允许 DROP，只能重建表
        connection.execute(text('DROP INDEX IF EXISTS "uq_song_file_hash_size"'))
        if _sqlite_song_files_has_unique_on_hash_size(connection):
            _sqlite_rebuild_song_files_without_hash_unique(connection)
    elif dialect in ("postgresql", "postgres"):
        connection.execute(text("ALTER TABLE song_files DROP CONSTRAINT IF EXISTS uq_song_file_hash_size"))
    elif dialect == "mysql":
        connection.execute(text("ALTER TABLE song_files DROP INDEX uq_song_file_hash_size"))


def ensure_schema() -> None:
    inspector = inspect(engine)
    with engine.begin() as connection:
        if "languages" not in inspector.get_table_names():
            Language.__table__.create(bind=connection, checkfirst=True)
        if "genres" not in inspector.get_table_names():
            Genre.__table__.create(bind=connection, checkfirst=True)
        if "song_genres" not in inspector.get_table_names():
            SongGenre.__table__.create(bind=connection, checkfirst=True)
        if "song_languages" not in inspector.get_table_names():
            SongLanguage.__table__.create(bind=connection, checkfirst=True)
        if "song_lead_artists" not in inspector.get_table_names():
            SongLeadArtist.__table__.create(bind=connection, checkfirst=True)
        if "song_chorus_artists" not in inspector.get_table_names():
            SongChorusArtist.__table__.create(bind=connection, checkfirst=True)
        if "song_lyricist_artists" not in inspector.get_table_names():
            SongLyricistArtist.__table__.create(bind=connection, checkfirst=True)
        if "song_composer_artists" not in inspector.get_table_names():
            SongComposerArtist.__table__.create(bind=connection, checkfirst=True)
        song_columns = {col["name"] for col in inspect(engine).get_columns("songs")}
        if "language_id" not in song_columns:
            connection.execute(text("ALTER TABLE songs ADD COLUMN language_id INTEGER"))
        if "chorus_artist_id" not in song_columns:
            connection.execute(text("ALTER TABLE songs ADD COLUMN chorus_artist_id INTEGER"))
        if "release_date" not in song_columns:
            connection.execute(text("ALTER TABLE songs ADD COLUMN release_date TEXT"))
        if "film_tv" not in song_columns:
            connection.execute(text("ALTER TABLE songs ADD COLUMN film_tv VARCHAR(255)"))
        if "genre_id" not in song_columns:
            connection.execute(text("ALTER TABLE songs ADD COLUMN genre_id INTEGER"))
        artist_columns = {col["name"] for col in inspect(engine).get_columns("artists")}
        if "types" not in artist_columns:
            connection.execute(text("ALTER TABLE artists ADD COLUMN types TEXT"))
        playlist_columns = {col["name"] for col in inspect(engine).get_columns("playlists")}
        if "sort_order" not in playlist_columns:
            connection.execute(text("ALTER TABLE playlists ADD COLUMN sort_order INTEGER DEFAULT 0"))
        if "song_genres" in inspect(engine).get_table_names():
            connection.execute(
                text(
                    "INSERT OR IGNORE INTO song_genres (song_id, genre_id) SELECT id, genre_id FROM songs WHERE genre_id IS NOT NULL"
                )
            )
        if "song_languages" in inspect(engine).get_table_names():
            connection.execute(
                text(
                    "INSERT OR IGNORE INTO song_languages (song_id, language_id) SELECT id, language_id FROM songs WHERE language_id IS NOT NULL"
                )
            )

        if "song_files" in inspector.get_table_names():
            connection.execute(
                text("CREATE TABLE IF NOT EXISTS _schema_migrations (name VARCHAR(128) PRIMARY KEY)")
            )
            done = connection.execute(
                text("SELECT 1 FROM _schema_migrations WHERE name = 'song_file_drop_global_hash_unique_v1'")
            ).first()
            if not done:
                _migrate_drop_song_file_hash_unique(connection)
                connection.execute(
                    text(
                        "INSERT INTO _schema_migrations (name) VALUES ('song_file_drop_global_hash_unique_v1')"
                    )
                )
            done_album_year = connection.execute(
                text("SELECT 1 FROM _schema_migrations WHERE name = 'album_drop_year_v1'")
            ).first()
            if not done_album_year and "albums" in inspector.get_table_names():
                album_columns = {col["name"] for col in inspect(engine).get_columns("albums")}
                if "year" in album_columns:
                    dialect = connection.dialect.name
                    if dialect == "sqlite":
                        connection.execute(text("ALTER TABLE albums DROP COLUMN year"))
                    elif dialect == "mysql":
                        connection.execute(text("ALTER TABLE albums DROP COLUMN year"))
                connection.execute(
                    text("INSERT INTO _schema_migrations (name) VALUES ('album_drop_year_v1')")
                )

    db = next(get_db())
    try:
        db.execute(
            text(
                "CREATE TABLE IF NOT EXISTS _schema_migrations (name VARCHAR(128) PRIMARY KEY)"
            )
        )
        ran_merge = db.scalar(
            text("SELECT 1 FROM _schema_migrations WHERE name = 'merge_duplicate_songs_v1'")
        )
        if not ran_merge:
            merge_duplicate_songs(db)
            db.execute(
                text(
                    "INSERT INTO _schema_migrations (name) VALUES ('merge_duplicate_songs_v1')"
                )
            )

        default_language = get_default_language(db)
        db.execute(text("UPDATE songs SET language_id = :language_id WHERE language_id IS NULL"), {"language_id": default_language.id})
        db.execute(text("UPDATE artists SET types = '歌手' WHERE types IS NULL OR types = ''"))
        songs = db.scalars(select(Song)).all()
        for song in songs:
            if song.artist_id and not db.scalar(select(SongLeadArtist).where(SongLeadArtist.song_id == song.id)):
                db.add(SongLeadArtist(song_id=song.id, artist_id=song.artist_id))
            if song.chorus_artist_id and not db.scalar(select(SongChorusArtist).where(SongChorusArtist.song_id == song.id)):
                db.add(SongChorusArtist(song_id=song.id, artist_id=song.chorus_artist_id))
        playlists = db.scalars(select(Playlist).order_by(Playlist.created_at.asc())).all()
        for index, playlist in enumerate(playlists, start=1):
            if not playlist.sort_order:
                playlist.sort_order = index
        db.commit()
    finally:
        db.close()


@app.on_event("startup")
def startup():
    try:
        Base.metadata.create_all(bind=engine)
        ensure_schema()
        storage.ensure_buckets_retry()
    except OperationalError as e:
        orig = getattr(e, "orig", None)
        msg = str(orig) if orig is not None else str(e)
        if "unable to open database file" in msg.lower() and settings.database_url.startswith("sqlite"):
            raise RuntimeError(
                "SQLite 无法打开或创建数据库文件。若 DATABASE_URL=sqlite:////data/music.db，"
                "在宿主机直接运行（未用 Docker）时通常没有可写的 /data；请改为 "
                "DATABASE_URL=sqlite:///./data/music.db，或在项目下创建 ./data 后使用上述相对路径。"
            ) from e
        raise


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/__debug/client-log")
async def client_debug_log(request: Request):
    body = await request.body()
    if not body:
        return {"ok": False}
    try:
        payload = json.loads(body)
    except json.JSONDecodeError:
        payload = {"raw": body.decode("utf-8", errors="replace")}
    log_path = Path("/data/debug-front-user-menu.ndjson")
    log_path.parent.mkdir(parents=True, exist_ok=True)
    entry = {**payload, "timestamp": datetime.now(ZoneInfo("UTC")).isoformat()}
    with log_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return {"ok": True}


@app.get("/library/stats")
def library_stats(db: Session = Depends(get_db)):
    song_count = db.scalar(select(func.count(Song.id))) or 0
    playlist_count = db.scalar(select(func.count(Playlist.id))) or 0
    return {"song_count": song_count, "playlist_count": playlist_count}


@app.get("/")
def index():
    return FileResponse(static_dir / "index.html")


@app.get("/admin")
def admin_page():
    return FileResponse(static_dir / "admin.html")


@app.get("/admin/scan-progress", response_model=ScanProgress)
def get_scan_progress():
    return ScanProgress(**scan_progress)


@app.post("/admin/scan-progress/reset")
def reset_scan_progress():
    global scan_progress
    scan_progress = {
        "is_scanning": False,
        "total_count": 0,
        "scanned_count": 0,
        "added_count": 0,
        "skipped_count": 0,
        "start_time": None,
        "skipped_details": [],
    }
    return {"status": "reset"}


@app.post("/libraries/scan", response_model=ScanResult)
def trigger_scan(payload: ScanRequest, db: Session = Depends(get_db)):
    global scan_progress
    target = Path(payload.directory or settings.import_root)
    
    if not target.exists() or not target.is_dir():
        raise HTTPException(status_code=400, detail="Invalid directory")
    
    files = [p for p in target.rglob("*") if p.is_file() and p.suffix.lower() in SUPPORTED_EXTENSIONS]
    scan_progress = {
        "is_scanning": True,
        "total_count": len(files),
        "scanned_count": 0,
        "added_count": 0,
        "skipped_count": 0,
        "start_time": __import__("time").time(),
        "skipped_details": [],
    }

    job = scan_directory(db=db, storage=storage, root=target, progress=scan_progress)

    scan_progress["is_scanning"] = False
    scan_progress["scanned_count"] = job.scanned_count
    scan_progress["added_count"] = job.added_count
    scan_progress["skipped_count"] = job.skipped_count

    return ScanResult(
        scan_job_id=job.id,
        status=job.status,
        scanned_count=job.scanned_count,
        added_count=job.added_count,
        skipped_count=job.skipped_count,
        total_count=len(files),
        start_time=scan_progress["start_time"],
        skipped_details=scan_progress.get("skipped_details") or [],
    )


@app.post("/admin/import-directory", response_model=ScanResult)
async def import_directory(files: list[UploadFile] = File(...), db: Session = Depends(get_db)):
    global scan_progress
    
    supported_files = []
    for f in files:
        if Path(f.filename or "").suffix.lower() in SUPPORTED_EXTENSIONS:
            supported_files.append(f)
    
    scan_progress = {
        "is_scanning": True,
        "total_count": len(supported_files),
        "scanned_count": 0,
        "added_count": 0,
        "skipped_count": 0,
        "start_time": __import__("time").time(),
        "skipped_details": [],
    }
    
    scanned_count = 0
    added_count = 0
    skipped_count = 0

    for upload in supported_files:
        suffix = Path(upload.filename or "").suffix.lower()
        if suffix not in SUPPORTED_EXTENSIONS:
            continue

        scanned_count += 1
        scan_progress["scanned_count"] = scanned_count
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            content = await upload.read()
            tmp.write(content)
            tmp_path = Path(tmp.name)

        display_name = upload.filename or tmp_path.name
        try:
            ok, skip_reason, _song_id = ingest_file(
                db,
                storage,
                tmp_path,
                source_filename=upload.filename,
            )
            if ok:
                added_count += 1
                scan_progress["added_count"] = added_count
            else:
                skipped_count += 1
                scan_progress["skipped_count"] = skipped_count
                scan_progress.setdefault("skipped_details", []).append(
                    {"path": display_name, "reason": skip_reason or "未知原因"}
                )
        finally:
            tmp_path.unlink(missing_ok=True)
        
        await __import__("asyncio").sleep(0.01)
    
    scan_progress["is_scanning"] = False
    
    return ScanResult(
        scan_job_id=0,
        status="finished",
        scanned_count=scanned_count,
        added_count=added_count,
        skipped_count=skipped_count,
        total_count=len(supported_files),
        start_time=scan_progress["start_time"],
        skipped_details=scan_progress.get("skipped_details") or [],
    )


@app.get("/songs", response_model=SongListPageOut)
def list_songs(
    keyword: Optional[str] = Query(default=None),
    format: Optional[str] = Query(default=None),
    artists: list[str] = Query(default=[]),
    albums: list[str] = Query(default=[]),
    languages: list[str] = Query(default=[]),
    genre_ids: list[int] = Query(default=[]),
    lead_artists: list[str] = Query(default=[]),
    chorus_artists: list[str] = Query(default=[]),
    lyricists: list[str] = Query(default=[]),
    composers: list[str] = Query(default=[]),
    formats: list[str] = Query(default=[]),
    bitrates: list[int] = Query(default=[]),
    sample_rates: list[int] = Query(default=[]),
    tag_ids: list[int] = Query(default=[]),
    sort_by: str = Query(default="created_at"),
    sort_order: str = Query(default="desc"),
    offset: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    library_total = db.scalar(select(func.count(Song.id))) or 0
    query = select(Song, Artist.name, Album.name).outerjoin(Artist, Song.artist_id == Artist.id).outerjoin(Album, Song.album_id == Album.id)

    if artists:
        query = query.where(Artist.name.in_(artists))
    if albums:
        query = query.where(Album.name.in_(albums))
    if languages:
        language_ids = [lang.id for lang in db.scalars(select(Language).where(Language.name.in_(languages))).all()]
        if language_ids:
            sl_songs = select(SongLanguage.song_id).where(SongLanguage.language_id.in_(language_ids))
            query = query.where(or_(Song.language_id.in_(language_ids), Song.id.in_(sl_songs)))
        else:
            return SongListPageOut(items=[], total=0, library_total=library_total)
    if genre_ids:
        sg_songs = select(SongGenre.song_id).where(SongGenre.genre_id.in_(genre_ids))
        query = query.where(or_(Song.genre_id.in_(genre_ids), Song.id.in_(sg_songs)))

    rows = db.execute(query).all()
    result: list[SongOut] = []
    tag_name_map = {tag.id: tag.name for tag in db.scalars(select(Tag).where(Tag.id.in_(tag_ids))).all()} if tag_ids else {}

    for song, artist_name, album_name in rows:
        files = list(db.scalars(select(SongFile).where(SongFile.song_id == song.id)).all())
        tag_names = get_song_tag_names(db, song.id)
        lead_artist_name = get_song_lead_artist_name(db, song)
        chorus_artist_name = get_song_chorus_artist_name(db, song)
        lead_names = get_song_lead_artist_names(db, song)
        chorus_names = get_song_chorus_artist_names(db, song)
        lyricist_names = get_song_role_artist_names(db, song, SongLyricistArtist)
        composer_names = get_song_role_artist_names(db, song, SongComposerArtist)

        if keyword:
            kw = keyword.lower()
            values = [
                song.title or "",
                lead_artist_name or "",
                chorus_artist_name or "",
                album_name or "",
                song.film_tv or "",
                " / ".join(lyricist_names),
                " / ".join(composer_names),
            ]
            if not any(kw in value.lower() for value in values):
                continue
        if tag_ids and tag_name_map:
            if not (set(tag_name_map.values()) & set(tag_names)):
                continue
        if lead_artists and not any(name in lead_names for name in lead_artists):
            continue
        if chorus_artists and not any(name in chorus_names for name in chorus_artists):
            continue
        if lyricists and not any(name in lyricist_names for name in lyricists):
            continue
        if composers and not any(name in composer_names for name in composers):
            continue

        if not files:
            # 保留仅元数据、无音频文件的歌曲；按格式/码率筛选时无法匹配则不出现在列表
            if format or formats or bitrates or sample_rates:
                continue
            result.append(build_song_out(db, song, artist_name, album_name, []))
            continue

        song_formats = sorted({f.format.lower() for f in audio_song_files(files)})
        candidate_files = audio_song_files(list(files))
        if format:
            candidate_files = [f for f in candidate_files if f.format and f.format.lower() == format.lower()]
        if formats:
            fmts_lower = [x.lower() for x in formats]
            candidate_files = [f for f in candidate_files if f.format and f.format.lower() in fmts_lower]
        if bitrates:
            candidate_files = [f for f in candidate_files if f.bitrate is not None and f.bitrate in bitrates]
        if sample_rates:
            candidate_files = [f for f in candidate_files if f.sample_rate is not None and f.sample_rate in sample_rates]
        if not candidate_files:
            continue
        best_file = choose_best_file(candidate_files)
        result.append(
            build_song_out_for_file(
                db, song, best_file, artist_name, album_name, song_formats, tag_names, all_files=files
            )
        )

    reverse = sort_order.lower() == "desc"

    def sort_value(item: SongOut):
        tag_text = ", ".join(item.tags)
        mapping = {
            "title": item.title or "",
            "artist": item.artist or "",
            "lead_artist": item.lead_artist or "",
            "chorus_artist": item.chorus_artist or "",
            "album": item.album or "",
            "duration_ms": item.duration_ms or 0,
            "file_format": item.file_format or "",
            "file_size": item.file_size or 0,
            "bitrate": item.bitrate or 0,
            "sample_rate": item.sample_rate or 0,
            "created_at": item.created_at.isoformat() if item.created_at else "",
            "updated_at": item.updated_at.isoformat() if item.updated_at else "",
            "release_date": item.release_date or "",
            "film_tv": item.film_tv or "",
            "tags": tag_text,
            "language": item.language or "",
            "genre": item.genre or "",
            "lyricists": ", ".join(item.lyricists or []),
            "composers": ", ".join(item.composers or []),
        }
        return mapping.get(sort_by, mapping["created_at"])

    result = sorted(result, key=sort_value, reverse=reverse)
    total = len(result)
    items = result[offset : offset + limit]
    return SongListPageOut(items=items, total=total, library_total=library_total)


@app.get("/playlists", response_model=list[PlaylistOut])
def list_playlists(db: Session = Depends(get_db)):
    playlists = db.scalars(select(Playlist).order_by(Playlist.sort_order.asc(), Playlist.created_at.asc())).all()
    result = []
    for playlist in playlists:
        song_count = db.scalar(
            select(func.count(PlaylistItem.id)).where(PlaylistItem.playlist_id == playlist.id)
        ) or 0
        result.append(PlaylistOut(id=playlist.id, name=playlist.name, song_count=song_count))
    return result


@app.get("/admin/filter-options", response_model=FilterOptionsOut)
def admin_filter_options(db: Session = Depends(get_db)):
    rows = db.execute(select(Song, Artist.name, Album.name).outerjoin(Artist, Song.artist_id == Artist.id).outerjoin(Album, Song.album_id == Album.id)).all()

    formats = sorted({fmt.format.lower() for fmt in db.scalars(select(SongFile)).all() if fmt.format})
    bitrates = sorted({int(sf.bitrate) for sf in db.scalars(select(SongFile)).all() if sf.bitrate is not None})
    sample_rates = sorted({int(sf.sample_rate) for sf in db.scalars(select(SongFile)).all() if sf.sample_rate is not None})
    tags = [TagOut(id=tag.id, name=tag.name) for tag in db.scalars(select(Tag).order_by(Tag.name.asc())).all()]
    languages = [LanguageOut(id=language.id, name=language.name) for language in db.scalars(select(Language).order_by(Language.name.asc())).all()]
    genres = [GenreOut(id=genre.id, name=genre.name) for genre in db.scalars(select(Genre).order_by(Genre.name.asc())).all()]
    lead_artist_names = sorted({name for song in db.scalars(select(Song)).all() for name in get_song_lead_artist_names(db, song)})
    chorus_artist_names = sorted({name for song in db.scalars(select(Song)).all() for name in get_song_chorus_artist_names(db, song)})
    lyricist_names = sorted({name for song in db.scalars(select(Song)).all() for name in get_song_role_artist_names(db, song, SongLyricistArtist)})
    composer_names = sorted({name for song in db.scalars(select(Song)).all() for name in get_song_role_artist_names(db, song, SongComposerArtist)})
    return FilterOptionsOut(
        artists=lead_artist_names,
        albums=chorus_artist_names,
        lead_artists=lead_artist_names,
        chorus_artists=chorus_artist_names,
        lyricists=lyricist_names,
        composers=composer_names,
        formats=formats,
        bitrates=bitrates,
        sample_rates=sample_rates,
        tags=tags,
        languages=languages,
        genres=genres,
    )


@app.post("/playlists", response_model=PlaylistOut)
def create_playlist(payload: PlaylistCreate, db: Session = Depends(get_db)):
    exists = db.scalar(select(Playlist).where(func.lower(Playlist.name) == payload.name.lower()))
    if exists:
        raise HTTPException(status_code=400, detail="Playlist already exists")
    max_sort_order = db.scalar(select(func.max(Playlist.sort_order))) or 0
    playlist = Playlist(name=payload.name.strip(), sort_order=max_sort_order + 1)
    db.add(playlist)
    db.commit()
    db.refresh(playlist)
    return PlaylistOut(id=playlist.id, name=playlist.name, song_count=0)


@app.put("/playlists/{playlist_id}", response_model=PlaylistOut)
def update_playlist(playlist_id: int, payload: PlaylistUpdate, db: Session = Depends(get_db)):
    playlist = db.scalar(select(Playlist).where(Playlist.id == playlist_id))
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist not found")
    name = payload.name.strip()
    if not name:
        raise HTTPException(status_code=400, detail="Playlist name cannot be empty")
    exists = db.scalar(select(Playlist).where(func.lower(Playlist.name) == name.lower(), Playlist.id != playlist_id))
    if exists:
        raise HTTPException(status_code=400, detail="Playlist already exists")
    playlist.name = name
    db.commit()
    song_count = db.scalar(select(func.count(PlaylistItem.id)).where(PlaylistItem.playlist_id == playlist.id)) or 0
    return PlaylistOut(id=playlist.id, name=playlist.name, song_count=song_count)


@app.delete("/playlists/{playlist_id}")
def delete_playlist(playlist_id: int, db: Session = Depends(get_db)):
    playlist = db.scalar(select(Playlist).where(Playlist.id == playlist_id))
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist not found")
    db.delete(playlist)
    db.commit()
    return {"success": True}


@app.put("/playlists-reorder", response_model=list[PlaylistOut])
def reorder_playlists(payload: PlaylistReorder, db: Session = Depends(get_db)):
    playlists = db.scalars(select(Playlist).where(Playlist.id.in_(payload.playlist_ids))).all()
    by_id = {playlist.id: playlist for playlist in playlists}
    ordered = [by_id[playlist_id] for playlist_id in payload.playlist_ids if playlist_id in by_id]
    remainder = [playlist for playlist in db.scalars(select(Playlist).order_by(Playlist.sort_order.asc(), Playlist.created_at.asc())).all() if playlist.id not in by_id]
    final = ordered + remainder
    for index, playlist in enumerate(final, start=1):
        playlist.sort_order = index
    db.commit()
    result = []
    for playlist in final:
        song_count = db.scalar(select(func.count(PlaylistItem.id)).where(PlaylistItem.playlist_id == playlist.id)) or 0
        result.append(PlaylistOut(id=playlist.id, name=playlist.name, song_count=song_count))
    return result


@app.get("/playlists/{playlist_id}", response_model=PlaylistDetailOut)
def get_playlist(playlist_id: int, db: Session = Depends(get_db)):
    playlist = db.scalar(select(Playlist).where(Playlist.id == playlist_id))
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist not found")

    items = db.scalars(
        select(PlaylistItem).where(PlaylistItem.playlist_id == playlist_id).order_by(PlaylistItem.position.asc())
    ).all()
    songs = []
    for item in items:
        song = db.scalar(select(Song).where(Song.id == item.song_id))
        if not song:
            continue
        artist_name = db.scalar(select(Artist.name).where(Artist.id == song.artist_id))
        album_name = db.scalar(select(Album.name).where(Album.id == song.album_id))
        files = db.scalars(select(SongFile).where(SongFile.song_id == song.id)).all()
        songs.append(build_song_out(db, song, artist_name, album_name, sorted({f.format.lower() for f in files})))
    return PlaylistDetailOut(id=playlist.id, name=playlist.name, songs=songs)


@app.post("/playlists/{playlist_id}/items", response_model=PlaylistOut)
def add_song_to_playlist(playlist_id: int, payload: PlaylistSongCreate, db: Session = Depends(get_db)):
    playlist = db.scalar(select(Playlist).where(Playlist.id == playlist_id))
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist not found")

    song = db.scalar(select(Song).where(Song.id == payload.song_id))
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")

    exists = db.scalar(
        select(PlaylistItem).where(
            PlaylistItem.playlist_id == playlist_id,
            PlaylistItem.song_id == payload.song_id,
        )
    )
    if exists:
        song_count = db.scalar(
            select(func.count(PlaylistItem.id)).where(PlaylistItem.playlist_id == playlist.id)
        ) or 0
        return PlaylistOut(id=playlist.id, name=playlist.name, song_count=song_count)

    max_position = db.scalar(
        select(func.max(PlaylistItem.position)).where(PlaylistItem.playlist_id == playlist_id)
    )
    item = PlaylistItem(
        playlist_id=playlist_id,
        song_id=payload.song_id,
        position=(max_position or 0) + 1,
    )
    db.add(item)
    db.commit()
    song_count = db.scalar(select(func.count(PlaylistItem.id)).where(PlaylistItem.playlist_id == playlist.id)) or 0
    return PlaylistOut(id=playlist.id, name=playlist.name, song_count=song_count)


@app.delete("/playlists/{playlist_id}/items/{song_id}")
def remove_song_from_playlist(playlist_id: int, song_id: int, db: Session = Depends(get_db)):
    item = db.scalar(select(PlaylistItem).where(PlaylistItem.playlist_id == playlist_id, PlaylistItem.song_id == song_id))
    if not item:
        raise HTTPException(status_code=404, detail="Playlist item not found")
    db.delete(item)
    db.commit()
    return {"success": True}


@app.get("/songs/{song_id}", response_model=SongDetailOut)
def get_song(song_id: int, db: Session = Depends(get_db)):
    song = db.scalar(select(Song).where(Song.id == song_id))
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")

    artist_name = db.scalar(select(Artist.name).where(Artist.id == song.artist_id))
    album_name = db.scalar(select(Album.name).where(Album.id == song.album_id))
    files = db.scalars(select(SongFile).where(SongFile.song_id == song_id)).all()
    return SongDetailOut(
        id=song.id,
        title=song.title,
        artist=get_song_artist_text(db, song),
        lead_artist=get_song_lead_artist_name(db, song),
        chorus_artist=get_song_chorus_artist_name(db, song),
        lead_artists=get_song_lead_artist_names(db, song),
        chorus_artists=get_song_chorus_artist_names(db, song),
        lyricists=get_song_role_artist_names(db, song, SongLyricistArtist),
        composers=get_song_role_artist_names(db, song, SongComposerArtist),
        album=album_name,
        duration_ms=song.duration_ms,
        files=[song_file_to_out(f) for f in files],
        tags=get_song_tag_names(db, song.id),
        language=get_song_language_name(db, song),
        language_ids=get_song_language_ids(db, song.id),
        genre=get_song_genre_name(db, song),
        lead_artist_ids=get_song_lead_artist_ids(db, song),
        chorus_artist_ids=get_song_chorus_artist_ids(db, song),
        lyricist_ids=get_song_role_artist_ids(db, song, SongLyricistArtist),
        composer_ids=get_song_role_artist_ids(db, song, SongComposerArtist),
        genre_id=song.genre_id,
        genre_ids=get_song_genre_ids(db, song.id),
        release_date=song.release_date,
        film_tv=song.film_tv,
        has_lyrics=song_has_lyrics(db, song.id),
    )


@app.get("/songs/{song_id}/lyrics", response_model=SongLyricsOut)
def get_song_lyrics(song_id: int, db: Session = Depends(get_db)):
    song = db.scalar(select(Song).where(Song.id == song_id))
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
    return build_song_lyrics_out(db, song_id)


@app.post("/songs/{song_id}/lyrics", response_model=SongLyricsOut)
async def upload_song_lyrics(
    song_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="未选择文件")
    ext = Path(file.filename).suffix.lower()
    if ext not in LYRIC_EXTENSIONS:
        raise HTTPException(status_code=400, detail="仅支持 .lrc 歌词文件")
    song = db.scalar(select(Song).where(Song.id == song_id))
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")

    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        content = await file.read()
        if len(content) > LYRIC_MAX_BYTES:
            raise HTTPException(status_code=400, detail=f"歌词文件不能超过 {LYRIC_MAX_BYTES // 1024}KB")
        tmp.write(content)
        tmp.flush()
        tmp_path = Path(tmp.name)
    try:
        try:
            ingest_lyric_file(db, storage, song_id, tmp_path, original_filename=file.filename)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
    finally:
        tmp_path.unlink(missing_ok=True)
    return build_song_lyrics_out(db, song_id)


@app.delete("/songs/{song_id}/lyrics")
def delete_song_lyrics(song_id: int, db: Session = Depends(get_db)):
    song = db.scalar(select(Song).where(Song.id == song_id))
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
    if not get_song_lyric_file(db, song_id):
        raise HTTPException(status_code=404, detail="该歌曲暂无歌词")
    delete_song_lyric_files(db, storage, song_id)
    db.commit()
    return {"success": True}


@app.put("/songs/{song_id}", response_model=SongDetailOut)
def update_song(song_id: int, payload: SongMetadataUpdate, db: Session = Depends(get_db)):
    song = db.scalar(select(Song).where(Song.id == song_id))
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")

    title_changed = False
    if payload.title is not None:
        title = payload.title.strip()
        if not title:
            raise HTTPException(status_code=400, detail="Title cannot be empty")
        old_title = (song.title or "").strip()
        title_changed = title != old_title
        song.title = title

    current_lead_ids = get_song_lead_artist_ids(db, song)
    current_chorus_ids = get_song_chorus_artist_ids(db, song)
    current_lyricist_ids = get_song_role_artist_ids(db, song, SongLyricistArtist)
    current_composer_ids = get_song_role_artist_ids(db, song, SongComposerArtist)
    if payload.lead_artist_ids is not None or payload.chorus_artist_ids is not None:
        lead_ids = [artist_id for artist_id in (payload.lead_artist_ids if payload.lead_artist_ids is not None else current_lead_ids) if artist_id]
        chorus_ids = [artist_id for artist_id in (payload.chorus_artist_ids if payload.chorus_artist_ids is not None else current_chorus_ids) if artist_id]
        set_song_artists(db, song.id, lead_ids, chorus_ids)
        song.artist_id = lead_ids[0] if lead_ids else None
        song.chorus_artist_id = chorus_ids[0] if chorus_ids else None
    if payload.lyricist_ids is not None:
        set_song_role_artists(db, song.id, [artist_id for artist_id in payload.lyricist_ids if artist_id], SongLyricistArtist)
    elif current_lyricist_ids:
        set_song_role_artists(db, song.id, current_lyricist_ids, SongLyricistArtist)
    if payload.composer_ids is not None:
        set_song_role_artists(db, song.id, [artist_id for artist_id in payload.composer_ids if artist_id], SongComposerArtist)
    elif current_composer_ids:
        set_song_role_artists(db, song.id, current_composer_ids, SongComposerArtist)

    target_artist_id = song.artist_id

    if payload.album is not None:
        album_name = payload.album.strip()
        if album_name:
            album = get_or_create_album(db, album_name, target_artist_id)
            song.album_id = album.id
        else:
            song.album_id = None

    if "duration_ms" in payload.model_dump(exclude_unset=True):
        duration = payload.duration_ms
        if duration is not None and duration < 0:
            raise HTTPException(status_code=400, detail="Duration must be >= 0")
        song.duration_ms = duration

    if payload.tag_ids is not None:
        set_song_tags(db, song.id, payload.tag_ids)

    if payload.language_ids is not None:
        unique_lang = [x for x in payload.language_ids if x]
        for lid in unique_lang:
            if not db.scalar(select(Language).where(Language.id == lid)):
                raise HTTPException(status_code=404, detail=f"Language {lid} not found")
        set_song_languages(db, song.id, unique_lang)
    elif payload.language_id is not None:
        language = db.scalar(select(Language).where(Language.id == payload.language_id))
        if not language:
            raise HTTPException(status_code=404, detail="Language not found")
        set_song_languages(db, song.id, [language.id])

    if payload.genre_ids is not None:
        unique = [g for g in payload.genre_ids if g]
        for gid in unique:
            if not db.scalar(select(Genre).where(Genre.id == gid)):
                raise HTTPException(status_code=404, detail=f"Genre {gid} not found")
        set_song_genres(db, song.id, unique)
    elif payload.genre_id is not None:
        if payload.genre_id == 0:
            set_song_genres(db, song.id, [])
        else:
            genre = db.scalar(select(Genre).where(Genre.id == payload.genre_id))
            if not genre:
                raise HTTPException(status_code=404, detail="Genre not found")
            set_song_genres(db, song.id, [genre.id])

    if payload.release_date is not None:
        song.release_date = payload.release_date.strip() or None

    if "film_tv" in payload.model_dump(exclude_unset=True):
        song.film_tv = (payload.film_tv or "").strip() or None

    if title_changed:
        sync_song_file_names_to_title(db, song)

    db.flush()
    relocate_song_files_storage(db, storage, song)
    db.commit()
    db.refresh(song)

    artist_name = db.scalar(select(Artist.name).where(Artist.id == song.artist_id))
    album_name = db.scalar(select(Album.name).where(Album.id == song.album_id))
    files = db.scalars(select(SongFile).where(SongFile.song_id == song_id)).all()
    return SongDetailOut(
        id=song.id,
        title=song.title,
        artist=get_song_artist_text(db, song),
        lead_artist=get_song_lead_artist_name(db, song),
        chorus_artist=get_song_chorus_artist_name(db, song),
        lead_artists=get_song_lead_artist_names(db, song),
        chorus_artists=get_song_chorus_artist_names(db, song),
        lyricists=get_song_role_artist_names(db, song, SongLyricistArtist),
        composers=get_song_role_artist_names(db, song, SongComposerArtist),
        album=album_name,
        duration_ms=song.duration_ms,
        files=[song_file_to_out(f) for f in files],
        tags=get_song_tag_names(db, song.id),
        language=get_song_language_name(db, song),
        language_ids=get_song_language_ids(db, song.id),
        genre=get_song_genre_name(db, song),
        lead_artist_ids=get_song_lead_artist_ids(db, song),
        chorus_artist_ids=get_song_chorus_artist_ids(db, song),
        lyricist_ids=get_song_role_artist_ids(db, song, SongLyricistArtist),
        composer_ids=get_song_role_artist_ids(db, song, SongComposerArtist),
        genre_id=song.genre_id,
        genre_ids=get_song_genre_ids(db, song.id),
        release_date=song.release_date,
        film_tv=song.film_tv,
        has_lyrics=song_has_lyrics(db, song.id),
    )


@app.delete("/songs/{song_id}")
def delete_song(song_id: int, db: Session = Depends(get_db)):
    song = db.scalar(select(Song).where(Song.id == song_id))
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
    db.query(PlaylistItem).filter(PlaylistItem.song_id == song_id).delete()
    db.query(SongTag).filter(SongTag.song_id == song_id).delete()
    db.query(SongGenre).filter(SongGenre.song_id == song_id).delete()
    db.query(SongLanguage).filter(SongLanguage.song_id == song_id).delete()
    db.query(SongFile).filter(SongFile.song_id == song_id).delete()
    db.delete(song)
    db.commit()
    return {"success": True}


@app.put("/songs/bulk", response_model=list[SongOut])
def bulk_update_songs(payload: BulkSongMetadataUpdate, db: Session = Depends(get_db)):
    if not payload.song_ids:
        raise HTTPException(status_code=400, detail="song_ids cannot be empty")

    songs = db.scalars(select(Song).where(Song.id.in_(payload.song_ids))).all()
    for song in songs:
        target_artist_id = song.artist_id
        if payload.artist is not None:
            artist_name = payload.artist.strip()
            if artist_name:
                artist = get_or_create_artist(db, artist_name)
                target_artist_id = artist.id
                song.artist_id = artist.id
            else:
                target_artist_id = None
                song.artist_id = None

        if payload.album is not None:
            album_name = payload.album.strip()
            if album_name:
                album = get_or_create_album(db, album_name, target_artist_id)
                song.album_id = album.id
            else:
                song.album_id = None

        if payload.tag_ids is not None:
            set_song_tags(db, song.id, payload.tag_ids)

    db.flush()
    for song in songs:
        relocate_song_files_storage(db, storage, song)
    db.commit()

    result = []
    for song in songs:
        artist_name = db.scalar(select(Artist.name).where(Artist.id == song.artist_id))
        album_name = db.scalar(select(Album.name).where(Album.id == song.album_id))
        files = db.scalars(select(SongFile).where(SongFile.song_id == song.id)).all()
        result.append(build_song_out(db, song, artist_name, album_name, sorted({f.format.lower() for f in files})))
    return result


@app.get("/tags", response_model=list[TagOut])
def list_tags(db: Session = Depends(get_db)):
    tags = db.scalars(select(Tag).order_by(Tag.name.asc())).all()
    return [TagOut(
        id=tag.id,
        name=tag.name,
        created_at=tag.created_at.strftime("%Y-%m-%d %H:%M") if tag.created_at else None
    ) for tag in tags]


@app.get("/people", response_model=list[PersonOut])
def list_people(db: Session = Depends(get_db)):
    people = db.scalars(select(Artist).order_by(Artist.name.asc())).all()
    return [PersonOut(
        id=person.id,
        name=person.name,
        types=parse_artist_types(person.types),
        created_at=person.created_at.strftime("%Y-%m-%d %H:%M") if person.created_at else None,
        updated_at=None
    ) for person in people]


@app.post("/people", response_model=PersonOut)
def create_person(payload: PersonCreate, db: Session = Depends(get_db)):
    name = payload.name.strip()
    if not name:
        raise HTTPException(status_code=400, detail="Person name cannot be empty")
    exists = db.scalar(select(Artist).where(func.lower(Artist.name) == name.lower()))
    if exists:
        raise HTTPException(status_code=400, detail="Person already exists")
    person = Artist(name=name, types=encode_artist_types(payload.types or ["歌手"]))
    db.add(person)
    db.commit()
    db.refresh(person)
    return PersonOut(id=person.id, name=person.name, types=parse_artist_types(person.types))


@app.put("/people/{person_id}", response_model=PersonOut)
def update_person(person_id: int, payload: PersonUpdate, db: Session = Depends(get_db)):
    person = db.scalar(select(Artist).where(Artist.id == person_id))
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    name = payload.name.strip()
    if not name:
        raise HTTPException(status_code=400, detail="Person name cannot be empty")
    exists = db.scalar(select(Artist).where(func.lower(Artist.name) == name.lower(), Artist.id != person_id))
    if exists:
        raise HTTPException(status_code=400, detail="Person already exists")
    person.name = name
    person.types = encode_artist_types(payload.types or ["歌手"])
    db.commit()
    db.refresh(person)
    return PersonOut(id=person.id, name=person.name, types=parse_artist_types(person.types))


@app.delete("/people/{person_id}")
def delete_person(person_id: int, db: Session = Depends(get_db)):
    person = db.scalar(select(Artist).where(Artist.id == person_id))
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    db.execute(text("UPDATE songs SET artist_id = NULL WHERE artist_id = :person_id"), {"person_id": person_id})
    db.execute(text("UPDATE songs SET chorus_artist_id = NULL WHERE chorus_artist_id = :person_id"), {"person_id": person_id})
    db.delete(person)
    db.commit()
    return {"success": True}


@app.get("/languages", response_model=list[LanguageOut])
def list_languages(db: Session = Depends(get_db)):
    languages = db.scalars(select(Language).order_by(Language.name.asc())).all()
    return [LanguageOut(
        id=language.id,
        name=language.name,
        created_at=language.created_at.strftime("%Y-%m-%d %H:%M") if language.created_at else None
    ) for language in languages]


@app.post("/languages", response_model=LanguageOut)
def create_language(payload: LanguageCreate, db: Session = Depends(get_db)):
    name = payload.name.strip()
    if not name:
        raise HTTPException(status_code=400, detail="Language name cannot be empty")
    exists = db.scalar(select(Language).where(func.lower(Language.name) == name.lower()))
    if exists:
        raise HTTPException(status_code=400, detail="Language already exists")
    language = Language(name=name)
    db.add(language)
    db.commit()
    db.refresh(language)
    return LanguageOut(id=language.id, name=language.name)


@app.put("/languages/{language_id}", response_model=LanguageOut)
def update_language(language_id: int, payload: LanguageUpdate, db: Session = Depends(get_db)):
    language = db.scalar(select(Language).where(Language.id == language_id))
    if not language:
        raise HTTPException(status_code=404, detail="Language not found")
    name = payload.name.strip()
    if not name:
        raise HTTPException(status_code=400, detail="Language name cannot be empty")
    exists = db.scalar(select(Language).where(func.lower(Language.name) == name.lower(), Language.id != language_id))
    if exists:
        raise HTTPException(status_code=400, detail="Language already exists")
    language.name = name
    db.commit()
    db.refresh(language)
    return LanguageOut(id=language.id, name=language.name)


@app.delete("/languages/{language_id}")
def delete_language(language_id: int, db: Session = Depends(get_db)):
    language = db.scalar(select(Language).where(Language.id == language_id))
    if not language:
        raise HTTPException(status_code=404, detail="Language not found")
    default_language = get_default_language(db)
    replacement_id = default_language.id if default_language.id != language_id else None
    if replacement_id is None:
        replacement = db.scalar(select(Language).where(Language.id != language_id).order_by(Language.id.asc()))
        if not replacement:
            raise HTTPException(status_code=400, detail="Cannot delete the only language")
        replacement_id = replacement.id
    db.execute(text("DELETE FROM song_languages WHERE language_id = :language_id"), {"language_id": language_id})
    db.execute(text("UPDATE songs SET language_id = :replacement_id WHERE language_id = :language_id"), {"replacement_id": replacement_id, "language_id": language_id})
    db.delete(language)
    db.commit()
    return {"success": True}


@app.get("/genres", response_model=list[GenreOut])
def list_genres(db: Session = Depends(get_db)):
    genres = db.scalars(select(Genre).order_by(Genre.name.asc())).all()
    return [GenreOut(
        id=genre.id,
        name=genre.name,
        created_at=genre.created_at.strftime("%Y-%m-%d %H:%M") if genre.created_at else None
    ) for genre in genres]


@app.post("/genres", response_model=GenreOut)
def create_genre(payload: GenreCreate, db: Session = Depends(get_db)):
    name = payload.name.strip()
    if not name:
        raise HTTPException(status_code=400, detail="Genre name cannot be empty")
    exists = db.scalar(select(Genre).where(func.lower(Genre.name) == name.lower()))
    if exists:
        raise HTTPException(status_code=400, detail="Genre already exists")
    genre = Genre(name=name)
    db.add(genre)
    db.commit()
    db.refresh(genre)
    return GenreOut(id=genre.id, name=genre.name)


@app.put("/genres/{genre_id}", response_model=GenreOut)
def update_genre(genre_id: int, payload: GenreUpdate, db: Session = Depends(get_db)):
    genre = db.scalar(select(Genre).where(Genre.id == genre_id))
    if not genre:
        raise HTTPException(status_code=404, detail="Genre not found")
    name = payload.name.strip()
    if not name:
        raise HTTPException(status_code=400, detail="Genre name cannot be empty")
    exists = db.scalar(select(Genre).where(func.lower(Genre.name) == name.lower(), Genre.id != genre_id))
    if exists:
        raise HTTPException(status_code=400, detail="Genre already exists")
    genre.name = name
    db.commit()
    db.refresh(genre)
    return GenreOut(id=genre.id, name=genre.name)


@app.delete("/genres/{genre_id}")
def delete_genre(genre_id: int, db: Session = Depends(get_db)):
    genre = db.scalar(select(Genre).where(Genre.id == genre_id))
    if not genre:
        raise HTTPException(status_code=404, detail="Genre not found")
    db.execute(text("DELETE FROM song_genres WHERE genre_id = :genre_id"), {"genre_id": genre_id})
    db.execute(text("UPDATE songs SET genre_id = NULL WHERE genre_id = :genre_id"), {"genre_id": genre_id})
    db.delete(genre)
    db.commit()
    return {"success": True}


@app.post("/tags", response_model=TagOut)
def create_tag(payload: TagCreate, db: Session = Depends(get_db)):
    name = payload.name.strip()
    if not name:
        raise HTTPException(status_code=400, detail="Tag name cannot be empty")
    exists = db.scalar(select(Tag).where(func.lower(Tag.name) == name.lower()))
    if exists:
        raise HTTPException(status_code=400, detail="Tag already exists")
    tag = Tag(name=name)
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return TagOut(id=tag.id, name=tag.name)


@app.put("/tags/{tag_id}", response_model=TagOut)
def update_tag(tag_id: int, payload: TagUpdate, db: Session = Depends(get_db)):
    tag = db.scalar(select(Tag).where(Tag.id == tag_id))
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    name = payload.name.strip()
    if not name:
        raise HTTPException(status_code=400, detail="Tag name cannot be empty")
    exists = db.scalar(select(Tag).where(func.lower(Tag.name) == name.lower(), Tag.id != tag_id))
    if exists:
        raise HTTPException(status_code=400, detail="Tag already exists")
    tag.name = name
    db.commit()
    db.refresh(tag)
    return TagOut(id=tag.id, name=tag.name)


@app.delete("/tags/{tag_id}")
def delete_tag(tag_id: int, db: Session = Depends(get_db)):
    tag = db.scalar(select(Tag).where(Tag.id == tag_id))
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    db.query(SongTag).filter(SongTag.tag_id == tag_id).delete()
    db.delete(tag)
    db.commit()
    return {"success": True}


@app.get("/songs/{song_id}/play", response_model=PlayResponse)
def get_song_play(
    song_id: int,
    preferred_format: Optional[str] = None,
    file_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    song = db.scalar(select(Song).where(Song.id == song_id))
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")

    files = audio_song_files(list(db.scalars(select(SongFile).where(SongFile.song_id == song_id)).all()))
    if not files:
        raise HTTPException(status_code=404, detail="No file version for this song")

    selected = None
    if file_id:
        selected = next((f for f in files if f.id == file_id), None)
    if not selected and preferred_format:
        selected = next((f for f in files if f.format and f.format.lower() == preferred_format.lower()), None)
    if not selected:
        selected = choose_best_file(files)
    # 试听必须返回浏览器可播资源；.effective_is_playable_web 与入库规则一致，修正历史行 is_playable_web=False 的 FLAC 等
    if selected and not effective_is_playable_web(selected):
        playable_files = [f for f in files if effective_is_playable_web(f)]
        if playable_files:
            selected = choose_best_file(playable_files)
        else:
            raise HTTPException(status_code=400, detail="当前歌曲没有可用于浏览器试听的音频格式")

    return PlayResponse(
        song_id=song_id,
        selected_song_file_id=selected.id,
        selected_format=selected.format,
        stream_url=f"/song-files/{selected.id}/stream",
        download_url=f"/songs/{song_id}/download",
    )


@app.get("/songs/{song_id}/download")
def download_song_bundle(
    song_id: int,
    formats: list[str] = Query(default=[]),
    db: Session = Depends(get_db),
):
    """
    下载歌曲音频。未指定 formats 时使用服务端推荐的一条；指定多种格式时，每格式一条（若存在），
    多于一个文件时打包为 ZIP。包内文件名：{歌名}-{原唱}.{格式}；ZIP 名：{歌名}-{原唱}-{yyyyMMddHHmmss + 五位亚秒}.zip。
    """
    song = db.scalar(select(Song).where(Song.id == song_id))
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
    chosen = resolve_song_files_for_download(db, song_id, formats)
    if not chosen:
        raise HTTPException(status_code=404, detail="没有可下载的音频文件（请检查所选格式是否存在）")
    if len(chosen) == 1:
        return streaming_download_song_file(db, chosen[0])
    title_seg = safe_download_segment(song.title, "untitled")
    lead_raw = get_song_lead_artist_name(db, song) or get_song_artist_text(db, song)
    lead_seg = safe_download_segment(lead_raw, "unknown")
    zip_name = f"{title_seg}-{lead_seg}-{download_zip_timestamp_tag()}.zip"
    return zip_song_files_response(db, chosen, zip_name)


@app.get("/song-files/{song_file_id}/stream")
def stream_song_file(song_file_id: int, request: Request, db: Session = Depends(get_db)):
    song_file = db.scalar(select(SongFile).where(SongFile.id == song_file_id))
    if not song_file:
        raise HTTPException(status_code=404, detail="Song file not found")
    if (song_file.format or "").strip().lower().lstrip(".") == "lrc":
        raise HTTPException(status_code=400, detail="歌词文件不可作为音频流播放")

    range_header = request.headers.get("range")
    try:
        s3_object = storage.get_object(song_file.object_key, byte_range=range_header)
    except ClientError as exc:
        raise HTTPException(status_code=404, detail="Audio object not found") from exc

    body = s3_object["Body"]
    content_type = stream_content_type_for_song_file(song_file)
    headers = {
        "Accept-Ranges": "bytes",
        "Content-Type": content_type,
    }

    if "ContentRange" in s3_object:
        headers["Content-Range"] = s3_object["ContentRange"]
    if "ContentLength" in s3_object:
        headers["Content-Length"] = str(s3_object["ContentLength"])

    status_code = 206 if range_header else 200
    return StreamingResponse(body.iter_chunks(), media_type=content_type, headers=headers, status_code=status_code)


@app.get("/song-files/{song_file_id}/download")
def download_song_file(song_file_id: int, db: Session = Depends(get_db)):
    song_file = db.scalar(select(SongFile).where(SongFile.id == song_file_id))
    if not song_file:
        raise HTTPException(status_code=404, detail="Song file not found")
    return streaming_download_song_file(db, song_file)


@app.patch("/song-files/{song_file_id}", response_model=SongFileOut)
def patch_song_file(song_file_id: int, body: SongFileRenameIn, db: Session = Depends(get_db)):
    """更新展示用原始文件名；扩展名不可改。保存后按当前规则调整对象存储路径（music/原唱/歌名/文件名.格式）。"""
    song_file = db.scalar(select(SongFile).where(SongFile.id == song_file_id))
    if not song_file:
        raise HTTPException(status_code=404, detail="Song file not found")
    fmt = (song_file.format or "").strip().lower().lstrip(".")
    if not fmt:
        raise HTTPException(status_code=400, detail="文件记录缺少格式信息，无法重命名")
    name = body.original_filename.strip()
    if not name:
        raise HTTPException(status_code=400, detail="文件名不能为空")
    if "/" in name or "\\" in name or name in (".", ".."):
        raise HTTPException(status_code=400, detail="文件名不能包含路径分隔符")
    suffix = Path(name).suffix.lower()
    if suffix != f".{fmt}":
        raise HTTPException(
            status_code=400,
            detail=f"扩展名必须为 .{fmt}，不允许修改音频格式",
        )
    if not Path(name).stem.strip():
        raise HTTPException(status_code=400, detail="主文件名不能为空")
    song_file.original_filename = name[:512]
    song = db.scalar(select(Song).where(Song.id == song_file.song_id))
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
    db.flush()
    relocate_song_files_storage(db, storage, song)
    db.commit()
    db.refresh(song_file)
    return song_file_to_out(song_file)


@app.post("/songs/{song_id}/files", response_model=SongFileOut)
async def add_song_file_to_song(
    song_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """向已有歌曲上传并关联一条新音频（对象存储 + song_files）。"""
    if not file.filename:
        raise HTTPException(status_code=400, detail="未选择文件")
    ext = Path(file.filename).suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的格式，支持: {', '.join(sorted(SUPPORTED_EXTENSIONS))}",
        )
    song = db.scalar(select(Song).where(Song.id == song_id))
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")

    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp.flush()
        tmp_path = Path(tmp.name)
    try:
        try:
            song_file = attach_audio_file_to_song(
                db, storage, song_id, tmp_path, original_filename=file.filename
            )
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        except Exception as exc:
            raise HTTPException(status_code=500, detail=f"添加文件失败：{exc}") from exc
    finally:
        tmp_path.unlink(missing_ok=True)

    return song_file_to_out(song_file)


@app.delete("/song-files/{song_file_id}")
def delete_song_file(song_file_id: int, db: Session = Depends(get_db)):
    """删除一条音频文件记录及对象存储中的对应对象。"""
    song_file = db.scalar(select(SongFile).where(SongFile.id == song_file_id))
    if not song_file:
        raise HTTPException(status_code=404, detail="Song file not found")
    try:
        storage.delete_object(song_file.object_key)
    except ClientError:
        pass
    db.delete(song_file)
    db.commit()
    return {"success": True}


@app.post("/admin/songs/batch-download")
def batch_download_songs_post(payload: BatchSongDownloadIn, db: Session = Depends(get_db)):
    """按所选格式批量下载；仅包含各曲中实际存在的格式；单文件直接下载，多文件打 ZIP。"""
    ids = list(dict.fromkeys(int(x) for x in payload.song_ids))
    fmts = list(dict.fromkeys(payload.formats))
    chosen = collect_batch_song_files(db, ids, fmts)
    if not chosen:
        raise HTTPException(status_code=404, detail="在已选歌曲中没有找到所选格式的文件")
    if len(chosen) == 1:
        return streaming_download_song_file(db, chosen[0])
    zip_name = f"music-songs-batch-{download_zip_timestamp_tag()}.zip"
    return zip_song_files_response(db, chosen, zip_name)


@app.post("/admin/merge-duplicate-songs")
def admin_merge_duplicate_songs(db: Session = Depends(get_db)):
    """
    手动再次合并重复歌曲（与启动时自动迁移规则相同）。
    仅合并歌曲元数据与文件归属，不删除任何音频文件或存储对象。
    """
    stats = merge_duplicate_songs(db)
    db.commit()
    return stats


@app.post("/admin/songs/merge-selected")
def admin_merge_selected_songs(payload: SongMergeSelected, db: Session = Depends(get_db)):
    """
    批量合并用户勾选的歌曲：**合并到用户指定的 master_song_id**。
    仅把从曲的 song_files 改挂到主曲；**主曲的元数据（含标签/语言/风格/艺人等）保持不变**。
    歌单项会指向主曲（避免断链）；从曲 Song 行删除。
    """
    ids = sorted({int(x) for x in payload.song_ids if x})
    master_id = int(payload.master_song_id)
    songs = db.scalars(select(Song).where(Song.id.in_(ids))).all()
    if len(songs) != len(ids):
        raise HTTPException(status_code=404, detail="部分歌曲不存在或已删除")
    merged_slaves = 0
    try:
        for sid in ids:
            if sid == master_id:
                continue
            master = db.scalar(select(Song).where(Song.id == master_id))
            slave = db.scalar(select(Song).where(Song.id == sid))
            if master and slave:
                merge_slave_into_master(db, master, slave, merge_metadata=False)
                merged_slaves += 1
        db.commit()
    except IntegrityError as e:
        db.rollback()
        orig = getattr(e, "orig", None)
        detail = str(orig) if orig is not None else str(e)
        raise HTTPException(status_code=409, detail=f"合并失败（数据冲突或唯一约束）: {detail}") from e
    except OperationalError as e:
        db.rollback()
        orig = getattr(e, "orig", None)
        detail = str(orig) if orig is not None else str(e)
        raise HTTPException(status_code=500, detail=f"合并失败（数据库错误）: {detail}") from e
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"合并失败: {str(e)}") from e

    master_song = db.scalar(select(Song).where(Song.id == master_id))
    if master_song:
        try:
            relocate_song_files_storage(db, storage, master_song)
            db.commit()
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=500,
                detail=(
                    "歌曲已合并完成，但同步存储路径失败；可在后台对该曲使用「同步存储路径」重试。"
                    f" 原因: {str(e)}"
                ),
            ) from e
    return {"master_id": master_id, "merged_slave_songs": merged_slaves}


@app.post("/admin/songs/{song_id}/relocate-storage")
def admin_relocate_song_storage(song_id: int, db: Session = Depends(get_db)):
    """
    按当前歌曲元数据，将该曲下所有音频文件的存储键迁移到
    `music/{原唱1&原唱2}/{歌曲名}/{文件名}.{格式}`。桶内 copy 成功后更新库并删旧键。
    供后台对勾选曲目逐首调用以展示进度。
    """
    song = db.scalar(select(Song).where(Song.id == song_id))
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
    try:
        n = relocate_song_files_storage(db, storage, song)
        db.commit()
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return {"song_id": song_id, "files_moved": n, "ok": True}
