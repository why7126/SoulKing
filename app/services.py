import hashlib
import mimetypes
from pathlib import Path
from typing import Optional

from mutagen import File as MutagenFile
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import Album, Artist, Language, ScanJob, Song, SongFile
from app.storage import S3Storage

SUPPORTED_EXTENSIONS = {".mp3", ".flac", ".m4a", ".aac", ".wav", ".ogg", ".alac"}
LOSSLESS_EXTENSIONS = {".flac", ".wav", ".alac"}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def normalize_text(value: Optional[str]) -> str:
    if not value:
        return "unknown"
    return " ".join(value.strip().lower().split())


def extract_metadata(path: Path) -> dict:
    audio = MutagenFile(path)
    tags = audio.tags if audio else {}

    def _first(values, fallback=""):
        if not values:
            return fallback
        if isinstance(values, str):
            return values
        try:
            return str(values[0])
        except Exception:
            return fallback

    duration_ms = int(audio.info.length * 1000) if audio and getattr(audio, "info", None) else None
    sample_rate = getattr(audio.info, "sample_rate", None) if audio and getattr(audio, "info", None) else None
    channels = getattr(audio.info, "channels", None) if audio and getattr(audio, "info", None) else None
    bitrate = getattr(audio.info, "bitrate", None) if audio and getattr(audio, "info", None) else None
    bit_depth = getattr(audio.info, "bits_per_sample", None) if audio and getattr(audio, "info", None) else None

    title = _first((tags.get("TIT2") if tags else None), fallback=path.stem)
    artist = _first((tags.get("TPE1") if tags else None), fallback="Unknown Artist")
    album = _first((tags.get("TALB") if tags else None), fallback="Unknown Album")

    if not title or title == "":
        title = path.stem
    if not artist:
        artist = "Unknown Artist"
    if not album:
        album = "Unknown Album"

    return {
        "title": str(title),
        "artist": str(artist),
        "album": str(album),
        "duration_ms": duration_ms,
        "sample_rate": sample_rate,
        "channels": channels,
        "bitrate": int(bitrate / 1000) if bitrate else None,
        "bit_depth": bit_depth,
    }


def get_or_create_artist(db: Session, name: str) -> Artist:
    artist = db.scalar(select(Artist).where(func.lower(Artist.name) == name.lower()))
    if artist:
        return artist
    artist = Artist(name=name)
    db.add(artist)
    db.flush()
    return artist


def get_or_create_album(db: Session, name: str, artist_id: Optional[int]) -> Album:
    album = db.scalar(select(Album).where(func.lower(Album.name) == name.lower(), Album.artist_id == artist_id))
    if album:
        return album
    album = Album(name=name, artist_id=artist_id)
    db.add(album)
    db.flush()
    return album


def locate_or_create_song(db: Session, title: str, artist_id: Optional[int], album_id: Optional[int], duration_ms: Optional[int]) -> Song:
    duration_low = (duration_ms - 2000) if duration_ms else None
    duration_high = (duration_ms + 2000) if duration_ms else None

    query = select(Song).where(func.lower(Song.title) == title.lower(), Song.artist_id == artist_id)
    if duration_ms is not None:
        query = query.where(Song.duration_ms >= duration_low, Song.duration_ms <= duration_high)

    song = db.scalar(query)
    if song:
        if not song.album_id and album_id:
            song.album_id = album_id
        return song

    default_language = db.scalar(select(Language).where(func.lower(Language.name) == "普通话"))
    song = Song(title=title, artist_id=artist_id, album_id=album_id, language_id=(default_language.id if default_language else None), duration_ms=duration_ms)
    db.add(song)
    db.flush()
    return song


def choose_best_file(files: list[SongFile]) -> SongFile:
    settings = get_settings()
    priorities = [p.strip().lower() for p in settings.default_format_priority.split(",") if p.strip()]
    priority_map = {fmt: idx for idx, fmt in enumerate(priorities)}

    def sort_key(song_file: SongFile):
        rank = priority_map.get(song_file.format.lower(), 999)
        bitrate = song_file.bitrate or 0
        sample_rate = song_file.sample_rate or 0
        return (rank, -bitrate, -sample_rate)

    return sorted(files, key=sort_key)[0]


def ingest_file(db: Session, storage: S3Storage, path: Path) -> bool:
    file_size = path.stat().st_size
    digest = sha256_file(path)

    exists = db.scalar(select(SongFile).where(SongFile.sha256 == digest, SongFile.file_size == file_size))
    if exists:
        return False

    metadata = extract_metadata(path)
    artist = get_or_create_artist(db, metadata["artist"])
    album = get_or_create_album(db, metadata["album"], artist.id)
    song = locate_or_create_song(
        db,
        title=metadata["title"],
        artist_id=artist.id,
        album_id=album.id,
        duration_ms=metadata["duration_ms"],
    )

    ext = path.suffix.lower().lstrip(".")
    object_key = f"music/{normalize_text(artist.name)}/{normalize_text(album.name)}/{song.id}/{digest}.{ext}"
    content_type, _ = mimetypes.guess_type(str(path))
    storage.upload_file(str(path), object_key, content_type=content_type)

    song_file = SongFile(
        song_id=song.id,
        object_key=object_key,
        original_filename=path.name,
        format=ext,
        mime_type=content_type,
        bitrate=metadata["bitrate"],
        sample_rate=metadata["sample_rate"],
        bit_depth=metadata["bit_depth"],
        channels=metadata["channels"],
        file_size=file_size,
        sha256=digest,
        is_lossless=path.suffix.lower() in LOSSLESS_EXTENSIONS,
        is_playable_web=ext in {"mp3", "m4a", "aac", "ogg", "wav"},
    )
    db.add(song_file)
    db.commit()
    return True


def scan_directory(db: Session, storage: S3Storage, root: Path, progress: dict = None) -> ScanJob:
    job = ScanJob(root_path=str(root), status="running")
    db.add(job)
    db.commit()
    db.refresh(job)

    if not root.exists() or not root.is_dir():
        job.status = "failed"
        db.commit()
        return job

    scanned = 0
    added = 0
    skipped = 0

    for path in root.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue

        scanned += 1
        if progress is not None:
            progress["scanned_count"] = scanned
        
        if ingest_file(db, storage, path):
            added += 1
            if progress is not None:
                progress["added_count"] = added
        else:
            skipped += 1
            if progress is not None:
                progress["skipped_count"] = skipped

    job.status = "finished"
    job.scanned_count = scanned
    job.added_count = added
    job.skipped_count = skipped
    db.commit()
    db.refresh(job)
    return job
