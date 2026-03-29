import hashlib
import mimetypes
from pathlib import Path, PurePosixPath
from typing import Optional

from mutagen import File as MutagenFile
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import Album, Artist, Language, ScanJob, Song, SongFile, SongLeadArtist
from app.storage import S3Storage

SUPPORTED_EXTENSIONS = {".mp3", ".flac", ".m4a", ".aac", ".wav", ".ogg", ".alac", ".ape"}
LOSSLESS_EXTENSIONS = {".flac", ".wav", ".alac", ".ape"}

# 浏览器试听能力以格式为准（与入库时 is_playable_web 一致），避免历史数据中 FLAC 等仍为 False 导致无法播放
BROWSER_PLAYABLE_FORMATS = frozenset({"mp3", "m4a", "aac", "ogg", "wav", "flac"})


def effective_is_playable_web(song_file: SongFile) -> bool:
    fmt = (song_file.format or "").strip().lower().lstrip(".")
    if fmt in BROWSER_PLAYABLE_FORMATS:
        return True
    return bool(song_file.is_playable_web)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def duplicate_content_skip_reason(db: Session, existing: SongFile) -> str:
    """与库中 (sha256, file_size) 重复时的跳过说明，包含对象存储路径（存储键 + s3:// 完整 URI）。"""
    settings = get_settings()
    bucket = settings.s3_bucket_music
    if existing.object_key and existing.object_key.strip():
        key = existing.object_key.strip()
        full_path = f"存储键 {key}；完整 URI s3://{bucket}/{key}"
        parent = str(PurePosixPath(key).parent)
        if parent and parent != ".":
            full_path += f"；所在目录：{parent}"
    else:
        disp = (existing.original_filename or "").strip() or "未知"
        full_path = f"（无存储路径，展示文件名：{disp}）"

    extras: list[str] = []
    song = db.get(Song, existing.song_id)
    if song and (song.title or "").strip():
        extras.append(f"对应歌曲：《{song.title.strip()}》")
    on = (existing.original_filename or "").strip()
    if on and existing.object_key and existing.object_key.strip():
        extras.append(f"已有展示文件名：{on}")
    suffix = f" {'；'.join(extras)}" if extras else ""
    return f"曲库中已存在相同内容（SHA256 与文件大小一致）。已有文件完整路径：{full_path}{suffix}"


def normalize_text(value: Optional[str]) -> str:
    if not value:
        return "unknown"
    return " ".join(value.strip().lower().split())


def sanitize_path_segment(value: Optional[str], fallback: str = "unknown", max_len: int = 200) -> str:
    """对象路径段：去掉非法字符，保留中英文等可读内容（不强制小写）。"""
    if not value or not str(value).strip():
        return fallback
    t = "".join(c for c in str(value).strip() if ord(c) >= 32 or c in "\u3000")
    for bad in ("\r", "\n", "\t"):
        t = t.replace(bad, " ")
    t = t.replace("/", "／").replace("\\", "＼")
    t = " ".join(t.split())
    t = t.strip(" .")
    if not t:
        return fallback
    return t[:max_len]


def get_ordered_lead_artist_names(db: Session, song: Song) -> list[str]:
    """按 SongLeadArtist.id 顺序；若无关联则退回 song.artist_id 对应艺人名。"""
    rows = list(
        db.scalars(
            select(Artist.name)
            .join(SongLeadArtist, SongLeadArtist.artist_id == Artist.id)
            .where(SongLeadArtist.song_id == song.id)
            .order_by(SongLeadArtist.id.asc())
        ).all()
    )
    names = [str(n).strip() for n in rows if n and str(n).strip()]
    if names:
        return names
    if song.artist_id:
        one = db.scalar(select(Artist.name).where(Artist.id == song.artist_id))
        if one and str(one).strip():
            return [str(one).strip()]
    return []


def build_lead_folder_segment(db: Session, song: Song) -> str:
    """目录第一层：原唱1&原唱2（艺人名内 & 替换为全角，避免与分隔符混淆）。"""
    parts = [sanitize_path_segment(n.replace("&", "＆"), "unknown", 120) for n in get_ordered_lead_artist_names(db, song)]
    if not parts:
        return "unknown"
    return "&".join(parts)


