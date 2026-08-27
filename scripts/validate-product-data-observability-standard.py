#!/usr/bin/env python3
"""Validate the SoulKing product data collection and observability standard."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STANDARD = "docs/standards/product-data-collection-observability.md"

REQUIRED_FILES = [
    STANDARD,
    "docs/README.md",
    "docs/08-command-execution-order.md",
    "rules/api.md",
    "rules/database.md",
    "rules/testing.md",
    "rules/data-management.md",
]

REQUIRED_REFERENCES = {
    "docs/README.md": [STANDARD],
    "docs/08-command-execution-order.md": ["validate-product-data-observability-gates.py"],
    "rules/api.md": [STANDARD, "product_data_collection_observability"],
    "rules/database.md": [STANDARD, "product_data_collection_observability"],
    "rules/testing.md": [STANDARD, "product_data_collection_observability"],
    "rules/data-management.md": [STANDARD, "product_data_collection_observability"],
}

REQUIRED_STANDARD_TERMS = [
    "usage_events",
    "request_logs",
    "task_traces",
    "task_trace_spans",
    "behavior_trace_id",
    "behavior_event_id",
    "parent_behavior_event_id",
    "request_id",
    "client_request_id",
    "播放",
    "下载",
    "导入",
    "歌词",
    "歌单",
    "对象存储",
    "Task Trace 分级覆盖",
    "保留周期",
    "Authorization",
    "Cookie",
    "Token",
    "完整请求体",
    "完整响应体",
    "完整私有对象 key",
    "完整签名 URL",
    "本机绝对路径",
    "product_data_collection_observability",
]


def read_rel(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def main() -> int:
    errors: list[str] = []

    for item in REQUIRED_FILES:
        if not (ROOT / item).exists():
            errors.append(f"缺少必需文件: {item}")

    if (ROOT / STANDARD).exists():
        standard_text = read_rel(STANDARD)
        for term in REQUIRED_STANDARD_TERMS:
            if term not in standard_text:
                errors.append(f"{STANDARD} 缺少关键内容: {term}")

    for path, refs in REQUIRED_REFERENCES.items():
        if not (ROOT / path).exists():
            continue
        text = read_rel(path)
        for ref in refs:
            if ref not in text and Path(ref).name not in text:
                errors.append(f"{path} 缺少引用: {ref}")

    if errors:
        print("产品数据采集与链路观测标准校验失败：")
        for error in errors:
            print(f"  - {error}")
        return 1

    print("产品数据采集与链路观测标准校验通过。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
