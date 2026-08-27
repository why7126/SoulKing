from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import sprint_close_stale_scan


def test_scan_line_blocks_archived_active_change_path() -> None:
    hits = sprint_close_stale_scan.scan_line(
        line="参考 openspec/changes/update-governance/tasks.md",
        line_no=7,
        file_path=ROOT / "iterations" / "change" / "sprint-001" / "sprint.md",
        root=ROOT,
        sprint=SimpleNamespace(sprint_id="sprint-001", requirements=[], bugs=[]),
        issues={},
        derived_issues={},
        derived_changes={
            "update-governance": SimpleNamespace(state="archived"),
        },
    )

    assert [hit.kind for hit in hits] == ["stale-change-active-path"]


def test_scan_line_blocks_archived_change_waiting_acceptance() -> None:
    hits = sprint_close_stale_scan.scan_line(
        line="update-governance 待验收后关闭。",
        line_no=9,
        file_path=ROOT / "iterations" / "change" / "sprint-001" / "acceptance-report.md",
        root=ROOT,
        sprint=SimpleNamespace(sprint_id="sprint-001", requirements=[], bugs=[]),
        issues={},
        derived_issues={},
        derived_changes={
            "update-governance": SimpleNamespace(state="archived"),
        },
    )

    assert [hit.kind for hit in hits] == ["stale-change-apply"]
