from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import ai_usage  # noqa: E402


def test_sprint_usage_matrix_marks_unknown_columns() -> None:
    rows = [
        {
            "workflow_event": "opsx.apply",
            "requirements": ["REQ-0001-audio-import"],
            "bugs": [],
            "changes": ["add-audio-import"],
            "total_tokens": 10,
            "input_tokens": 7,
            "output_tokens": 3,
            "model_call_count": 1,
        }
    ]
    matrix = ai_usage.build_sprint_usage_matrices(
        rows,
        "sprint-001",
        scope={"requirements": ["REQ-0001-audio-import"], "bugs": [], "changes": ["add-audio-import"]},
    )

    columns = {column["label"]: column for column in matrix["columns"]}
    assert columns["Opsx-Apply"]["status"] == "observed"
    assert columns["Sprint-Archive"]["status"] == "unknown"
    assert columns["Opsx-Apply"]["command_run_count"] == 1


def test_trim_rows_to_sprint_scope_removes_related_history_rows() -> None:
    rows = [
        {
            "requirements": ["REQ-0001-audio-import", "REQ-9999-related-history"],
            "bugs": ["BUG-9999-related-history"],
            "changes": ["add-audio-import", "fix-related-history"],
        }
    ]

    trimmed = ai_usage.trim_rows_to_sprint_scope(
        rows,
        scope={"requirements": ["REQ-0001-audio-import"], "bugs": [], "changes": ["add-audio-import"]},
    )

    assert trimmed[0]["requirements"] == ["REQ-0001-audio-import"]
    assert trimmed[0]["bugs"] == []
    assert trimmed[0]["changes"] == ["add-audio-import"]
