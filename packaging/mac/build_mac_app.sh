#!/usr/bin/env bash
# 在 Apple Silicon Mac 上构建 PersonalMusic.app 与 PersonalMusic.dmg。
# 依赖：Xcode 命令行工具（codesign/hdiutil）、Python 3.12+、网络（下载 MinIO）。
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

ARCH="$(uname -m)"
if [[ "$ARCH" != "arm64" ]]; then
  echo "请在 Apple Silicon (arm64) Mac 上运行本脚本；当前架构: $ARCH" >&2
  exit 1
fi

VENV="$ROOT/.venv-mac-build"
if [[ ! -d "$VENV" ]]; then
  if command -v python3.12 >/dev/null 2>&1; then
    python3.12 -m venv "$VENV"
  else
    python3 -m venv "$VENV"
  fi
fi
# shellcheck source=/dev/null
source "$VENV/bin/activate"
pip install -q -U pip
pip install -q -r "$ROOT/requirements.txt" "pyinstaller>=6.3"

rm -rf "$ROOT/build/personal-music" "$ROOT/dist/PersonalMusic" "$ROOT/dist/PersonalMusic.app"
pyinstaller "$ROOT/packaging/mac/PersonalMusic.spec" --distpath "$ROOT/dist" --workpath "$ROOT/build/personal-music" --noconfirm

MINIO_URL="https://dl.min.io/server/minio/release/darwin-arm64/minio"
MINIO_DST="$ROOT/dist/PersonalMusic.app/Contents/MacOS/minio"
echo "下载 MinIO (darwin-arm64)…"
curl -fsSL -o "$MINIO_DST" "$MINIO_URL"
chmod +x "$MINIO_DST"

APP_PATH="$ROOT/dist/PersonalMusic.app"
if [[ -n "${CODESIGN_IDENTITY:-}" ]]; then
  echo "使用身份签名: $CODESIGN_IDENTITY"
  codesign --force --deep --sign "$CODESIGN_IDENTITY" "$APP_PATH"
else
  echo "未设置 CODESIGN_IDENTITY，使用 ad-hoc 签名（仅本机友好）"
  codesign --force --deep --sign - "$APP_PATH"
fi

DMG_PATH="$ROOT/dist/PersonalMusic.dmg"
rm -f "$DMG_PATH"
hdiutil create -volname "Personal Music" -srcfolder "$APP_PATH" -ov -format UDZO "$DMG_PATH"

echo "完成:"
echo "  应用: $APP_PATH"
echo "  镜像: $DMG_PATH"
echo "数据目录: ~/Library/Application Support/PersonalMusic/（数据库、import；应用包仍内置 MinIO 数据目录）"
