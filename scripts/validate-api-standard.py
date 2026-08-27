#!/usr/bin/env python3
"""Validate ProjectSoulKing API governance baseline."""

from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP_DIR = ROOT / "app"
API_FILES = [
    APP_DIR / "main.py",
    APP_DIR / "auth_routes.py",
]
REQUIRED_DOCS = [
    ROOT / "docs" / "03-api-index.md",
    ROOT / "docs" / "standards" / "api-governance.md",
]
ROUTE_DECORATOR = re.compile(r"@(app|router)\.(get|post|put|patch|delete)\(")


def source_for(path: Path, node: ast.AST, text: str) -> str:
    return ast.get_source_segment(text, node) or ""


def check_routes(path: Path, errors: list[str]) -> None:
    if not path.exists():
        errors.append(f"缺少 API 文件: {path.relative_to(ROOT)}")
        return
    text = path.read_text(encoding="utf-8")
    try:
        tree = ast.parse(text)
    except SyntaxError as exc:
        errors.append(f"{path.relative_to(ROOT)} 语法错误: {exc}")
        return

    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        decorators = "\n".join(source_for(path, dec, text) for dec in node.decorator_list)
        if not ROUTE_DECORATOR.search(decorators):
            continue
        rel = path.relative_to(ROOT)
        if "summary=" not in decorators:
            errors.append(f"{rel}:{node.lineno} 路由 {node.name} 缺少 summary")
        if "response_model" not in decorators and "response_model" not in source_for(path, node, text):
            errors.append(f"{rel}:{node.lineno} 路由 {node.name} 缺少 response_model 或显式响应契约说明")


def main() -> int:
    errors: list[str] = []
    for doc in REQUIRED_DOCS:
        if not doc.exists():
            errors.append(f"缺少治理文档: {doc.relative_to(ROOT)}")
    for path in API_FILES:
        check_routes(path, errors)

    if errors:
        print("API 标准校验失败：")
        for error in errors:
            print(f"  - {error}")
        return 1
    print("API 标准校验通过。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
