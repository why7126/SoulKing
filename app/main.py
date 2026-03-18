from pathlib import Path
import tempfile
from typing import Optional

from botocore.exceptions import ClientError
from fastapi import Depends, FastAPI, File, HTTPException, Query, Request, UploadFile
from fastapi.responses import FileResponse
from fastapi.responses import StreamingResponse
from urllib.parse import quote
from fastapi.staticfiles import StaticFiles
from sqlalchemy import func, inspect, or_, select, text
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import Base, engine, get_db
from app.models import Album, Artist, Genre, Language, Playlist, PlaylistItem, Song, SongChorusArtist, SongComposerArtist, SongFile, SongLeadArtist, SongLyricistArtist, SongTag, Tag
from app.schemas import (
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
    SongMetadataUpdate,
    SongOut,
    LanguageCreate,
    LanguageOut,
    LanguageUpdate,
    TagCreate,
    TagOut,
    TagUpdate,
)
from app.services import choose_best_file, get_or_create_album, get_or_create_artist, scan_directory
from app.services import SUPPORTED_EXTENSIONS, ingest_file
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
}


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


def get_song_language_name(db: Session, song: Song) -> Optional[str]:
    if not song.language_id:
        return None
    return db.scalar(select(Language.name).where(Language.id == song.language_id))


def get_song_genre_name(db: Session, song: Song) -> Optional[str]:
    if not song.genre_id:
        return None
    return db.scalar(select(Genre.name).where(Genre.id == song.genre_id))


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


def build_song_out(db: Session, song: Song, artist_name: Optional[str], album_name: Optional[str], formats: list[str]) -> SongOut:
    files = list(db.scalars(select(SongFile).where(SongFile.song_id == song.id)).all())
    best_file = choose_best_file(files) if files else None
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
        tags=get_song_tag_names(db, song.id),
        file_format=best_file.format if best_file else None,
        file_size=best_file.file_size if best_file else None,
        bitrate=best_file.bitrate if best_file else None,
        sample_rate=best_file.sample_rate if best_file else None,
        created_at=best_file.created_at if best_file else song.created_at,
        language=get_song_language_name(db, song),
                genre=get_song_genre_name(db, song),
        release_date=song.release_date,
    )


def ensure_schema() -> None:
    inspector = inspect(engine)
    with engine.begin() as connection:
        if "languages" not in inspector.get_table_names():
            Language.__table__.create(bind=connection, checkfirst=True)
        if "genres" not in inspector.get_table_names():
            Genre.__table__.create(bind=connection, checkfirst=True)
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
        if "genre_id" not in song_columns:
            connection.execute(text("ALTER TABLE songs ADD COLUMN genre_id INTEGER"))
        artist_columns = {col["name"] for col in inspect(engine).get_columns("artists")}
        if "types" not in artist_columns:
            connection.execute(text("ALTER TABLE artists ADD COLUMN types TEXT"))
        playlist_columns = {col["name"] for col in inspect(engine).get_columns("playlists")}
        if "sort_order" not in playlist_columns:
            connection.execute(text("ALTER TABLE playlists ADD COLUMN sort_order INTEGER DEFAULT 0"))

    db = next(get_db())
    try:
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
    Base.metadata.create_all(bind=engine)
    ensure_schema()
    storage.ensure_buckets()


@app.get("/health")
def health():
    return {"status": "ok"}


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

        try:
            if ingest_file(db, storage, tmp_path):
                added_count += 1
                scan_progress["added_count"] = added_count
            else:
                skipped_count += 1
                scan_progress["skipped_count"] = skipped_count
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
    )


