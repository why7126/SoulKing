from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from workflow_sync.collect import IssueRecord  # noqa: E402
from workflow_sync.derive import DerivedIssue  # noqa: E402
from workflow_sync import patch  # noqa: E402


def test_patch_issue_trace_writes_iteration_from_resolved_sprint(tmp_path: Path, monkeypatch) -> None:
    issue_dir = tmp_path / "issues/requirements/review/REQ-9018-example"
    issue_dir.mkdir(parents=True)
    trace_path = issue_dir / "trace.md"
    trace_path.write_text(
        "\n".join(
            [
                "---",
                "requirement_id: REQ-9018-example",
                "status: in_sprint",
                "openspec_changes:",
                "  - change_id: update-example",
                "    type: update",
                "    status: proposed",
                "---",
                "",
                "# Trace",
                "",
                "## 当前状态",
                "- 状态：in_sprint",
                "- 阶段：review",
                "",
                "## 关联 OpenSpec",
                "- `update-example`（proposed，update）",
                "",
                "## 变更记录",
                "",
                "| 时间 | 命令 | 说明 |",
                "|---|---|---|",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(patch, "ROOT", tmp_path)

    result = patch.patch_issue_trace(
        IssueRecord(
            issue_id="REQ-9018-example",
            kind="req",
            path=issue_dir,
            trace_status="in_sprint",
            openspec_changes=[{"change_id": "update-example", "status": "proposed"}],
        ),
        DerivedIssue(
            issue_id="REQ-9018-example",
            kind="req",
            display_status="in_sprint",
            linked_change="update-example",
            note="apply 完成；待 archive `update-example`",
        ),
        {"update-example": "applied"},
        event="opsx.apply",
        focus_change="update-example",
        sprint_id="sprint-002",
    )

    text = trace_path.read_text(encoding="utf-8")
    assert result.changed is True
    assert "iteration: sprint-002" in text
    assert "    status: applied" in text
    assert "- `update-example`（applied）" in text
    assert "/opsx-apply" in text
