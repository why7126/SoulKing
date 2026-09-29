from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))


def load_module():
    spec = importlib.util.spec_from_file_location("generate_sprint_fact_sheet", SCRIPTS / "generate-sprint-fact-sheet.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_render_usage_matrix_table_renders_unknown_as_dash() -> None:
    generate_sprint_fact_sheet = load_module()
    usage_matrices = {
        "columns": [
            {"label": "Opsx-Apply", "status": "observed"},
            {"label": "Sprint-Archive", "status": "unknown"},
        ],
        "rows": [
            {
                "object_id": "Total",
                "metrics": {"total_tokens": {"Opsx-Apply": 12, "Sprint-Archive": 0}},
            }
        ],
    }

    lines = generate_sprint_fact_sheet.render_usage_matrix_table(usage_matrices, "total_tokens")

    assert "| Total | 12 | - |" in lines


def test_ai_usage_matrix_gate_requires_present_actual_fresh_matrix() -> None:
    generate_sprint_fact_sheet = load_module()
    gate = generate_sprint_fact_sheet.ai_usage_matrix_gate(
        {
            "fresh_gate": {"status": "pass"},
            "snapshot_status": "present",
            "ai_usage_mode": "actual",
            "usage_matrices": {
                "columns": [{"label": "Opsx-Apply", "status": "observed"}],
                "rows": [{"object_id": "Total", "metrics": {}}],
            },
        }
    )
    assert gate["status"] == "pass"

    blocked = generate_sprint_fact_sheet.ai_usage_matrix_gate(
        {
            "fresh_gate": {"status": "blocker", "blockers": ["snapshot-stale"]},
            "snapshot_status": "present",
            "ai_usage_mode": "actual",
            "usage_matrices": {
                "columns": [{"label": "Opsx-Apply", "status": "observed"}],
                "rows": [{"object_id": "Total", "metrics": {}}],
            },
        }
    )
    assert blocked["status"] == "blocker"
    assert "snapshot-stale" in blocked["blockers"]


def test_ai_usage_markdown_blocks_fallback_matrix_and_keeps_recommended_action() -> None:
    generate_sprint_fact_sheet = load_module()
    section = generate_sprint_fact_sheet.render_ai_usage_retrospective_section(
        {
            "sprint": {"sprint_id": "sprint-002"},
            "ai_usage_freshness_baseline": {"min_generated_at": "2026-08-31T01:00:00Z", "source": "sprint.md:updated_at"},
            "ai_usage_snapshot": {
                "path": "data/ai-usage/sprints/sprint-002.json",
                "snapshot_status": "present",
                "ai_usage_mode": "estimated_fallback",
                "fresh_gate": {"status": "blocker", "blockers": ["usage-mode-estimated_fallback"]},
                "generated_at": "2026-08-31T01:01:00Z",
                "totals": {"command_run_count": 1, "total_tokens": 12, "input_tokens": 7, "output_tokens": 5},
                "usage_matrices": {
                    "columns": [{"label": "Opsx-Apply", "status": "observed"}],
                    "rows": [{"object_id": "Total", "metrics": {"total_tokens": {"Opsx-Apply": 12}}}],
                },
                "recommended_action": (
                    "Run `python scripts/extract-ai-usage.py --session-jsonl <local-session.jsonl> "
                    "--manual-map <manual-map.json> --sprint <sprint-id> --json`, then rerun summary."
                ),
            },
        }
    )

    assert "Matrix write gate | blocker" in section
    assert "--manual-map <manual-map.json>" in section
    assert "### total_tokens 矩阵" not in section
    assert "刷新后重新运行 `--summary`" in section