@app.get("/songs", response_model=list[SongOut])
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
    query = select(Song, Artist.name, Album.name).outerjoin(Artist, Song.artist_id == Artist.id).outerjoin(Album, Song.album_id == Album.id)

    if artists:
        query = query.where(Artist.name.in_(artists))
    if albums:
        query = query.where(Album.name.in_(albums))
    if languages:
        language_ids = [lang.id for lang in db.scalars(select(Language).where(Language.name.in_(languages))).all()]
        if language_ids:
            query = query.where(Song.language_id.in_(language_ids))
        else:
            return []
    if genre_ids:
        query = query.where(Song.genre_id.in_(genre_ids))

    rows = db.execute(query).all()
    result: list[SongOut] = []
    for song, artist_name, album_name in rows:
        files = list(db.scalars(select(SongFile).where(SongFile.song_id == song.id)).all())
        if not files:
            continue

        song_formats = sorted({f.format.lower() for f in files})
        tag_names = get_song_tag_names(db, song.id)
        tag_name_map = {tag.id: tag.name for tag in db.scalars(select(Tag).where(Tag.id.in_(tag_ids))).all()} if tag_ids else {}
        best_file = choose_best_file(files)
        lead_artist_name = get_song_lead_artist_name(db, song)
        chorus_artist_name = get_song_chorus_artist_name(db, song)
        lead_names = get_song_lead_artist_names(db, song)
        chorus_names = get_song_chorus_artist_names(db, song)
        lyricist_names = get_song_role_artist_names(db, song, SongLyricistArtist)
        composer_names = get_song_role_artist_names(db, song, SongComposerArtist)
        if keyword:
            kw = keyword.lower()
            values = [song.title or "", lead_artist_name or "", chorus_artist_name or "", album_name or "", " / ".join(lyricist_names), " / ".join(composer_names)]
            if not any(kw in value.lower() for value in values):
                continue

        if format and format.lower() not in song_formats:
            continue
        if formats and not any(fmt.lower() in song_formats for fmt in formats):
            continue
        if bitrates and (best_file.bitrate not in bitrates):
            continue
        if sample_rates and (best_file.sample_rate not in sample_rates):
            continue
        if tag_ids and not set(tag_name_map.values()).issubset(set(tag_names)):
            continue
        if lead_artists and not any(name in lead_names for name in lead_artists):
            continue
        if chorus_artists and not any(name in chorus_names for name in chorus_artists):
            continue
        if lyricists and not any(name in lyricist_names for name in lyricists):
            continue
        if composers and not any(name in composer_names for name in composers):
            continue

        result.append(
            SongOut(
                id=song.id,
                title=song.title,
                artist=get_song_artist_text(db, song),
                lead_artist=lead_artist_name,
                chorus_artist=chorus_artist_name,
                lead_artists=lead_names,
                chorus_artists=chorus_names,
                lyricists=lyricist_names,
                composers=composer_names,
                album=album_name,
                duration_ms=song.duration_ms,
                formats=song_formats,
                tags=tag_names,
                file_format=best_file.format,
                file_size=best_file.file_size,
                bitrate=best_file.bitrate,
                sample_rate=best_file.sample_rate,
                created_at=best_file.created_at,
                language=get_song_language_name(db, song),
                genre=get_song_genre_name(db, song),
                release_date=song.release_date or "",
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
            "release_date": item.release_date or "",
            "tags": tag_text,
            "language": item.language or "",
            "lyricists": ", ".join(item.lyricists or []),
            "composers": ", ".join(item.composers or []),
        }
        return mapping.get(sort_by, mapping["created_at"])

    result = sorted(result, key=sort_value, reverse=reverse)
    return result[offset : offset + limit]


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
        files=[SongFileOut.model_validate(f) for f in files],
        tags=get_song_tag_names(db, song.id),
        language=get_song_language_name(db, song),
        genre=get_song_genre_name(db, song),
        lead_artist_ids=get_song_lead_artist_ids(db, song),
        chorus_artist_ids=get_song_chorus_artist_ids(db, song),
        lyricist_ids=get_song_role_artist_ids(db, song, SongLyricistArtist),
        composer_ids=get_song_role_artist_ids(db, song, SongComposerArtist),
        genre_id=song.genre_id,
        release_date=song.release_date,
    )


@app.put("/songs/{song_id}", response_model=SongDetailOut)
def update_song(song_id: int, payload: SongMetadataUpdate, db: Session = Depends(get_db)):
    song = db.scalar(select(Song).where(Song.id == song_id))
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")

    if payload.title is not None:
        title = payload.title.strip()
        if not title:
            raise HTTPException(status_code=400, detail="Title cannot be empty")
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

    if payload.duration_ms is not None:
        if payload.duration_ms < 0:
            raise HTTPException(status_code=400, detail="Duration must be >= 0")
        song.duration_ms = payload.duration_ms

    if payload.tag_ids is not None:
        set_song_tags(db, song.id, payload.tag_ids)

    if payload.language_id is not None:
        language = db.scalar(select(Language).where(Language.id == payload.language_id))
        if not language:
            raise HTTPException(status_code=404, detail="Language not found")
        song.language_id = language.id

    if payload.genre_id is not None:
        if payload.genre_id == 0:
            song.genre_id = None
        else:
            genre = db.scalar(select(Genre).where(Genre.id == payload.genre_id))
            if not genre:
                raise HTTPException(status_code=404, detail="Genre not found")
            song.genre_id = genre.id

    if payload.release_date is not None:
        song.release_date = payload.release_date.strip() or None

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
        files=[SongFileOut.model_validate(f) for f in files],
        tags=get_song_tag_names(db, song.id),
        language=get_song_language_name(db, song),
                genre=get_song_genre_name(db, song),
        lead_artist_ids=get_song_lead_artist_ids(db, song),
        chorus_artist_ids=get_song_chorus_artist_ids(db, song),
        lyricist_ids=get_song_role_artist_ids(db, song, SongLyricistArtist),
        composer_ids=get_song_role_artist_ids(db, song, SongComposerArtist),
        release_date=song.release_date,
    )


