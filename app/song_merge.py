"""
将多条 Song 在「文件层面」合并：把从曲下**全部** song_files 的 song_id 改为主曲（全部保留记录与 object_key）。

- merge_duplicate_songs / merge_slave_into_master（默认 merge_metadata=True）：另会将标签/语言/风格/艺人、空字段补全等并入主曲（历史去重）。
- merge_metadata=False（后台「合并所选歌曲」）：**主曲元数据完全不动**，仅从曲关联清除后删从曲；歌单仍改指向主曲。
"""
from __future__ import annotations

from collections import defaultdict
from typing import Optional

from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import (
    PlaylistItem,
    Song,
    SongChorusArtist,
    SongComposerArtist,
    SongFile,
    SongGenre,
    SongLanguage,
    SongLeadArtist,
    SongLyricistArtist,
    SongTag,
)

# 与 locate_or_create_song 思路一致：时长差在此范围内视为同一曲
DURATION_TOLERANCE_MS = 5000


def _duration_bucket(duration_ms: Optional[int]) -> Optional[int]:
    if duration_ms is None:
        return None
    return round(duration_ms / 2000) * 2000


def _song_merge_key(song: Song) -> tuple:
    title = (song.title or "").strip().lower()
    artist_key = song.artist_id if song.artist_id is not None else -1
    return (title, artist_key, _duration_bucket(song.duration_ms))


def _duration_pair_ok(a: Optional[int], b: Optional[int]) -> bool:
    if a is None or b is None:
        return True
    return abs(a - b) <= DURATION_TOLERANCE_MS


def _copy_unique_fk_rows(
    db: Session,
    model,
    master_id: int,
    slave_id: int,
    fk_column: str,
) -> None:
    fk_attr = getattr(model, fk_column)
    for row in list(db.scalars(select(model).where(model.song_id == slave_id)).all()):
        fk_val = getattr(row, fk_column)
        exists = db.scalar(select(model).where(model.song_id == master_id, fk_attr == fk_val))
        if not exists:
            db.add(model(song_id=master_id, **{fk_column: fk_val}))
    db.query(model).filter(model.song_id == slave_id).delete()


def _union_artist_role(db: Session, model, master_id: int, slave_id: int) -> None:
    for row in list(db.scalars(select(model).where(model.song_id == slave_id)).all()):
        exists = db.scalar(
            select(model).where(model.song_id == master_id, model.artist_id == row.artist_id)
        )
        if not exists:
            db.add(model(song_id=master_id, artist_id=row.artist_id))
    db.query(model).filter(model.song_id == slave_id).delete()


def _merge_playlist_items(db: Session, master_id: int, slave_id: int) -> None:
    for item in list(db.scalars(select(PlaylistItem).where(PlaylistItem.song_id == slave_id)).all()):
        dup = db.scalar(
            select(PlaylistItem).where(
                PlaylistItem.playlist_id == item.playlist_id,
                PlaylistItem.song_id == master_id,
            )
        )
        if dup:
            db.delete(item)
        else:
            item.song_id = master_id


def _delete_song_metadata_links(db: Session, song_id: int) -> None:
    """删除歌曲的标签/语言/风格/多艺人角色关联（不删 song_files、不删 songs 行）。"""
    for model in (
        SongTag,
        SongGenre,
        SongLanguage,
        SongLeadArtist,
        SongChorusArtist,
        SongLyricistArtist,
        SongComposerArtist,
    ):
        db.query(model).filter(model.song_id == song_id).delete()


def _fill_master_from_slave(master: Song, slave: Song) -> None:
    if not master.album_id and slave.album_id:
        master.album_id = slave.album_id
    if not master.language_id and slave.language_id:
        master.language_id = slave.language_id
    if not master.genre_id and slave.genre_id:
        master.genre_id = slave.genre_id
    if not master.chorus_artist_id and slave.chorus_artist_id:
        master.chorus_artist_id = slave.chorus_artist_id
    if master.duration_ms is None and slave.duration_ms is not None:
        master.duration_ms = slave.duration_ms
    if not master.release_date and slave.release_date:
        master.release_date = slave.release_date
    if not (master.film_tv or "").strip() and (slave.film_tv or "").strip():
        master.film_tv = slave.film_tv


def merge_slave_into_master(
    db: Session,
    master: Song,
    slave: Song,
    *,
    merge_metadata: bool = True,
) -> None:
    """
    合并从曲到主曲：将 slave 下**每一条** SongFile 的 song_id 改为 master（全部保留 DB 行与 object_key）。
   歌单项仍会并入主曲（避免删除歌曲后歌单断链）。

    merge_metadata=True（默认，用于启动时去重）：合并标签/语言/风格/艺人角色，并用从曲补全主曲空字段。
    merge_metadata=False（合并所选歌曲）：**主曲 songs 行及元数据关联一律不改**，仅收文件；从曲的
    标签/语言等关联在删除从曲前清除（不并入主曲）。
    """
    mid, sid = master.id, slave.id
    if mid == sid:
        return

    for sf in db.scalars(select(SongFile).where(SongFile.song_id == sid)):
        sf.song_id = mid

    if merge_metadata:
        _copy_unique_fk_rows(db, SongTag, mid, sid, "tag_id")
        _copy_unique_fk_rows(db, SongGenre, mid, sid, "genre_id")
        _copy_unique_fk_rows(db, SongLanguage, mid, sid, "language_id")

        _union_artist_role(db, SongLeadArtist, mid, sid)
        _union_artist_role(db, SongChorusArtist, mid, sid)
        _union_artist_role(db, SongLyricistArtist, mid, sid)
        _union_artist_role(db, SongComposerArtist, mid, sid)

        _fill_master_from_slave(master, slave)
    else:
        _delete_song_metadata_links(db, sid)

    _merge_playlist_items(db, mid, sid)

    # 勿用 db.delete(slave)：若从曲曾加载过 .files，ORM 同步子集合时可能把已改挂的 SongFile.song_id 置 NULL，触发 NOT NULL。
    db.execute(delete(Song).where(Song.id == sid))
    db.expunge(slave)
    db.flush()


def merge_duplicate_songs(db: Session) -> dict:
    """
    按 (标题规范化、artist_id、时长桶) 分组，组内保留 id 最小为主曲，其余并入。
    若主曲与待合并曲时长均非空且相差超过 DURATION_TOLERANCE_MS，则跳过该条（不合并）。
    """
    songs = list(db.scalars(select(Song).order_by(Song.id.asc())).all())
    groups: dict[tuple, list[Song]] = defaultdict(list)
    for s in songs:
        groups[_song_merge_key(s)].append(s)

    merged_groups = 0
    merged_slaves = 0

    for _key, group in groups.items():
        if len(group) < 2:
            continue
        group.sort(key=lambda s: s.id)
        master = group[0]
        group_merged = 0
        for slave in group[1:]:
            if not _duration_pair_ok(master.duration_ms, slave.duration_ms):
                continue
            merge_slave_into_master(db, master, slave)
            merged_slaves += 1
            group_merged += 1
        if group_merged:
            merged_groups += 1

    return {"merged_duplicate_groups": merged_groups, "merged_slave_songs": merged_slaves}
