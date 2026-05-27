#!/usr/bin/env python3
"""macOS 桌面应用入口：配置数据目录、启动捆绑的 MinIO、运行 FastAPI 并打开浏览器。"""
from __future__ import annotations

import atexit
import logging
import os
import signal
import subprocess
import sys
import time
import webbrowser
from pathlib import Path


def _is_frozen() -> bool:
    return bool(getattr(sys, "frozen", False))


def _bundle_macos_dir() -> Path:
    """与可执行文件同目录（.app/Contents/MacOS）。"""
    return Path(sys.executable).resolve().parent


def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent.parent


def _app_support() -> Path:
    return Path.home() / "Library/Application Support/PersonalMusic"


def _setup_logging() -> None:
    support = _app_support()
    support.mkdir(parents=True, exist_ok=True)
    log_path = support / "server.log"
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(log_path, encoding="utf-8"),
            logging.StreamHandler(sys.stderr),
        ],
    )


_minio_proc: subprocess.Popen | None = None


def _stop_minio() -> None:
    global _minio_proc
    if _minio_proc is not None and _minio_proc.poll() is None:
        _minio_proc.terminate()
        try:
            _minio_proc.wait(timeout=8)
        except subprocess.TimeoutExpired:
            _minio_proc.kill()
    _minio_proc = None


def _wait_tcp(host: str, port: int, timeout: float = 45) -> bool:
    import socket

    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with socket.create_connection((host, port), timeout=2):
                return True
        except OSError:
            time.sleep(0.25)
    return False


def _configure_env() -> None:
    support = _app_support()
    support.mkdir(parents=True, exist_ok=True)
    imp = support / "import"
    imp.mkdir(exist_ok=True)
    (support / "minio-data").mkdir(parents=True, exist_ok=True)

    db_path = support / "music.db"
    os.environ.setdefault("DATABASE_URL", f"sqlite:///{db_path}")
    os.environ.setdefault("S3_ENDPOINT_URL", "http://127.0.0.1:9000")
    os.environ.setdefault("S3_ACCESS_KEY_ID", "minioadmin")
    os.environ.setdefault("S3_SECRET_ACCESS_KEY", "minioadmin")
    os.environ.setdefault("IMPORT_ROOT", str(imp))


def _start_minio() -> None:
    global _minio_proc
    minio_exe = _bundle_macos_dir() / "minio"
    if not minio_exe.is_file():
        logging.error("未找到 minio，请重新用 packaging/mac/build_mac_app.sh 构建应用包。")
        sys.exit(1)
    data_dir = _app_support() / "minio-data"
    _minio_proc = subprocess.Popen(
        [
            str(minio_exe),
            "server",
            str(data_dir),
            "--address",
            ":9000",
            "--console-address",
            ":9001",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        cwd=str(_app_support()),
    )
    atexit.register(_stop_minio)

    def _handle_term(*_: object) -> None:
        _stop_minio()
        sys.exit(0)

    signal.signal(signal.SIGTERM, _handle_term)
    signal.signal(signal.SIGINT, _handle_term)

    if not _wait_tcp("127.0.0.1", 9000):
        logging.error("MinIO 未在 9000 端口就绪，请查看 %s", _app_support() / "server.log")
        _stop_minio()
        sys.exit(1)


def main() -> None:
    if not _is_frozen():
        sys.path.insert(0, str(_repo_root()))

    _configure_env()
    _setup_logging()

    if _is_frozen():
        _start_minio()
    else:
        if not _wait_tcp("127.0.0.1", 9000, timeout=3):
            logging.error(
                "开发模式需要本机 MinIO（先启动并列目录 ProjectMinio：docker compose -f docker-compose.yaml -p minio up -d）。"
            )
            sys.exit(1)

    # 必须在导入 app 之前完成环境变量，以便 database / settings 正确初始化。
    import uvicorn

    from app.main import app as fastapi_app

    webbrowser.open("http://127.0.0.1:8000/")
    uvicorn.run(fastapi_app, host="127.0.0.1", port=8000, log_level="info")


if __name__ == "__main__":
    main()
