from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from . import collect
from .derive import DerivedIssue
from .timefmt import now_shanghai, touch_frontmatter

CLOSED_STATUSES = frozenset({"done", "archived", "resolved", "closed", "completed"})
BLOCKING_STATUSES = frozenset(
    {
        "captured",
        "exploring",
        "draft",
        "enriching",
        "pending_review",
        "approved",
        "in_sprint",
        "applied",
        "proposed",
        "todo",
        "open",
    }
)

REQ_PRIMARY_DOC = "requirement.md"
BUG_PRIMARY_DOC = "bug.md"
ACCEPTANCE_DOC = "acceptance.md"


@dataclass(frozen=True)
class SubdocumentFinding:
    issue_id: str
    file: Path
    source: str
    current: str | None
    target: str | None
    classification: str
    safe_to_sync: bool
    reason: str


@dataclass
class SubdocumentSyncResult:
    issue_id: str
    checked_files: int = 0
    updated_files: int = 0
    updated_fields: int = 0
    acceptance_status: str = "n/a"
    findings: list[SubdocumentFinding] = field(default_factory=list)

    @property
    def warnings(self) -> list[SubdocumentFinding]:
        return [item for item in self.findings if item.classification == "needs_manual_review"]

    @property
    def blockers(self) -> list[SubdocumentFinding]:
        return [item for item in self.findings if item.classification in {"blocker", "missing_acceptance_result"}]


def status_value(value: object) -> str | None:
    status = str(value).strip() if value is not None else ""
    return status or None


def is_closed_status(status: str | None) -> bool:
    return (status or "").strip().lower() in CLOSED_STATUSES


def is_blocking_status(status: str | None) -> bool:
    normalized = (status or "").strip().lower()
    return normalized in BLOCKING_STATUSES


def iter_yaml_blocks(text: str) -> list[tuple[re.Match[str], dict[str, object]]]:
    blocks: list[tuple[re.Match[str], dict[str, object]]] = []
    for match in re.finditer(r"```yaml\n(.*?)```", text, re.DOTALL):
        blocks.append((match, collect.parse_simple_yaml(match.group(1))))
    return blocks


def replace_mapping_value(text: str, key: str, value: str) -> tuple[str, bool]:
    pattern = re.compile(rf"^(\s*{re.escape(key)}\s*:\s*).*$", re.MULTILINE)
    new_text, count = pattern.subn(rf"\g<1>{value}", text, count=1)
    return new_text, bool(count)


def replace_frontmatter_key(text: str, key: str, value: str) -> tuple[str, bool]:
    if not text.startswith("---"):
        return text, False
    match = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    if not match:
        return text, False
    fm_text = match.group(1)
    new_fm, changed = replace_mapping_value(fm_text, key, value)
    if changed:
        return f"---\n{new_fm}\n---{text[match.end():]}", True
    insert = fm_text.rstrip() + f"\n{key}: {value}\n"
    return f"---\n{insert}---{text[match.end():]}", True


def rename_frontmatter_key(text: str, old_key: str, new_key: str) -> tuple[str, bool]:
    if not text.startswith("---"):
        return text, False
    match = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    if not match:
        return text, False
    fm_text = match.group(1)
    pattern = re.compile(rf"^(\s*){re.escape(old_key)}(\s*:\s*)", re.MULTILINE)
    new_fm, count = pattern.subn(rf"\1{new_key}\2", fm_text, count=1)
    if not count:
        return text, False
    return f"---\n{new_fm}\n---{text[match.end():]}", True


def primary_doc_name(issue: collect.IssueRecord) -> str:
    return REQ_PRIMARY_DOC if issue.kind == "req" else BUG_PRIMARY_DOC


def acceptance_status_for(derived: DerivedIssue, event: str | None) -> str:
    if derived.display_status in CLOSED_STATUSES or event in {"opsx.archive", "sprint.archive"}:
        return "passed"
    if event in {"opsx.apply", "opsx.modify"}:
        return "pending"
    if derived.display_status == "in_sprint":
        return "not_started"
    return "not_started"


def source_sprint_for(issue: collect.IssueRecord) -> str | None:
    trace = issue.path / "trace.md"
    if not trace.exists():
        return None
    text = collect.read_text(trace)
    fm = collect.parse_frontmatter_yaml(text)
    value = fm.get("iteration")
    if isinstance(value, str) and value.strip() and value.strip() != "null":
        return value.strip()
    block = collect.parse_yaml_block(text) or {}
    value = block.get("iteration")
    if isinstance(value, str) and value.strip() and value.strip() != "null":
        return value.strip()
    return None


def render_acceptance_block(
    *,
    status: str,
    source_change: str | None,
    source_sprint: str | None,
    event: str | None,
) -> str:
    accepted_at = now_shanghai() if status in {"passed", "failed", "partial", "waived"} else "null"
    accepted_by = "workflow-sync" if accepted_at != "null" else "null"
    notes = "待验收；由 opsx.apply 标记，后续 archive 时回填结论。" if status == "pending" else "由 Workflow Sync 根据 Change/Sprint 状态回填。"
    return "\n".join(
        [
            "## 验收结果回填",
            "",
            "```yaml",
            f"acceptance_status: {status}",
            f"accepted_at: {accepted_at}",
            f"accepted_by: {accepted_by}",
            f"source_change: {source_change or 'null'}",
            f"source_sprint: {source_sprint or 'null'}",
            "evidence: []",
            "failed_items: []",
            f"source_event: {event or 'workflow-sync'}",
            f"notes: {notes}",
            "```",
            "",
        ]
    )