def compute_music_object_key(
    db: Session,
    song: Song,
    song_file: SongFile,
    *,
    exclude_file_id: Optional[int] = None,
    reserved_keys: Optional[set[str]] = None,
) -> str:
    """
    music/{原唱1&原唱2}/{歌曲名}/{文件名}.{格式}
    全局 object_key 唯一：若与库中或其它行冲突，则追加 _{sha256 前 12 位} 等后缀。
    """
    lead_part = build_lead_folder_segment(db, song)
    title_part = sanitize_path_segment(song.title, "untitled", 200)
    fmt = (song_file.format or "bin").strip().lower().lstrip(".")
    raw_name = (song_file.original_filename or f"audio.{fmt}").strip()
    stem = Path(raw_name).stem.strip() or "audio"
    stem_s = sanitize_path_segment(stem, "audio", 180)
    _sha = (song_file.sha256 or "")[:12]
    sha_short = _sha if _sha else (str(song_file.id) if song_file.id is not None else "new")

    def exists_conflict(key: str) -> bool:
        q = select(SongFile.id).where(SongFile.object_key == key)
        if exclude_file_id is not None:
            q = q.where(SongFile.id != exclude_file_id)
        if db.scalar(q.limit(1)):
            return True
        if reserved_keys is not None and key in reserved_keys:
            return True
        return False

    base = f"music/{lead_part}/{title_part}/{stem_s}.{fmt}"
    if not exists_conflict(base):
        return base
    alt = f"music/{lead_part}/{title_part}/{stem_s}_{sha_short}.{fmt}"
    if not exists_conflict(alt):
        return alt
    n = 2
    while True:
        cand = f"music/{lead_part}/{title_part}/{stem_s}_{sha_short}_{n}.{fmt}"
        if not exists_conflict(cand):
            return cand
        n += 1
        if n > 500:
            raise RuntimeError("无法分配唯一 object_key")


def relocate_song_files_storage(db: Session, storage: S3Storage, song: Song) -> int:
    """
    按当前歌曲元数据（原唱、歌名、各文件展示名）重新计算 object_key；
    桶内 copy 后更新库并删除旧键。返回实际搬迁的文件数。
    """
    from botocore.exceptions import ClientError

    files = list(db.scalars(select(SongFile).where(SongFile.song_id == song.id).order_by(SongFile.id.asc())).all())
    if not files:
        return 0
    reserved: set[str] = set()
    plan: list[tuple[SongFile, str]] = []
    for sf in files:
        new_key = compute_music_object_key(db, song, sf, exclude_file_id=sf.id, reserved_keys=reserved)
        reserved.add(new_key)
        plan.append((sf, new_key))

    moved = 0
    for sf, new_key in plan:
        old_key = sf.object_key
        if new_key == old_key:
            continue
        try:
            storage.copy_object(old_key, new_key)
        except ClientError:
            continue
        sf.object_key = new_key
        moved += 1
        try:
            storage.delete_object(old_key)
        except ClientError:
            pass
    return moved


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


def lookup_artist_id_if_exists(db: Session, name: str) -> Optional[int]:
    """按名称（忽略大小写）匹配已有艺人；不存在则返回 None，不新建（用于扫描/导入入库）。"""
    n = (name or "").strip()
    if not n:
        return None
    return db.scalar(select(Artist.id).where(func.lower(Artist.name) == n.lower()))


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


def _pick_song_for_ingest(candidates: list[Song], duration_ms: Optional[int]) -> Song:
    """多条同名同艺人时：优先时长 ±2s 内最接近的一条，否则取 id 最小。"""
    if len(candidates) == 1:
        return candidates[0]
    if duration_ms is None:
        return candidates[0]
    in_window = [s for s in candidates if s.duration_ms is not None and abs(int(s.duration_ms) - int(duration_ms)) <= 2000]
    if in_window:
        return min(in_window, key=lambda s: abs(int(s.duration_ms) - int(duration_ms)))
    return candidates[0]


