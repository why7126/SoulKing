#!/usr/bin/env python3
"""Migrate MinIO buckets music-files / music-covers into a single soulking bucket.

Usage (from repo root, MinIO on 127.0.0.1:9000):
  python scripts/migrate_minio_to_soulking.py --dry-run
  python scripts/migrate_minio_to_soulking.py
  python scripts/migrate_minio_to_soulking.py --delete-old-buckets

Reads S3_* from .env when present. For Docker-only .env endpoints, pass --endpoint-url.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import boto3
from botocore.client import Config
from botocore.exceptions import ClientError

REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_MUSIC = "music-files"
SOURCE_COVERS = "music-covers"
TARGET_BUCKET = "soulking"


def _load_dotenv() -> None:
    env_path = REPO_ROOT / ".env"
    if not env_path.is_file():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


def _covers_dest_key(source_key: str) -> str:
    if source_key.startswith("covers/"):
        return source_key
    return f"covers/{source_key}"


def _list_object_keys(client, bucket: str) -> list[str]:
    keys: list[str] = []
    paginator = client.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=bucket):
        for obj in page.get("Contents") or []:
            keys.append(obj["Key"])
    return keys


def _bucket_exists(client, name: str) -> bool:
    try:
        client.head_bucket(Bucket=name)
        return True
    except ClientError:
        return False


def _ensure_bucket(client, name: str, dry_run: bool) -> None:
    if _bucket_exists(client, name):
        return
    if dry_run:
        print(f"[dry-run] would create bucket {name}")
        return
    client.create_bucket(Bucket=name)


def _copy_object(
    client,
    *,
    src_bucket: str,
    src_key: str,
    dest_bucket: str,
    dest_key: str,
    dry_run: bool,
) -> None:
    if dry_run:
        print(f"[dry-run] copy s3://{src_bucket}/{src_key} -> s3://{dest_bucket}/{dest_key}")
        return
    client.copy_object(
        Bucket=dest_bucket,
        Key=dest_key,
        CopySource={"Bucket": src_bucket, "Key": src_key},
    )


def _delete_bucket_contents(client, bucket: str, dry_run: bool) -> int:
    total = 0
    while True:
        keys = _list_object_keys(client, bucket)
        if not keys:
            break
        total += len(keys)
        if dry_run:
            for key in keys:
                print(f"[dry-run] delete s3://{bucket}/{key}")
            break
        for i in range(0, len(keys), 1000):
            batch = keys[i : i + 1000]
            client.delete_objects(
                Bucket=bucket,
                Delete={"Objects": [{"Key": k} for k in batch], "Quiet": True},
            )
    return total


def _delete_bucket(client, bucket: str, dry_run: bool) -> None:
    if not _bucket_exists(client, bucket):
        return
    n = _delete_bucket_contents(client, bucket, dry_run)
    if dry_run:
        print(f"[dry-run] delete bucket {bucket} ({n} object(s))")
        return
    remaining = _list_object_keys(client, bucket)
    if remaining:
        raise RuntimeError(f"bucket {bucket} still has {len(remaining)} object(s) after delete")
    client.delete_bucket(Bucket=bucket)
    print(f"deleted bucket {bucket} ({n} object(s) removed)")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="Print actions without writing")
    parser.add_argument(
        "--delete-old-buckets",
        action="store_true",
        help="After successful copy + count check, empty and delete source buckets",
    )
    parser.add_argument(
        "--endpoint-url",
        default=os.environ.get("S3_ENDPOINT_URL", "http://127.0.0.1:9000"),
        help="MinIO endpoint (default: S3_ENDPOINT_URL or http://127.0.0.1:9000)",
    )
    parser.add_argument("--access-key", default=os.environ.get("S3_ACCESS_KEY_ID", "minioadmin"))
    parser.add_argument("--secret-key", default=os.environ.get("S3_SECRET_ACCESS_KEY", "minioadmin"))
    parser.add_argument("--region", default=os.environ.get("S3_REGION_NAME", "us-east-1"))
    args = parser.parse_args()

    _load_dotenv()
    endpoint = args.endpoint_url
    if "host.docker.internal" in endpoint:
        endpoint = "http://127.0.0.1:9000"
        print(f"note: using {endpoint} for migration (host cannot use host.docker.internal)")

    client = boto3.client(
        "s3",
        endpoint_url=endpoint,
        aws_access_key_id=args.access_key or os.environ.get("S3_ACCESS_KEY_ID", "minioadmin"),
        aws_secret_access_key=args.secret_key or os.environ.get("S3_SECRET_ACCESS_KEY", "minioadmin"),
        region_name=args.region,
        config=Config(signature_version="s3v4"),
    )

    dry = args.dry_run
    _ensure_bucket(client, TARGET_BUCKET, dry)

    music_keys: list[str] = []
    if _bucket_exists(client, SOURCE_MUSIC):
        music_keys = _list_object_keys(client, SOURCE_MUSIC)
        print(f"{SOURCE_MUSIC}: {len(music_keys)} object(s)")
        for key in music_keys:
            _copy_object(
                client,
                src_bucket=SOURCE_MUSIC,
                src_key=key,
                dest_bucket=TARGET_BUCKET,
                dest_key=key,
                dry_run=dry,
            )
    else:
        print(f"{SOURCE_MUSIC}: bucket not found, skip")

    cover_keys: list[str] = []
    if _bucket_exists(client, SOURCE_COVERS):
        cover_keys = _list_object_keys(client, SOURCE_COVERS)
        print(f"{SOURCE_COVERS}: {len(cover_keys)} object(s)")
        for key in cover_keys:
            dest_key = _covers_dest_key(key)
            _copy_object(
                client,
                src_bucket=SOURCE_COVERS,
                src_key=key,
                dest_bucket=TARGET_BUCKET,
                dest_key=dest_key,
                dry_run=dry,
            )
    else:
        print(f"{SOURCE_COVERS}: bucket not found, skip")

    if dry:
        print("dry-run complete")
        return 0

    if _bucket_exists(client, TARGET_BUCKET):
        target_keys = set(_list_object_keys(client, TARGET_BUCKET))
        for key in music_keys:
            if key not in target_keys:
                print(f"verify failed: missing {key} in {TARGET_BUCKET}", file=sys.stderr)
                return 1
        for key in cover_keys:
            dest = _covers_dest_key(key)
            if dest not in target_keys:
                print(f"verify failed: missing {dest} in {TARGET_BUCKET}", file=sys.stderr)
                return 1
        print(
            f"verify ok: {len(music_keys)} from {SOURCE_MUSIC}, "
            f"{len(cover_keys)} from {SOURCE_COVERS} -> {TARGET_BUCKET}"
        )

    if args.delete_old_buckets:
        for bucket in (SOURCE_MUSIC, SOURCE_COVERS):
            _delete_bucket(client, bucket, dry_run=False)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