def upsert_acceptance_block(
    text: str,
    *,
    status: str,
    source_change: str | None,
    source_sprint: str | None,
    event: str | None,
) -> tuple[str, bool]:
    block = render_acceptance_block(
        status=status,
        source_change=source_change,
        source_sprint=source_sprint,
        event=event,
    ).rstrip()
    pattern = re.compile(r"^## 验收结果回填\s*\n.*?(?=^## |\Z)", re.MULTILINE | re.DOTALL)
    if pattern.search(text):
        new_text = pattern.sub(block + "\n\n", text, count=1)
        return new_text, new_text != text
    suffix = "" if text.endswith("\n") else "\n"
    return f"{text}{suffix}\n{block}\n", True


def classify_status_field(
    *,
    issue: collect.IssueRecord,
    path: Path,
    source: str,
    status: str | None,
    target: str,
) -> SubdocumentFinding | None:
    if not status:
        return None
    name = path.name
    if name in {"trace.md", "capture.md"}:
        return None
    if name == primary_doc_name(issue):
        if status == target:
            return None
        return SubdocumentFinding(issue.issue_id, path, source, status, target, "safe_sync", True, "primary document mirrors trace status")
    if name == ACCEPTANCE_DOC:
        if source == "frontmatter.status":
            return SubdocumentFinding(issue.issue_id, path, source, status, "acceptance_status", "safe_rename", True, "acceptance.md status is acceptance semantics")
        return None
    if name == "review.md":
        return SubdocumentFinding(issue.issue_id, path, source, status, None, "needs_manual_review", False, "review status may be review_result, not current issue status")
    if is_blocking_status(status) and is_closed_status(target):
        return SubdocumentFinding(issue.issue_id, path, source, status, target, "residual_safe_sync", True, "closed issue residual status")
    return SubdocumentFinding(issue.issue_id, path, source, status, None, "needs_manual_review", False, "status field semantics are not declared")


def scan_issue_subdocuments(
    issue: collect.IssueRecord,
    derived: DerivedIssue | None = None,
) -> tuple[list[SubdocumentFinding], int]:
    target = derived.display_status if derived else (issue.trace_status or "done")
    findings: list[SubdocumentFinding] = []
    checked = 0
    if not issue.path.is_dir():
        return findings, checked
    for path in sorted(issue.path.glob("*.md")):
        checked += 1
        text = collect.read_text(path)
        fm = collect.parse_frontmatter(text)
        finding = classify_status_field(
            issue=issue,
            path=path,
            source="frontmatter.status",
            status=status_value(fm.get("status")),
            target=target,
        )
        if finding:
            findings.append(finding)
        if path.name == ACCEPTANCE_DOC and is_closed_status(target):
            fm_yaml = collect.parse_frontmatter_yaml(text)
            has_acceptance_status = bool(fm_yaml.get("acceptance_status")) or "acceptance_status:" in text
            if not has_acceptance_status:
                findings.append(
                    SubdocumentFinding(
                        issue.issue_id,
                        path,
                        "acceptance_result",
                        None,
                        "acceptance_status",
                        "missing_acceptance_result",
                        True,
                        "closed issue requires acceptance result",
                    )
                )
        for _, block in iter_yaml_blocks(text):
            finding = classify_status_field(
                issue=issue,
                path=path,
                source="yaml_block.status",
                status=status_value(block.get("status")),
                target=target,
            )
            if finding:
                findings.append(finding)
    return findings, checked


def sync_issue_subdocuments(
    issue: collect.IssueRecord,
    derived: DerivedIssue,
    *,
    event: str | None,
    source_change: str | None,
    write: bool,
) -> SubdocumentSyncResult:
    findings, checked = scan_issue_subdocuments(issue, derived)
    result = SubdocumentSyncResult(issue_id=issue.issue_id, checked_files=checked, findings=findings)
    changed_files: set[Path] = set()
    target_status = derived.display_status

    for path in sorted(issue.path.glob("*.md")):
        text = collect.read_text(path)
        original = text
        if path.name == primary_doc_name(issue):
            text, _ = replace_frontmatter_key(text, "status", target_status)
        elif path.name == ACCEPTANCE_DOC:
            acceptance_status = acceptance_status_for(derived, event)
            result.acceptance_status = acceptance_status
            text, _ = rename_frontmatter_key(text, "status", "acceptance_status")
            text, _ = replace_frontmatter_key(text, "acceptance_status", acceptance_status)
            text, _ = upsert_acceptance_block(
                text,
                status=acceptance_status,
                source_change=source_change or derived.linked_change,
                source_sprint=source_sprint_for(issue),
                event=event,
            )
        if text != original:
            result.updated_fields += 1
            changed_files.add(path)
            if write:
                text, _ = touch_frontmatter(text, bump_updated=True)
                path.write_text(text, encoding="utf-8")

    result.updated_files = len(changed_files)
    if result.acceptance_status == "n/a" and not (issue.path / ACCEPTANCE_DOC).exists():
        result.acceptance_status = "missing"
    return result


def safe_reconcile_findings(issue: collect.IssueRecord) -> list[SubdocumentFinding]:
    findings, _ = scan_issue_subdocuments(issue)
    return [item for item in findings if item.safe_to_sync]