def locate_or_create_song_for_ingest(
    db: Session,
    title: str,
    artist_id: Optional[int],
    album_id: Optional[int],
    duration_ms: Optional[int],
) -> Song:
    """
    扫描/添加歌曲入库：若已存在相同歌名 + 相同主艺人（artist_id）的 Song，则复用，仅追加音频；
    否则新建 Song（与仅按「时长窗口」匹配的 locate_or_create_song 不同）。
    """
    title_clean = (title or "").strip() or "Unknown"
    q = select(Song).where(func.lower(Song.title) == title_clean.lower())
    if artist_id is not None:
        q = q.where(Song.artist_id == artist_id)
    else:
        q = q.where(Song.artist_id.is_(None))
    candidates = list(db.scalars(q.order_by(Song.id.asc())).all())
    if candidates:
        song = _pick_song_for_ingest(candidates, duration_ms)
        if not song.album_id and album_id:
            song.album_id = album_id
        return song

    default_language = db.scalar(select(Language).where(func.lower(Language.name) == "普通话"))
    song = Song(
        title=title_clean,
        artist_id=artist_id,
        album_id=album_id,
        language_id=(default_language.id if default_language else None),
        duration_ms=duration_ms,
    )
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


def attach_audio_file_to_song(
    db: Session,
    storage: S3Storage,
    song_id: int,
    path: Path,
    *,
    original_filename: Optional[str] = None,
) -> SongFile:
    """
    将本地音频文件上传到对象存储并关联到指定歌曲（用于后台「添加文件」）。
    path 通常为临时文件；与扫描入库相同的内容去重规则（sha256+size 全局唯一）。
    """
    if not path.is_file():
        raise ValueError("文件不存在或无法读取")

    display_name = (original_filename or path.name).strip() or path.name
    ext_with_dot = path.suffix.lower()
    if not ext_with_dot:
        ext_with_dot = Path(display_name).suffix.lower()
    if ext_with_dot not in SUPPORTED_EXTENSIONS:
        supported = ", ".join(sorted(SUPPORTED_EXTENSIONS))
        raise ValueError(f"不支持的音频格式，支持: {supported}")

    file_size = path.stat().st_size
    digest = sha256_file(path)

    dup = db.scalar(select(SongFile).where(SongFile.sha256 == digest, SongFile.file_size == file_size))
    if dup:
        raise ValueError(duplicate_content_skip_reason(db, dup))

    metadata = extract_metadata(path)

    song = db.scalar(select(Song).where(Song.id == song_id))
    if not song:
        raise ValueError("歌曲不存在")

    if song.artist_id and not db.scalar(select(SongLeadArtist).where(SongLeadArtist.song_id == song.id)):
        db.add(SongLeadArtist(song_id=song.id, artist_id=song.artist_id))
        db.flush()

    fmt = ext_with_dot.lstrip(".")
    content_type, _ = mimetypes.guess_type(display_name)
    phantom = SongFile(
        song_id=song.id,
        object_key="",
        original_filename=display_name[:512],
        format=fmt,
        mime_type=content_type,
        bitrate=metadata.get("bitrate"),
        sample_rate=metadata.get("sample_rate"),
        bit_depth=metadata.get("bit_depth"),
        channels=metadata.get("channels"),
        file_size=file_size,
        sha256=digest,
        is_lossless=ext_with_dot in LOSSLESS_EXTENSIONS,
        is_playable_web=fmt in {"mp3", "m4a", "aac", "ogg", "wav", "flac"},
    )
    object_key = compute_music_object_key(db, song, phantom)

    storage.upload_file(str(path), object_key, content_type=content_type)

    song_file = SongFile(
        song_id=song.id,
        object_key=object_key,
        original_filename=display_name[:512],
        format=fmt,
        mime_type=content_type,
        bitrate=metadata.get("bitrate"),
        sample_rate=metadata.get("sample_rate"),
        bit_depth=metadata.get("bit_depth"),
        channels=metadata.get("channels"),
        file_size=file_size,
        sha256=digest,
        is_lossless=ext_with_dot in LOSSLESS_EXTENSIONS,
        is_playable_web=fmt in {"mp3", "m4a", "aac", "ogg", "wav", "flac"},
    )
    db.add(song_file)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        try:
            storage.delete_object(object_key)
        except Exception:
            pass
        ex = db.scalar(select(SongFile).where(SongFile.sha256 == digest, SongFile.file_size == file_size))
        if ex:
            raise ValueError(duplicate_content_skip_reason(db, ex))
        raise ValueError("该音频内容已在曲库中存在（唯一约束冲突），无法重复添加") from None
    db.refresh(song_file)
    return song_file


