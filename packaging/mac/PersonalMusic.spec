# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller 规格：生成 PersonalMusic.app（Apple Silicon / darwin-arm64）。"""
from pathlib import Path

from PyInstaller.utils.hooks import collect_data_files

SPECDIR = Path(SPECPATH).resolve()
ROOT = SPECDIR.parent.parent

block_cipher = None

datas = [
    (str(ROOT / "app" / "static"), "app/static"),
]
datas += collect_data_files("botocore")
datas += collect_data_files("boto3")

hiddenimports = [
    "multipart",
    "uvicorn.logging",
    "uvicorn.loops",
    "uvicorn.loops.auto",
    "uvicorn.loops.asyncio",
    "uvicorn.protocols",
    "uvicorn.protocols.http",
    "uvicorn.protocols.http.auto",
    "uvicorn.protocols.websockets",
    "uvicorn.protocols.websockets.auto",
    "uvicorn.lifespan",
    "uvicorn.lifespan.on",
    "sqlalchemy.sql.default_comparator",
    "sqlalchemy.dialects.sqlite",
    "pydantic.deprecated.decorator",
]

a = Analysis(
    [str(SPECDIR / "run_app.py")],
    pathex=[str(ROOT)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="PersonalMusic",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch="arm64",
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    name="PersonalMusic",
)

app = BUNDLE(
    coll,
    name="PersonalMusic.app",
    icon=None,
    bundle_identifier="local.projectmusic.desktop",
    info_plist={
        "CFBundleDisplayName": "Personal Music",
        "CFBundleName": "PersonalMusic",
        "NSHighResolutionCapable": True,
        "LSMinimumSystemVersion": "11.0",
    },
)
