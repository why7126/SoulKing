#!/usr/bin/env python3
"""Validate that sprint.md planning sections mirror sprint.yaml formal scope."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from workflow_sync.collect import load_sprint, read_text


def short_issue_code(issue_id: str) -> str:
    parts = issue_id.split("-", 2)
    if len(parts) >= 2 and parts[0] in {"REQ", "BUG"}:
        return f"{parts[0]}-{parts[1]}"
    return issue_id


def extract_scope_section(text: str) -> str | None:
    match = re.search(r"^## 2\. Scope\s*\n(.*?)(?=^## |\Z)", text, re.MULTILINE | re.DOTALL)
    return match.group(1) if match else None


def extract_goal_section(text: str) -> str | None:
    match = re.search(r"^## 1\.\s*(?:Sprint\s*)?目标\s*\n(.*?)(?=^## |\Z)", text, re.MULTILINE | re.DOTALL)
    return match.group(1) if match else None


def extract_target_id_list(text: str) -> set[str] | None:
    goal = extract_goal_section(text)
    if goal is None:
        return None

    lines = goal.splitlines()
    start_index: int | None = None
    for index, line in enumerate(lines):
        if "Sprint 目标编号列表" in line or line.strip() in {"正式目标：", "正式目标:"}:
            start_index = index + 1
            break
    if start_index is None:
        return None

    ids: set[str] = set()
    for line in lines[start_index:]:
        stripped = line.strip()
        if not stripped:
            if ids:
                break
            continue
        if stripped.startswith("#"):
            break
        bullet = re.match(r"^[-*]\s+(.+?)\s*$", stripped)
        if not bullet:
            if ids:
                break
            continue
        item = bullet.group(1).strip()
        match = re.search(r"`?((?:REQ|BUG)-\d{4}(?:-[A-Za-z0-9_-]+)?|[a-z0-9][a-z0-9_-]+)`?", item)
        if not match:
            continue
        item_id = match.group(1)
        ids.add(item_id)
        short = short_issue_code(item_id)
        if short != item_id:
            ids.add(short)
    return ids if ids else None


def extract_marker_block(text: str, name: str) -> str:
    pattern = re.compile(
        rf"<!-- workflow-sync:{re.escape(name)}:start -->(.*?)"
        rf"<!-- workflow-sync:{re.escape(name)}:end -->",
        re.DOTALL,
    )
    match = pattern.search(text)
    return match.group(1) if match else ""


def main_scope_table_header(scope: str) -> list[str] | None:
    for line in scope.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if "类型" in cells:
            return cells
    return None


def target_list_contains(target_ids: set[str] | None, item_id: str) -> bool:
    if target_ids is None:
        return False
    return item_id in target_ids or short_issue_code(item_id) in target_ids


def sprint_scope_linked_changes(sprint_path: Path) -> set[str]:
    yaml_path = sprint_path / "sprint.yaml"
    if not yaml_path.exists():
        return set()
    text = read_text(yaml_path)
    linked: set[str] = set()
    for block in re.finditer(r"(?ms)^  - id:\s+(.+?)(?=^  - id:|\Z)", text):
        item = block.group(0)
        if re.search(r"^\s+(?:requirement|bug):\s*\S+", item, re.MULTILINE):
            match = re.search(r"^\s+change:\s*(\S+)\s*$", item, re.MULTILINE)
            if match:
                linked.add(match.group(1).strip())
    return linked


def validate_sprint_scope(sprint_id: str, focus: set[str]) -> list[str]:
    sprint = load_sprint(sprint_id)
    if sprint is None:
        return [f"sprint `{sprint_id}` not found"]

    md_path = sprint.path / "sprint.md"
    if not md_path.exists():
        return [f"{md_path} not found"]

    text = read_text(md_path)
    scope = extract_scope_section(text)
    if scope is None:
        return [f"{md_path} missing `## 2. Scope` section"]

    main_scope = scope.split("<!-- workflow-sync:", 1)[0]
    req_block = extract_marker_block(text, "scope-requirements")
    bug_block = extract_marker_block(text, "scope-bugs")
    change_block = extract_marker_block(text, "scope-changes")
    target_ids = extract_target_id_list(text)
    linked_changes = sprint_scope_linked_changes(sprint.path)

    failures: list[str] = []
    expected_header = ["类型", "编号", "标题", "状态", "估算", "说明"]
    header = main_scope_table_header(main_scope)
    if header != expected_header:
        actual = "missing" if header is None else " | ".join(header)
        failures.append(
            "sprint.md `## 2. Scope` main table header must be "
            "`类型 | 编号 | 标题 | 状态 | 估算 | 说明`; "
            f"actual: `{actual}`"
        )

    def in_focus(item_id: str) -> bool:
        return not focus or item_id in focus or short_issue_code(item_id) in focus

    def append_target_failure(item_id: str) -> None:
        if target_ids is None:
            failures.append("sprint.md Sprint target id list missing or malformed")
        else:
            failures.append(f"{item_id} missing from sprint.md Sprint target id list")

    for req_id in sprint.requirements:
        if not in_focus(req_id):
            continue
        if req_id not in main_scope:
            failures.append(f"{req_id} missing from sprint.md `## 2. Scope` main table")
        if short_issue_code(req_id) not in req_block:
            failures.append(f"{req_id} missing from workflow-sync requirements table")
        if not target_list_contains(target_ids, req_id):
            append_target_failure(req_id)

    for bug_id in sprint.bugs:
        if not in_focus(bug_id):
            continue
        if bug_id not in main_scope:
            failures.append(f"{bug_id} missing from sprint.md `## 2. Scope` main table")
        if short_issue_code(bug_id) not in bug_block:
            failures.append(f"{bug_id} missing from workflow-sync bugs table")
        if not target_list_contains(target_ids, bug_id):
            append_target_failure(bug_id)

    for change_id in sprint.changes:
        if focus and change_id not in focus:
            continue
        if change_id not in main_scope:
            failures.append(f"{change_id} missing from sprint.md `## 2. Scope` main table")
        if change_id not in change_block:
            failures.append(f"{change_id} missing from workflow-sync changes table")
        if change_id not in linked_changes and not target_list_contains(target_ids, change_id):
            append_target_failure(change_id)

    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("sprint_id")
    parser.add_argument(
        "--item",
        action="append",
        default=[],
        help="Limit validation to an issue/change id; may be repeated.",
    )
    args = parser.parse_args()

    failures = validate_sprint_scope(args.sprint_id, set(args.item))
    if failures:
        print("## Sprint Scope Validation Failed")
        print()
        print(f"**Sprint:** {args.sprint_id}")
        print()
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("## Sprint Scope Validation")
    print()
    print(f"**Sprint:** {args.sprint_id}")
    if args.item:
        print(f"**Items:** {', '.join(args.item)}")
    print()
    print("Result: pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
