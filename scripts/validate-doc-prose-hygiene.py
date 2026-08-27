#!/usr/bin/env python3
"""Heuristic scan for long-lived documentation prose hygiene issues."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TARGETS = [
    ROOT / "AGENTS.md",
    ROOT / "rules",
    ROOT / "docs",
    ROOT / ".agents" / "skills",
]
EXCLUDED_PARTS = {
    ".git",
    "node_modules",
    "dist",
    "coverage",
    "archive",
    "releases",
}
EXCLUDED_DOC_PARTS = {
    "spec-logs",
}
PATTERNS = [
    ("session-reasoning", re.compile(r"(我先|我会先|本轮|这次改动|本次新增|执行过程中|先.*然后)")),
    ("review-dialogue", re.compile(r"(reviewer|review 要求|按评论|评审意见|已按.*修改)", re.IGNORECASE)),
    ("draft-reference", re.compile(r"(草案|设计稿第|audit [A-Z]\d|decision \d+|第\s*\d+\s*版)")),
    ("history-narration", re.compile(r"(之前|现在|不再|原来|旧版|这次|本次)", re.IGNORECASE)),
    ("local-path", re.compile(r"(/Users/[^`\s)]+|/home/[^`\s)]+|[A-Za-z]:\\\\[^`\s)]+)")),
]


@dataclass
class Finding:
    kind: str
    path: str
    line: int
    text: str


def should_skip(path: Path) -> bool:
    parts = set(path.relative_to(ROOT).parts)
    if parts & EXCLUDED_PARTS:
        return True
    return "docs" in parts and bool(parts & EXCLUDED_DOC_PARTS)


def iter_markdown(targets: list[Path]) -> list[Path]:
    files: list[Path] = []
    for target in targets:
        path = target if target.is_absolute() else ROOT / target
        if not path.exists():
            continue
        if path.is_file() and path.suffix == ".md" and not should_skip(path):
            files.append(path)
        elif path.is_dir():
            for item in path.rglob("*.md"):
                if not should_skip(item):
                    files.append(item)
    return sorted(set(files))


def scan_file(path: Path) -> list[Finding]:
    findings: list[Finding] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except UnicodeDecodeError:
        return findings
    in_code = False
    rel = str(path.relative_to(ROOT))
    for index, line in enumerate(lines, start=1):
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code = not in_code
            continue
        if in_code or not stripped:
            continue
        for kind, pattern in PATTERNS:
            if pattern.search(line):
                findings.append(Finding(kind, rel, index, stripped[:180]))
    return findings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="*")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    targets = [ROOT / value for value in args.paths] if args.paths else DEFAULT_TARGETS
    findings: list[Finding] = []
    for path in iter_markdown(targets):
        findings.extend(scan_file(path))

    payload = {
        "status": "passed" if not findings else "warning",
        "finding_count": len(findings),
        "findings": [item.__dict__ for item in findings],
    }
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(f"doc prose hygiene: {payload['status']} findings={len(findings)}")
        for item in findings[:80]:
            print(f"- {item.kind}: {item.path}:{item.line} - {item.text}")
        if len(findings) > 80:
            print(f"- ... {len(findings) - 80} more finding(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