def ingest_file(
    db: Session,
    storage: S3Storage,
    path: Path,
    *,
    source_filename: Optional[str] = None,
) -> tuple[bool, Optional[str]]:
    """
    扫描/导入单文件：若 (sha256, file_size) 已在 song_files 中存在则跳过；
    否则若已有相同歌名 + 主艺人的 Song 则只追加文件，否则新建 Song。
    不入库自动新建艺人：仅当标签中的艺人在库中已存在时才关联主艺人，否则主艺人为空（可在后台再编辑）。

    返回 (True, None) 表示成功；(False, reason) 表示跳过或失败（reason 为人类可读说明）。
    """
    object_key_uploaded: Optional[str] = None
    try:
        file_size = path.stat().st_size
        digest = sha256_file(path)

        exists = db.scalar(select(SongFile).where(SongFile.sha256 == digest, SongFile.file_size == file_size))
        if exists:
            return False, duplicate_content_skip_reason(db, exists)

        metadata = extract_metadata(path)
        source_name = (source_filename or path.name).strip() or path.name
        source_stem = Path(source_name).stem.strip() or "Unknown"
        artist_id = lookup_artist_id_if_exists(db, metadata["artist"])
        album = get_or_create_album(db, metadata["album"], artist_id)
        song = locate_or_create_song_for_ingest(
            db,
            title=source_stem,
            artist_id=artist_id,
            album_id=album.id,
            duration_ms=metadata["duration_ms"],
        )

        if song.artist_id and not db.scalar(select(SongLeadArtist).where(SongLeadArtist.song_id == song.id)):
            db.add(SongLeadArtist(song_id=song.id, artist_id=song.artist_id))
            db.flush()

        ext = path.suffix.lower().lstrip(".")
        content_type, _ = mimetypes.guess_type(str(path))
        phantom = SongFile(
            song_id=song.id,
            object_key="",
            original_filename=source_name[:512],
            format=ext,
            mime_type=content_type,
            bitrate=metadata["bitrate"],
            sample_rate=metadata["sample_rate"],
            bit_depth=metadata["bit_depth"],
            channels=metadata["channels"],
            file_size=file_size,
            sha256=digest,
            is_lossless=path.suffix.lower() in LOSSLESS_EXTENSIONS,
            is_playable_web=ext in {"mp3", "m4a", "aac", "ogg", "wav", "flac"},
        )
        object_key = compute_music_object_key(db, song, phantom)
        storage.upload_file(str(path), object_key, content_type=content_type)
        object_key_uploaded = object_key

        song_file = SongFile(
            song_id=song.id,
            object_key=object_key,
            original_filename=source_name[:512],
            format=ext,
            mime_type=content_type,
            bitrate=metadata["bitrate"],
            sample_rate=metadata["sample_rate"],
            bit_depth=metadata["bit_depth"],
            channels=metadata["channels"],
            file_size=file_size,
            sha256=digest,
            is_lossless=path.suffix.lower() in LOSSLESS_EXTENSIONS,
            is_playable_web=ext in {"mp3", "m4a", "aac", "ogg", "wav", "flac"},
        )
        db.add(song_file)
        db.commit()
        return True, None
    except IntegrityError:
        db.rollback()
        if object_key_uploaded:
            try:
                storage.delete_object(object_key_uploaded)
            except Exception:
                pass
        try:
            rs = path.stat().st_size
            dg = sha256_file(path)
            ex = db.scalar(select(SongFile).where(SongFile.sha256 == dg, SongFile.file_size == rs))
            if ex:
                return False, duplicate_content_skip_reason(db, ex)
        except Exception:
            pass
        return False, "该音频内容已在曲库中存在（唯一约束冲突），无法重复添加"
    except Exception as e:
        db.rollback()
        if object_key_uploaded:
            try:
                storage.delete_object(object_key_uploaded)
            except Exception:
                pass
        msg = str(e).strip() if e else ""
        return False, msg or type(e).__name__


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

        ok, skip_reason = ingest_file(db, storage, path)
        if ok:
            added += 1
            if progress is not None:
                progress["added_count"] = added
        else:
            skipped += 1
            if progress is not None:
                progress["skipped_count"] = skipped
                progress.setdefault("skipped_details", []).append(
                    {"path": str(path), "reason": skip_reason or "未知原因"}
                )

    job.status = "finished"
    job.scanned_count = scanned
    job.added_count = added
    job.skipped_count = skipped
    db.commit()
    db.refresh(job)
    return job
