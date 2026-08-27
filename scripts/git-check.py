#!/usr/bin/env python3
"""Pre-push Git safety check for tracked and staged files."""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAX_TEXT_BYTES = 512 * 1024
MAX_FILE_BYTES = 10 * 1024 * 1024

RUNTIME_PATTERNS = (
    re.compile(r"(^|/)data/(runtime|uploads|tmp|minio|mysql|s3)(/|$)"),
    re.compile(r"\.(sqlite|sqlite3|db|db-wal|db-shm)$", re.IGNORECASE),
)
REAL_ENV_PATTERNS = (
    re.compile(r"(^|/)\.env($|\.)"),
    re.compile(r"(^|/)deploy/.+\.env$"),
    re.compile(r"(^|/)scripts/build-images\.env$"),
)
SECRET_PATTERNS = (
    re.compile(r"(?i)(authorization:\s*bearer\s+)[A-Za-z0-9._~+/=-]{12,}"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |)PRIVATE KEY-----"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"(?i)(mysql|postgresql)://[^\\s]+"),
    re.compile(r"(?i)(minio|s3|aws).*(secret|access).*(=|:)\s*['\"]?(?!change-me|example|placeholder|localhost|admin|test|dev)[A-Za-z0-9._~+/=-]{24,}"),
)
LOCAL_PATH_PATTERNS = (
    re.compile(r"/Users/(?!<)[^/`\s]+/"),
    re.compile(r"/home/(?!<)[^/`\s]+/"),
    re.compile(r"/private/var/folders/"),
)
ALLOWED_ENV_EXAMPLES = (
    ".env.example",
    "build-images.env.example",
)
SKIP_PREFIXES = (
    "node_modules/",
    "dist/",
    "coverage/",
    "build/",
)


def run_git(args: list[str]) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return result.stdout


def tracked_and_staged_files() -> set[str]:
    tracked = set(run_git(["ls-files"]).splitlines())
    staged = set(run_git(["diff", "--cached", "--name-only", "--diff-filter=ACMR"]).splitlines())
    return {path for path in tracked | staged if path}


def all_files() -> set[str]:
    return {path for path in run_git(["ls-files"]).splitlines() if path}


def is_binary_or_large(path: Path) -> tuple[bool, int]:
    try:
        size = path.stat().st_size
    except OSError:
        return False, 0
    if size > MAX_FILE_BYTES:
        return True, size
    try:
        chunk = path.read_bytes()[:4096]
    except OSError:
        return False, size
    return b"\0" in chunk, size


def read_text(path: Path) -> str | None:
    try:
        data = path.read_bytes()
    except OSError:
        return None
    if len(data) > MAX_TEXT_BYTES or b"\0" in data[:4096]:
        return None
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return None


def masked_reason(pattern_name: str, rel: str) -> str:
    return f"{rel}: 命中 {pattern_name}，内容已脱敏"


def check_file(rel: str) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    path = ROOT / rel
    normalized = rel.replace(os.sep, "/")
    if normalized.startswith(SKIP_PREFIXES):
        return errors, warnings

    if any(pattern.search(normalized) for pattern in REAL_ENV_PATTERNS) and not normalized.endswith(ALLOWED_ENV_EXAMPLES):
        errors.append(f"{rel}: 真实 env 文件不得进入 staged/tracked")

    if any(pattern.search(normalized) for pattern in RUNTIME_PATTERNS):
        errors.append(f"{rel}: 运行时数据或数据库文件不得进入 Git")

    is_binary, size = is_binary_or_large(path)
    if size > MAX_FILE_BYTES:
        warnings.append(f"{rel}: 文件超过 10MB，需确认是否为必要治理资产")
    if is_binary:
        return errors, warnings

    text = read_text(path)
    if text is None:
        return errors, warnings

    if normalized.endswith(ALLOWED_ENV_EXAMPLES):
        return errors, warnings

    for pattern in SECRET_PATTERNS:
        if pattern.search(text):
            errors.append(masked_reason("疑似密钥/Token/连接串", rel))
            break

    for pattern in LOCAL_PATH_PATTERNS:
        if pattern.search(text):
            errors.append(masked_reason("本机绝对路径", rel))
            break

    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--all", action="store_true", help="扫描全部 tracked 文件")
    args = parser.parse_args()

    files = sorted(all_files() if args.all else tracked_and_staged_files())
    errors: list[str] = []
    warnings: list[str] = []
    for rel in files:
        path = ROOT / rel
        if not path.is_file():
            continue
        file_errors, file_warnings = check_file(rel)
        errors.extend(file_errors)
        warnings.extend(file_warnings)

    print(f"Git 安全扫描摘要：扫描 {len(files)} 个 staged/tracked 文件。")
    if errors:
        print("阻断项：")
        for item in errors:
            print(f"- {item}")
    else:
        print("阻断项：无")
    if warnings:
        print("Warning：")
        for item in warnings:
            print(f"- {item}")
    else:
        print("Warning：无")

    if errors:
        print("修复建议：移除真实 env、运行时数据、密钥、本机路径或改为脱敏示例后重试。")
        return 1
    print("通过摘要：未发现需要阻断的 Git 安全风险。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
