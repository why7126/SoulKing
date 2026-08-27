#!/usr/bin/env python3
"""Validate ProjectSoulKing test-governance baseline."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED_DIRS = [
    ROOT / "tests",
    ROOT / "tests" / "unit",
    ROOT / "tests" / "integration",
    ROOT / "tests" / "integration" / "api",
    ROOT / "tests" / "e2e",
    ROOT / "tests" / "compatibility",
]
REQUIRED_DOCS = [
    ROOT / "rules" / "testing.md",
    ROOT / "docs" / "standards" / "testing-governance.md",
    ROOT / "openspec" / "testing-mapping.md",
]


def has_tests(path: Path) -> bool:
    return path.exists() and any(path.rglob("test_*.py"))


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    for path in REQUIRED_DIRS:
        if not path.is_dir():
            errors.append(f"缺少测试目录: {path.relative_to(ROOT)}")
    for path in REQUIRED_DOCS:
        if not path.exists():
            errors.append(f"缺少测试治理文档: {path.relative_to(ROOT)}")

    if not has_tests(ROOT / "tests"):
        warnings.append("tests/ 下暂无 test_*.py；当前只校验治理骨架，后续功能变更应补单元/集成测试")
    if not (ROOT / "package.json").exists():
        warnings.append("缺少 package.json，E2E 命令需另行确认")

    if errors:
        print("测试框架校验失败：")
        for error in errors:
            print(f"  - {error}")
        for warning in warnings:
            print(f"  - warning: {warning}")
        return 1

    print("测试框架校验通过。")
    for warning in warnings:
        print(f"  - warning: {warning}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
