from pathlib import Path

from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import get_settings


def _ensure_sqlite_parent_dir(database_url: str) -> None:
    """为 SQLite 文件库创建父目录，避免 create_all 因目录不存在而失败。"""
    if not database_url.startswith("sqlite:///"):
        return
    path_str = database_url[10:]  # 去掉 "sqlite:///"
    if not path_str or path_str.startswith(":"):
        return
    if path_str.startswith("memory") or path_str == ":memory:":
        return
    try:
        Path(path_str).expanduser().parent.mkdir(parents=True, exist_ok=True)
    except OSError:
        pass


settings = get_settings()
_ensure_sqlite_parent_dir(settings.database_url)

connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}

engine = create_engine(settings.database_url, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


@event.listens_for(engine, "connect")
def _set_connection_timezone(dbapi_connection, _connection_record) -> None:
    """PostgreSQL / MySQL 会话时区设为北京时间；SQLite 无服务端时区，由应用层 now_cn_naive 写入。"""
    url = settings.database_url.lower()
    tz = settings.database_timezone.replace("'", "''")
    try:
        if url.startswith("postgresql") or url.startswith("postgres"):
            cur = dbapi_connection.cursor()
            cur.execute(f"SET TIME ZONE '{tz}'")
            cur.close()
        elif url.startswith("mysql"):
            cur = dbapi_connection.cursor()
            cur.execute("SET time_zone = '+08:00'")
            cur.close()
    except Exception:
        pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
