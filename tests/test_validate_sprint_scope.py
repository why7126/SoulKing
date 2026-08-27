from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import SimpleNamespace


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "validate-sprint-scope.py"


def load_module():
    spec = importlib.util.spec_from_file_location("validate_sprint_scope", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_validate_sprint_scope_requires_target_list_and_six_column_scope(tmp_path: Path, monkeypatch) -> None:
    module = load_module()
    sprint_path = tmp_path / "iterations" / "change" / "sprint-001"
    sprint_path.mkdir(parents=True)
    (sprint_path / "sprint.yaml").write_text(
        "scope_estimates:\n"
        "  - id: update-governance\n"
        "    change: update-governance\n",
        encoding="utf-8",
    )
    (sprint_path / "sprint.md").write_text(
        "# sprint-001\n\n"
        "## 1. 目标\n\n"
        "Sprint 目标编号列表：\n"
        "- update-governance\n\n"
        "## 2. Scope\n\n"
        "| 类型 | 编号 | 标题 | 状态 | 估算 | 说明 |\n"
        "|---|---|---|---|---:|---|\n"
        "| Change | update-governance | 治理更新 | planned | 1 | - |\n"
        "<!-- workflow-sync:scope-changes:start -->\n"
        "update-governance\n"
        "<!-- workflow-sync:scope-changes:end -->\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        module,
        "load_sprint",
        lambda _sprint_id: SimpleNamespace(
            path=sprint_path,
            requirements=[],
            bugs=[],
            changes=["update-governance"],
        ),
    )

    assert module.validate_sprint_scope("sprint-001", set()) == []

    (sprint_path / "sprint.md").write_text(
        "# sprint-001\n\n"
        "## 1. 目标\n\n"
        "目标摘要。\n\n"
        "## 2. Scope\n\n"
        "| 范围项 | 状态 | 估算 |\n"
        "|---|---|---:|\n"
        "| update-governance | planned | 1 |\n"
        "<!-- workflow-sync:scope-changes:start -->\n"
        "update-governance\n"
        "<!-- workflow-sync:scope-changes:end -->\n",
        encoding="utf-8",
    )
    failures = module.validate_sprint_scope("sprint-001", set())
    assert any("Sprint target id list missing or malformed" in failure for failure in failures)
    assert any("main table header must be" in failure for failure in failures)


def test_extract_target_id_list_accepts_short_issue_aliases() -> None:
    module = load_module()
    target_ids = module.extract_target_id_list(
        "## 1. 目标\n\n"
        "正式目标：\n"
        "- `REQ-0123-upload-stage-trace-spans`：补齐 trace spans。\n"
    )
    assert target_ids == {"REQ-0123-upload-stage-trace-spans", "REQ-0123"}
