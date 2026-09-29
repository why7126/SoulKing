from __future__ import annotations

import json
import subprocess
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


def test_manual_map_merges_fields_and_marks_post_command_target() -> None:
    records = [
        {
            "turn_hash": "turn-a",
            "source_session_hash": "session-a",
            "workflow_event": "unknown",
            "requirements": ["REQ-9018-first"],
            "bugs": [],
            "changes": [],
            "release_sprints": [],
            "attribution_confidence": "low",
        },
        {
            "turn_hash": "turn-b",
            "source_session_hash": "session-a",
            "workflow_event": "unknown",
            "requirements": [],
            "bugs": [],
            "changes": [],
            "release_sprints": [],
            "attribution_confidence": "low",
        },
    ]

    mapped = ai_usage.apply_manual_mapping(
        records,
        {
            "turn-a": {
                "requirements": ["REQ-9019-second"],
                "bugs": ["BUG-9018-third"],
                "changes": ["update-ai-usage"],
                "sprint_id": "sprint-002",
                "workflow_event": "req.opsx",
                "release_sprints": ["sprint-001"],
                "release_version": "v1.2.3",
                "post_command_target": True,
                "attribution_confidence": "reviewed",
            },
            "session-a": {
                "changes": ["session-wide-change"],
                "workflow_event": "sprint.archive",
            },
        },
    )

    assert mapped[0]["requirements"] == ["REQ-9018-first", "REQ-9019-second"]
    assert mapped[0]["bugs"] == ["BUG-9018-third"]
    assert mapped[0]["changes"] == ["update-ai-usage"]
    assert mapped[0]["sprint_id"] == "sprint-002"
    assert mapped[0]["workflow_event"] == "req.opsx"
    assert mapped[0]["release_sprints"] == ["sprint-001"]
    assert mapped[0]["release_version"] == "v1.2.3"
    assert mapped[0]["_post_command_target"] is True
    assert mapped[0]["attribution_confidence"] == "reviewed"
    assert mapped[1]["changes"] == ["session-wide-change"]
    assert mapped[1]["attribution_confidence"] == "medium"


def test_post_command_hook_uses_manual_map_to_refresh_sprint_snapshot(tmp_path: Path) -> None:
    session_path = tmp_path / "session.jsonl"
    rows = [
        {"type": "user_message", "timestamp": "2026-08-31T01:00:00Z", "text": "work with sparse attribution"},
        {
            "type": "token_count",
            "timestamp": "2026-08-31T01:00:01Z",
            "payload": {"last_token_usage": {"input_tokens": 7, "output_tokens": 5, "total_tokens": 12}},
        },
    ]
    raw = "\n".join(json.dumps(row) for row in rows).encode("utf-8") + b"\n"
    session_path.write_bytes(raw)
    session_hash = ai_usage.session_source_hash(session_path, raw)

    payload = ai_usage.post_command_hook(
        session_jsonl=session_path,
        out_dir=tmp_path / "ai-usage",
        workflow_event="opsx.apply",
        changes=["update-ai-usage-manual-map-refresh"],
        sprint_id="sprint-002",
        manual_map={
            session_hash: {
                "requirements": ["REQ-0018-ai-usage-manual-map-refresh"],
                "changes": ["update-ai-usage-manual-map-refresh"],
                "sprint_id": "sprint-002",
                "workflow_event": "opsx.apply",
                "post_command_target": True,
                "attribution_confidence": "manual",
            }
        },
    )

    assert payload["status"] == "ok"
    assert payload["usage_mode"] == "actual"
    assert payload["command_run_count"] == 1
    assert payload["sprint_snapshot"]["status"] == "refreshed"
    snapshot = json.loads((tmp_path / "ai-usage/sprints/sprint-002.json").read_text(encoding="utf-8"))
    assert snapshot["totals"]["total_tokens"] == 12
    assert snapshot["coverage"]["requirements"] == ["REQ-0018-ai-usage-manual-map-refresh"]
    assert snapshot["coverage"]["changes"] == ["update-ai-usage-manual-map-refresh"]
    assert session_path.read_text(encoding="utf-8") not in json.dumps(snapshot, ensure_ascii=False)


def test_extract_ai_usage_cli_refreshes_sprint_snapshot_with_manual_map(tmp_path: Path) -> None:
    session_path = tmp_path / "session.jsonl"
    rows = [
        {"type": "user_message", "timestamp": "2026-08-31T01:00:00Z", "text": "sparse command"},
        {
            "type": "token_count",
            "timestamp": "2026-08-31T01:00:01Z",
            "payload": {"last_token_usage": {"input_tokens": 11, "output_tokens": 13, "total_tokens": 24}},
        },
    ]
    raw = "\n".join(json.dumps(row) for row in rows).encode("utf-8") + b"\n"
    session_path.write_bytes(raw)
    manual_path = tmp_path / "manual-map.json"
    manual_path.write_text(
        json.dumps(
            {
                ai_usage.session_source_hash(session_path, raw): {
                    "requirements": ["REQ-0018-ai-usage-manual-map-refresh"],
                    "changes": ["update-ai-usage-manual-map-refresh"],
                    "sprint_id": "sprint-002",
                    "workflow_event": "opsx.apply",
                    "post_command_target": True,
                    "attribution_confidence": "manual",
                }
            }
        ),
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPTS / "extract-ai-usage.py"),
            "--session-jsonl",
            str(session_path),
            "--manual-map",
            str(manual_path),
            "--sprint",
            "sprint-002",
            "--out-dir",
            str(tmp_path / "ai-usage"),
            "--json",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )

    payload = json.loads(result.stdout)
    snapshot = json.loads((tmp_path / "ai-usage/sprints/sprint-002.json").read_text(encoding="utf-8"))
    assert payload["command_run_count"] == 1
    assert snapshot["totals"]["total_tokens"] == 24
    assert snapshot["by_workflow_event"]["opsx.apply"]["command_run_count"] == 1
