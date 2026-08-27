#!/usr/bin/env python3
"""Validate lightweight documentation governance rules."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

FRONTMATTER_REQUIRED_GLOBS = (
    "AGENTS.md",
    "rules/*.md",
    "docs/*.md",
    "docs/standards/*.md",
    "docs/spec-logs/*.md",
    "openspec/changes/*/*.md",
)

FRONTMATTER_EXEMPT = {
    "docs/spec-logs/CHANGELOG.md",
}

SCAFFOLD_TERMS = (
    "TBD - created by",
    "[通用]",
    "[个性化]",
    "[条件启用]",
)

LOCAL_PATH_PATTERNS = (
    re.compile(r"/Users/(?!<)[^/`\s]+/"),
    re.compile(r"/home/(?!<)[^/`\s]+/"),
    re.compile(r"/private/var/folders/"),
)

WORD_BUDGETS = {
    "AGENTS.md": 1800,
    "rules/agent-context-budget.md": 1200,
    "rules/document-governance.md": 900,
    "docs/README.md": 700,
}

REQUIRED_FRONTMATTER_KEYS = ("created_at", "updated_at")


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def iter_frontmatter_targets() -> list[Path]:
    paths: set[Path] = set()
    for glob in FRONTMATTER_REQUIRED_GLOBS:
        for path in ROOT.glob(glob):
            if path.is_file() and rel(path) not in FRONTMATTER_EXEMPT:
                paths.add(path)
    return sorted(paths)


def frontmatter_block(text: str) -> str | None:
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---\n", 4)
    if end == -1:
        return None
    return text[4:end]


def validate_frontmatter(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    block = frontmatter_block(text)
    if block is None:
        return [f"{rel(path)}: 缺少 YAML Frontmatter"]
    errors: list[str] = []
    for key in REQUIRED_FRONTMATTER_KEYS:
        if not re.search(rf"^{re.escape(key)}:\s*\S+", block, re.MULTILINE):
            errors.append(f"{rel(path)}: Frontmatter 缺少 `{key}`")
    return errors


def validate_scaffold_terms(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    errors: list[str] = []
    for lineno, line in enumerate(text.splitlines(), start=1):
        for term in SCAFFOLD_TERMS:
            if term in line:
                errors.append(f"{rel(path)}:{lineno}: 存在脚手架或占位标记 `{term}`")
                break
    return errors


def validate_spec_log_privacy() -> list[str]:
    errors: list[str] = []
    for path in ROOT.glob("docs/spec-logs/*.md"):
        if not path.is_file():
            continue
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            for pattern in LOCAL_PATH_PATTERNS:
                if pattern.search(line):
                    errors.append(f"{rel(path)}:{lineno}: spec-log 中存在未脱敏本机绝对路径")
                    break
    return errors


def count_words(text: str) -> int:
    chinese_chars = len(re.findall(r"[\u4e00-\u9fff]", text))
    latin_words = len(re.findall(r"[A-Za-z0-9_./:-]+", text))
    return chinese_chars + latin_words


def validate_word_budgets() -> list[str]:
    errors: list[str] = []
    for path_text, budget in WORD_BUDGETS.items():
        path = ROOT / path_text
        if not path.exists():
            continue
        count = count_words(path.read_text(encoding="utf-8"))
        if count > budget:
            errors.append(f"{path_text}: 文档预算超限 {count}/{budget}")
    return errors


def main() -> int:
    errors: list[str] = []
    targets = iter_frontmatter_targets()
    for path in targets:
        errors.extend(validate_frontmatter(path))
        errors.extend(validate_scaffold_terms(path))
    errors.extend(validate_spec_log_privacy())
    errors.extend(validate_word_budgets())

    if errors:
        print("文档治理校验失败：")
        for error in errors:
            print(f"- {error}")
        return 1

    print(
        "文档治理校验通过："
        f"{len(targets)} 个长期 Markdown 已检查 Frontmatter 和脚手架残留；"
        "spec logs 未发现未脱敏本机路径；AGENTS 与核心文档预算未超限。"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
