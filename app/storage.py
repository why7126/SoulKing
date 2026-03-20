from typing import Optional

from botocore.client import Config
import boto3

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