@app.delete("/songs/{song_id}")
def delete_song(song_id: int, db: Session = Depends(get_db)):
    song = db.scalar(select(Song).where(Song.id == song_id))
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
    db.query(PlaylistItem).filter(PlaylistItem.song_id == song_id).delete()
    db.query(SongTag).filter(SongTag.song_id == song_id).delete()
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
def get_song_play(song_id: int, preferred_format: Optional[str] = None, db: Session = Depends(get_db)):
    song = db.scalar(select(Song).where(Song.id == song_id))
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")

    files = list(db.scalars(select(SongFile).where(SongFile.song_id == song_id)).all())
    if not files:
        raise HTTPException(status_code=404, detail="No file version for this song")

    selected = None
    if preferred_format:
        selected = next((f for f in files if f.format.lower() == preferred_format.lower()), None)
    if not selected:
        selected = choose_best_file(files)

    return PlayResponse(
        song_id=song_id,
        selected_song_file_id=selected.id,
        selected_format=selected.format,
        stream_url=f"/song-files/{selected.id}/stream",
        download_url=f"/song-files/{selected.id}/download",
    )


@app.get("/song-files/{song_file_id}/stream")
def stream_song_file(song_file_id: int, request: Request, db: Session = Depends(get_db)):
    song_file = db.scalar(select(SongFile).where(SongFile.id == song_file_id))
    if not song_file:
        raise HTTPException(status_code=404, detail="Song file not found")

    range_header = request.headers.get("range")
    try:
        s3_object = storage.get_object(song_file.object_key, byte_range=range_header)
    except ClientError as exc:
        raise HTTPException(status_code=404, detail="Audio object not found") from exc

    body = s3_object["Body"]
    headers = {
        "Accept-Ranges": "bytes",
        "Content-Type": song_file.mime_type or "application/octet-stream",
    }

    if "ContentRange" in s3_object:
        headers["Content-Range"] = s3_object["ContentRange"]
    if "ContentLength" in s3_object:
        headers["Content-Length"] = str(s3_object["ContentLength"])

    status_code = 206 if range_header else 200
    return StreamingResponse(body.iter_chunks(), media_type=song_file.mime_type, headers=headers, status_code=status_code)


@app.get("/song-files/{song_file_id}/download")
def download_song_file(song_file_id: int, db: Session = Depends(get_db)):
    song_file = db.scalar(select(SongFile).where(SongFile.id == song_file_id))
    if not song_file:
        raise HTTPException(status_code=404, detail="Song file not found")
    try:
        s3_object = storage.get_object(song_file.object_key)
    except ClientError as exc:
        raise HTTPException(status_code=404, detail="Audio object not found") from exc

    filename = quote(song_file.original_filename)
    headers = {
        "Content-Type": song_file.mime_type or "application/octet-stream",
        "Content-Length": str(s3_object.get("ContentLength", song_file.file_size)),
        "Content-Disposition": f"attachment; filename*=UTF-8''{filename}",
    }
    return StreamingResponse(s3_object["Body"].iter_chunks(), media_type=song_file.mime_type, headers=headers)


@app.get("/admin/songs/batch-download")
def batch_download_songs(song_ids: str = Query(...), db: Session = Depends(get_db)):
    import io
    import zipfile
    
    ids = [int(x.strip()) for x in song_ids.split(",") if x.strip().isdigit()]
    if not ids:
        raise HTTPException(status_code=400, detail="No valid song IDs provided")
    
    song_files = db.scalars(select(SongFile).where(SongFile.song_id.in_(ids))).all()
    if not song_files:
        raise HTTPException(status_code=404, detail="No song files found")
    
    memory_file = io.BytesIO()
    with zipfile.ZipFile(memory_file, "w", zipfile.ZIP_DEFLATED) as zf:
        for sf in song_files:
            try:
                s3_object = storage.get_object(sf.object_key)
                content = b"".join(list(s3_object["Body"].iter_chunks()))
                safe_name = sf.original_filename or f"song_{sf.id}.{sf.format}"
                zf.writestr(safe_name, content)
            except Exception as e:
                print(f"Error adding file {sf.id} to zip: {e}")
                continue
    
    memory_file.seek(0)
    headers = {
        "Content-Type": "application/zip",
        "Content-Disposition": f"attachment; filename*=UTF-8''music_batch_{len(ids)}.zip",
    }
    return StreamingResponse(memory_file, media_type="application/zip", headers=headers)
