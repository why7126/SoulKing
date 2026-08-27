#!/usr/bin/env python3
"""Validate ProjectSoulKing static Web design-system baseline."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATIC_DIR = ROOT / "app" / "static"
REQUIRED = [
    ROOT / "ui-design.md",
    ROOT / "rules" / "ui-design.md",
    STATIC_DIR / "studio.css",
    STATIC_DIR / "admin-studio.css",
]
SCAN_EXTENSIONS = {".css", ".html", ".js"}
HEX_PATTERN = re.compile(r"#[0-9A-Fa-f]{3,8}\b")
CSS_VAR_PATTERN = re.compile(r"--[A-Za-z0-9_-]+\s*:")


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    for path in REQUIRED:
        if not path.exists():
            errors.append(f"缺少设计系统文件: {path.relative_to(ROOT)}")

    css_var_count = 0
    hex_hits = 0
    for path in STATIC_DIR.rglob("*") if STATIC_DIR.exists() else []:
        if path.suffix not in SCAN_EXTENSIONS or not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        css_var_count += len(CSS_VAR_PATTERN.findall(text))
        if path.suffix == ".css" and path.name not in {"studio.css", "admin-studio.css", "styles.css", "login.css"}:
            hits = len(HEX_PATTERN.findall(text))
            if hits:
                hex_hits += hits
                warnings.append(f"{path.relative_to(ROOT)} 存在 {hits} 个 Hex 颜色，请确认是否应沉淀为 token")

    if css_var_count == 0:
        errors.append("app/static 未发现 CSS custom properties，设计 token 可能未落地")

    if errors:
        print("Design System 校验失败：")
        for error in errors:
            print(f"  - {error}")
        for warning in warnings:
            print(f"  - warning: {warning}")
        return 1

    print(f"Design System 校验通过。CSS token 数量: {css_var_count}; 非核心 CSS Hex warning: {hex_hits}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
