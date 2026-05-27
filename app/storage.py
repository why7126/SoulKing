import time
from typing import Optional

import boto3
from botocore.client import Config
from botocore.exceptions import EndpointConnectionError

from app.config import get_settings


class S3Storage:
    def __init__(self):
        settings = get_settings()
        self.settings = settings
        self.client = boto3.client(
            "s3",
            endpoint_url=settings.s3_endpoint_url,
            aws_access_key_id=settings.s3_access_key_id,
            aws_secret_access_key=settings.s3_secret_access_key,
            region_name=settings.s3_region_name,
            use_ssl=settings.s3_secure,
            config=Config(signature_version="s3v4"),
        )

    def ensure_buckets(self) -> None:
        existing = {b["Name"] for b in self.client.list_buckets().get("Buckets", [])}
        for name in (self.settings.s3_bucket_music, self.settings.s3_bucket_covers):
            if name not in existing:
                self.client.create_bucket(Bucket=name)

    def ensure_buckets_retry(self, max_wait_seconds: float = 90.0, interval: float = 1.5) -> None:
        """MinIO 可能比应用晚就绪（或未启动）；连接失败时重试，避免 Docker 一启动就退出。"""
        deadline = time.monotonic() + max_wait_seconds
        last: Exception | None = None
        while time.monotonic() < deadline:
            try:
                self.ensure_buckets()
                return
            except EndpointConnectionError as e:
                last = e
                time.sleep(interval)
        raise RuntimeError(
            f"{max_wait_seconds:.0f}s 内无法连接对象存储 {self.settings.s3_endpoint_url}。"
            "请先在本机启动 ProjectMinio（并列目录下）："
            "docker compose -f docker-compose.yaml -p minio up -d"
        ) from last

    def upload_file(self, local_path: str, object_key: str, content_type: Optional[str] = None) -> None:
        if content_type:
            self.client.upload_file(
                Filename=local_path,
                Bucket=self.settings.s3_bucket_music,
                Key=object_key,
                ExtraArgs={"ContentType": content_type},
            )
            return

        self.client.upload_file(
            Filename=local_path,
            Bucket=self.settings.s3_bucket_music,
            Key=object_key,
        )

    def create_presigned_get_url(self, object_key: str, expire_seconds: Optional[int] = None) -> str:
        expires_in = expire_seconds or self.settings.s3_presign_expire_seconds
        return self.client.generate_presigned_url(
            ClientMethod="get_object",
            Params={"Bucket": self.settings.s3_bucket_music, "Key": object_key},
            ExpiresIn=expires_in,
        )

    def get_object(self, object_key: str, byte_range: Optional[str] = None):
        params = {"Bucket": self.settings.s3_bucket_music, "Key": object_key}
        if byte_range:
            params["Range"] = byte_range
        return self.client.get_object(**params)

    def delete_object(self, object_key: str) -> None:
        self.client.delete_object(Bucket=self.settings.s3_bucket_music, Key=object_key)

    def copy_object(self, src_key: str, dest_key: str) -> None:
        bucket = self.settings.s3_bucket_music
        self.client.copy_object(
            Bucket=bucket,
            Key=dest_key,
            CopySource={"Bucket": bucket, "Key": src_key},
        )
