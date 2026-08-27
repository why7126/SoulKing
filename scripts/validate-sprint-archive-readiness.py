#!/usr/bin/env python3
"""Validate that a Sprint is ready to be archived.

The gate is intentionally separate from workflow sync: `/sprint-archive` needs
a command that can fail before any OpenSpec archive or Sprint close mutation.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import sprint_change_batches


ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class TaskCounts:
    done: int
    total: int
    missing: bool = False

    @property
    def incomplete(self) -> int:
        if self.missing:
            return 1
        return max(self.total - self.done, 0)

    @property
    def label(self) -> str:
        return "missing" if self.missing else f"{self.done}/{self.total}"


@dataclass(frozen=True)
class ChangeReadiness:
    change_id: str
    location: str
    path: str | None
    tasks: TaskCounts
    trace_exists: bool | None = None
    fallback_summary_status: str = "n/a"
    fallback_summary_file: str | None = None
    fallback_summary_missing: list[str] | None = None
    blocker: str | None = None


@dataclass(frozen=True)
class SprintReadiness:
    sprint_id: str
    sprint_path: str
    changes: list[ChangeReadiness]
    change_batches: dict[str, object]

    @property
    def blockers(self) -> list[ChangeReadiness]:
        return [change for change in self.changes if change.blocker]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def resolve_sprint_dir(root: Path, sprint_id: str) -> Path | None:
    iterations = root / "iterations"
    for stage in ("change", "archive"):
        candidate = iterations / stage / sprint_id
        if (candidate / "sprint.yaml").exists():
            return candidate
    legacy = iterations / sprint_id
    if (legacy / "sprint.yaml").exists():
        return legacy
    return None


def parse_sprint_changes(sprint_yaml: Path) -> list[str]:
    text = read_text(sprint_yaml)
    changes: list[str] = []
    in_changes = False
    changes_indent = 0

    for line in text.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue

        indent = len(line) - len(line.lstrip(" "))
        stripped = line.strip()
        if re.match(r"^changes\s*:\s*$", stripped):
            in_changes = True
            changes_indent = indent
            continue

        if in_changes and indent <= changes_indent and not stripped.startswith("- "):
            break

        if not in_changes:
            continue

        match = re.match(r"^-\s*['\"]?([^'\"\s#]+)['\"]?", stripped)
        if match:
            changes.append(match.group(1))

    return changes


def find_archived_change_dir(root: Path, change_id: str) -> Path | None:
    for archive_root in (
        root / "openspec" / "archive",
        root / "openspec" / "changes" / "archive",
    ):
        if not archive_root.exists():
            continue
        matches = sorted(archive_root.glob(f"*-{change_id}"))
        if matches:
            return matches[-1]
    return None


def resolve_change_dir(root: Path, change_id: str) -> tuple[str, Path | None]:
    active = root / "openspec" / "changes" / change_id
    if active.exists():
        return "active", active
    archived = find_archived_change_dir(root, change_id)
    if archived:
        return "archived", archived
    return "missing", None


def count_tasks(tasks_path: Path | None) -> TaskCounts:
    if tasks_path is None or not tasks_path.exists():
        return TaskCounts(done=0, total=0, missing=True)
    text = read_text(tasks_path)
    done = len(re.findall(r"^- \[x\]", text, re.MULTILINE))
    total = len(re.findall(r"^- \[[ x]\]", text, re.MULTILINE))
    return TaskCounts(done=done, total=total, missing=False)


FALLBACK_SUMMARY_FILES = ("proposal.md", "design.md", "tasks.md")
FALLBACK_SUMMARY_REQUIREMENTS = {
    "validation": ("验证命令", "验证结果", "测试命令", "test", "pytest", "validate"),
    "acceptance": ("验收结论", "验收结果", "acceptance", "verdict"),
    "issue_or_sprint_status": ("Issue", "Sprint", "REQ-", "BUG-", "状态"),
    "archive_evidence": ("归档路径", "归档时间", "openspec/archive", "archive"),
}


def extract_archive_summary(text: str) -> str | None:
    match = re.search(r"^## 归档验证摘要\s*\n(.*?)(?=^##\s+|\Z)", text, re.MULTILINE | re.DOTALL)
    if not match:
        return None
    return match.group(1).strip()


def missing_fallback_summary_items(summary: str) -> list[str]:
    missing: list[str] = []
    lowered = summary.lower()
    for key, terms in FALLBACK_SUMMARY_REQUIREMENTS.items():
        if not any(term.lower() in lowered for term in terms):
            missing.append(key)
    return missing


def evaluate_fallback_summary(change_dir: Path, root: Path) -> tuple[str, str | None, list[str]]:
    checked: list[str] = []
    best_missing = list(FALLBACK_SUMMARY_REQUIREMENTS)
    for name in FALLBACK_SUMMARY_FILES:
        path = change_dir / name
        checked.append(str(path.relative_to(root)))
        if not path.exists():
            continue
        summary = extract_archive_summary(read_text(path))
        if summary is None:
            continue
        missing = missing_fallback_summary_items(summary)
        if not missing:
            return "pass", str(path.relative_to(root)), []
        if len(missing) < len(best_missing):
            best_missing = missing
    return "missing", None, best_missing or checked


def evaluate_sprint(root: Path, sprint_id: str, *, only_change: str | None = None) -> SprintReadiness:
    sprint_dir = resolve_sprint_dir(root, sprint_id)
    if sprint_dir is None:
        raise FileNotFoundError(f"sprint.yaml not found for {sprint_id}")

    change_ids = parse_sprint_changes(sprint_dir / "sprint.yaml")
    if only_change:
        if only_change not in change_ids:
            raise ValueError(f"change `{only_change}` is not listed in {sprint_id} sprint.yaml")
        change_ids = [only_change]

    records: list[ChangeReadiness] = []
    for change_id in change_ids:
        location, change_dir = resolve_change_dir(root, change_id)
        tasks = count_tasks(change_dir / "tasks.md" if change_dir else None)
        blocker = None
        trace_exists = None
        fallback_summary_status = "n/a"
        fallback_summary_file = None
        fallback_summary_missing: list[str] | None = None
        if location == "missing":
            blocker = "change directory missing"
        elif tasks.missing:
            blocker = "tasks.md missing"
        elif tasks.incomplete > 0:
            blocker = f"{tasks.incomplete} incomplete task(s)"
        elif location == "archived" and change_dir is not None:
            trace_exists = (change_dir / "trace.md").exists()
            if trace_exists:
                fallback_summary_status = "trace-present"
            else:
                fallback_summary_status, fallback_summary_file, fallback_summary_missing = evaluate_fallback_summary(
                    change_dir,
                    root,
                )
                if fallback_summary_status != "pass":
                    checked = ", ".join(
                        str((change_dir / name).relative_to(root)) for name in FALLBACK_SUMMARY_FILES
                    )
                    missing = ", ".join(fallback_summary_missing or list(FALLBACK_SUMMARY_REQUIREMENTS))
                    blocker = (
                        "archived change missing trace.md and complete fallback summary "
                        f"(checked: {checked}; missing: {missing})"
                    )

        records.append(
            ChangeReadiness(
                change_id=change_id,
                location=location,
                path=str(change_dir.relative_to(root)) if change_dir else None,
                tasks=tasks,
                trace_exists=trace_exists,
                fallback_summary_status=fallback_summary_status,
                fallback_summary_file=fallback_summary_file,
                fallback_summary_missing=fallback_summary_missing,
                blocker=blocker,
            )
        )

    change_batch_rows = [
        {
            "change_id": record.change_id,
            "tasks": {
                "done": record.tasks.done,
                "total": record.tasks.total,
            },
            "trace_exists": record.trace_exists,
            "blocker": record.blocker,
        }
        for record in records
    ]

    return SprintReadiness(
        sprint_id=sprint_id,
        sprint_path=str(sprint_dir.relative_to(root)),
        changes=records,
        change_batches=sprint_change_batches.build_change_batches(
            change_batch_rows,
            ordering="archive-readiness queue",
        ),
    )


def render_markdown(readiness: SprintReadiness, *, force: bool) -> str:
    lines = [
        "## Sprint Archive Readiness Report",
        "",
        f"**Sprint:** {readiness.sprint_id}",
        f"**Sprint Path:** `{readiness.sprint_path}`",
        f"**Mode:** {'force' if force else 'strict'}",
        "",
        "| Change | Location | Tasks | Archive Evidence | Result |",
        "|---|---|---:|---|---|",
    ]
    for change in readiness.changes:
        result = "PASS" if not change.blocker else f"BLOCKED: {change.blocker}"
        if change.location == "active":
            evidence = "active change; fallback not required"
        elif change.location == "archived" and change.trace_exists:
            evidence = "trace.md present"
        elif change.location == "archived" and change.fallback_summary_status == "pass":
            evidence = f"fallback summary pass: `{change.fallback_summary_file}`"
        elif change.location == "archived":
            missing = ", ".join(change.fallback_summary_missing or [])
            evidence = f"trace.md missing; fallback {change.fallback_summary_status}"
            if missing:
                evidence = f"{evidence}; missing {missing}"
        else:
            evidence = "n/a"
        lines.append(
            f"| `{change.change_id}` | {change.location} | {change.tasks.label} | {evidence} | {result} |"
        )

    batches = readiness.change_batches
    lines.extend(
        [
            "",
            "## Change Batches",
            "",
            f"- Applicable: {batches['applicable']} ({batches['reason']})",
            f"- Total Changes: {batches['total_changes']}",
            f"- Batch Count: {batches['batch_count']}",
            f"- Batch Size: {batches['batch_size']}",
        ]
    )
    if batches["batches"]:
        lines.extend(
            [
                "",
                "| Batch | Changes | Tasks | Blockers | Next Read |",
                "|---|---:|---:|---:|---|",
            ]
        )
        for batch in batches["batches"]:
            counts = batch["counts"]
            lines.append(
                f"| `{batch['batch_id']}` | {counts['changes']} | {counts['tasks_done']}/{counts['tasks_total']} | {counts['blockers']} | {batch['recommended_next_read']} |"
            )

    blockers = readiness.blockers
    lines.append("")
    if blockers and not force:
        lines.append("**Verdict:** BLOCKED")
        lines.append("")
        lines.append("Complete remaining `tasks.md` items via `/sprint-apply` before `/sprint-archive`.")
    elif blockers:
        lines.append("**Verdict:** FORCE-PROCEED")
        lines.append("")
        lines.append("Blocked items remain and require explicit reviewer confirmation.")
    else:
        lines.append("**Verdict:** PASS")

    return "\n".join(lines)


def readiness_to_json(readiness: SprintReadiness, *, force: bool) -> str:
    payload = asdict(readiness)
    payload["mode"] = "force" if force else "strict"
    payload["verdict"] = "blocked" if readiness.blockers and not force else "pass"
    return json.dumps(payload, ensure_ascii=False, indent=2)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sprint", required=True, help="Sprint id, e.g. sprint-004")
    parser.add_argument("--change", help="Validate one change listed in the Sprint")
    parser.add_argument("--root", type=Path, default=ROOT, help=argparse.SUPPRESS)
    parser.add_argument("--force", action="store_true", help="Report blockers but exit 0")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        readiness = evaluate_sprint(args.root.resolve(), args.sprint, only_change=args.change)
    except (FileNotFoundError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    if args.json:
        print(readiness_to_json(readiness, force=args.force))
    else:
        print(render_markdown(readiness, force=args.force))

    if readiness.blockers and not args.force:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
