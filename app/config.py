from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Personal Music MVP"
    app_version: str = "0.0.6"
    database_url: str = "sqlite:///./music.db"
    #: 连接 PostgreSQL/MySQL 时由 database 模块在 connect 事件中设置会话时区（SQLite 见 datetime_util）
    database_timezone: str = "Asia/Shanghai"

    s3_endpoint_url: str = "http://localhost:9000"
    s3_access_key_id: str = "minioadmin"
    s3_secret_access_key: str = "minioadmin"
    s3_region_name: str = "us-east-1"
    s3_bucket_music: str = "music-files"
    s3_bucket_covers: str = "music-covers"
    s3_presign_expire_seconds: int = 900
    s3_secure: bool = False

    import_root: str = "/import"
    default_format_priority: str = "flac,alac,m4a,aac,mp3,ogg,wav"


@lru_cache
def get_settings() -> Settings:
    return Settings()
